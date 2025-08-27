
import warnings
warnings.filterwarnings("ignore")
import os
# os.environ["CUDA_DEVICE_ORDER"]= '0'
import sys
import math
from .sad_model import SAD_INA_MODEL
import numpy as np
import torch
seed = 0
torch.manual_seed(seed)
from .thread_returning import ThreadReturning

import shutil
import time
import random
from tqdm import tqdm


from .viterbi import viterbi_decoding
from .viterbi_utils import pred2logemission, diag_trans_exp, log_trans_exp

from .features import media2feats




def _energy_activity(loge, ratio=0.4):   ##########0.9

    threshold = np.mean(loge[np.isfinite(loge)]) + np.log(ratio)
    raw_activity = (loge > threshold)
    return viterbi_decoding(pred2logemission(raw_activity),
                            log_trans_exp(150, cost0=-5))

#exp(150, cost0=-5)


def MVN(x):
   current_mean = torch.mean(x, dim=0).detach()
   current_std = torch.std(x, dim=0).detach()
   x= (x - current_mean) / current_std
   return (x) 
   
def vaw_torch(arr_in , window_shape , step):
      ndim = len(arr_in.size())
      steps = (step,) * ndim      
      arr_shape = np.array(arr_in.size())    
      window_shape = np.array(window_shape, dtype=arr_shape.dtype)
      slices = tuple(slice(None, None, st) for st in steps)         
      window_strides = np.array((arr_in.stride()))    
      indexing_strides = arr_in[slices].stride()      
      win_indices_shape = (((np.array(arr_in.size()) - np.array(window_shape))// np.array(steps)) + 1)    
      new_shape = tuple(list(win_indices_shape) + list(window_shape))      
      strides = tuple(list(indexing_strides) + list(window_strides))      
      arr_out = torch.as_strided(arr_in, new_shape, strides)
      return arr_out
   
    
def _get_patches(mspec, w, step):
      h = mspec.size(1)
      arr_out = vaw_torch(mspec, (w,h), step=step)
      arr_out = arr_out.view (arr_out.size(0), w*h) 
      arr_out =( arr_out-  torch.mean(arr_out, axis=1).view((len(arr_out), 1))) /(torch.std(arr_out,axis=1).view(arr_out.size(0),-1) + 1e-10)
      lfill = [arr_out[0,:].view(1, h*w)] * (w // (2 * step))
      rfill = [arr_out[-1,:].view(1, h*w)] * (w // (2* step) - 1 + mspec.size(0) % 2)
      arr_out=torch.vstack(lfill + [arr_out] + rfill )
      arr_out=arr_out.view(arr_out.size(0),w,h  )
      return arr_out


def _binidx2seglist(binidx):
    """
    ss._binidx2seglist((['f'] * 5) + (['bbb'] * 10) + ['v'] * 5)
    Out: [('f', 0, 5), ('bbb', 5, 15), ('v', 15, 20)]
    
    #TODO: is there a pandas alternative??
    """
    curlabel = None
    bseg = -1
    ret = []
    for i, e in enumerate(binidx):
        if e != curlabel:
            if curlabel is not None:
                ret.append((curlabel, bseg, i))
            curlabel = e
            bseg = i
    ret.append((curlabel, bseg, i + 1))
    return ret


class DnnSegmenter:
    """
    DnnSegmenter is an abstract class allowing to perform Dnn-based
    segmentation using Keras serialized models using 24 mel spectrogram
    features obtained with SIDEKIT framework.

    Child classes MUST define the following class attributes:
    * nmel: the number of mel bands to used (max: 24)
    * viterbi_arg: the argument to be used with viterbi post-processing
    * model_fname: the filename of the serialized keras model to be used
        the model should be stored in the current directory
    * inlabel: only segments with label name inlabel will be analyzed.
        other labels will stay unchanged
    * outlabels: the labels associated the output of neural network models
    """
    def __init__(self, batch_size, vad_type , model_path,tq, device):
        # load the DNN model
      if (vad_type!='vad'):
        xx = SAD_INA_MODEL()   

        
        sample_input = [torch.rand(16,68,21)]
        
        xx.load_state_dict(torch.load(model_path , map_location=torch.device(device)))  
        
        xx.eval()
        
        if (device!="cuda"):
          xx = torch.jit.trace(xx, sample_input)

          xx = torch.jit.freeze(xx)

        print('model Loded from--> ' + model_path)
        self.nn=xx.to(device)
        self.nn.eval()    
        # self.nn.summary()
        self.batch_size = batch_size
        self.tq= tq
        self.device= device
        
    def __call__(self, mspec, lseg):
        """
        *** input
        * mspec: mel spectrogram
        * lseg: list of tuples (label, start, stop) corresponding to previous segmentations
        * difflen: 0 if the original length of the mel spectrogram is >= 68
                otherwise it is set to 68 - length(mspec)
        *** output
        a list of adjacent tuples (label, start, stop)
        """

        mspec = torch.squeeze(mspec)
        
        mspec =mspec[:,0:21].clone()
        
        patches = _get_patches(mspec, 68, 2)

        batch = []
        for lab, start, stop in lseg:
            if lab == self.inlabel:
                batch.append(patches[start:stop, :])
        
        with torch.no_grad():
         bsize=self.batch_size
         if len(batch) > 0:
            batch = torch.cat(batch,0).to(self.device)
            fsize = len(batch)
            num = (fsize//bsize)+1
            x=[]
            with torch.inference_mode():
              if (self.tq == 1):
               for i in tqdm(range(num)):
                 inp =  batch[i*bsize:(i+1)*bsize,:,:]
                 if (len(inp)>0):
                    rawpred = self.nn(inp)
                    x.append(rawpred)
               rawpred = torch.concat(x)
              else:
               for i in range(num):
                 inp =  batch[i*bsize:(i+1)*bsize,:,:]
                 if (len(inp)>0):
                    rawpred = self.nn(inp)
                    x.append(rawpred)
               rawpred = torch.concat(x)              

            rawpred=rawpred.cpu().detach().numpy()
        
        ret = []
        for lab, start, stop in lseg:
            if lab != self.inlabel:
                ret.append((lab, start, stop))
                continue

            l = stop - start
            r = rawpred[:l] 
            rawpred = rawpred[l:]
           # r[finite[start:stop] == False, :] = 0.5
            pred = viterbi_decoding(np.log(r), diag_trans_exp(self.viterbi_arg, len(self.outlabels)))
            for lab2, start2, stop2 in _binidx2seglist(pred):
                ret.append((self.outlabels[int(lab2)], start2+start, stop2+start))            
        return  ret





class SpeechMusicNoise(DnnSegmenter):
    # Voice activity detection: requires energetic activity detection
    outlabels = ('speech', 'noise', 'music')
    inlabel = 'energy'
    nmel = 21
    viterbi_arg = 80

    

def getnew(ar, _len):
    
    aa = ar.numpy()
    while(len(aa)<_len):
        
      di = _len - len(aa)
      
      a2 = ar[0:di]
      
      aa = np.vstack((aa , a2))
      
    return torch.tensor(aa)



class Segmenter:


    def __init__(self, vad_type = 'sad', sr=8000, batch_size=32 ,model_path=r"C:\sad_model_pytorch.pth" , max_time=120 ,tq=1,ffmpeg_path='c:\\ffmpeg.exe', device='cuda' , pad=False):
     
        self.sample_rate = sr
        self.device = device
       
        self.max_time = max_time #sec
        self.tq=tq
        self.ffmpeg_path=ffmpeg_path
        self.pad=pad
        


        self.vad = SpeechMusicNoise(batch_size , vad_type,model_path,tq , device)

      
        self.vad_type = vad_type
        self.model_path = model_path

    def segment_feats(self, mspec, loge, start_sec):
        """
        do segmentation
        require input corresponding to wav file sampled at 16000Hz
        with a single channel
        """

        speech_len=0


        # perform energy-based activity detection
        lseg = []
        vadseg=[]
        for lab, start, stop in _binidx2seglist(_energy_activity(loge)[::2]):
            if lab == 0:
                lab = 'noEnergy'
            else:
                lab = 'energy'
                speech_len = speech_len + stop  - start
                vadseg.append(('speech', start, stop))
            lseg.append((lab, start, stop))
        if (self.vad_type == 'vad'):
           return  speech_len*0.02 , [(lab, start_sec + start * .02, start_sec + stop * .02 , stop-start) for lab, start, stop in vadseg]
        # perform voice activity detection
        lseg = self.vad(mspec, lseg)
        speech_len=0
        for lab, start, stop in lseg :
           if (lab=='speech'):
               speech_len = speech_len+ stop - start
        
        # perform gender segmentation on speech segments
      
     
        return   speech_len*0.02 , [[lab, start_sec + start * .02, start_sec + stop * .02 , (stop-start) * .02] for lab, start, stop in lseg if (lab=='speech')]   


    def __call__(self, medianame, start_sec=None, stop_sec=None):
        
        
        hop = int((10 / 1000) * self.sample_rate) # hope len = 10 ms
        
        max_frame = int(self.max_time * self.sample_rate / hop)
             
        need_speech = 2*self.max_time
        startfrom=0
        
        last_mfcc=[]
        last_isig=[]
        spee =0
        total_len=0
        while(True):
             
              mspec,loge = media2feats(medianame,self.sample_rate, startfrom , need_speech, ffmpeg_path=self.ffmpeg_path)
              
              if (mspec==[]):
                 break

              if start_sec is None:
                  start_sec = 0
              
              speech_len , isii = self.segment_feats(mspec, loge, start_sec)
             
              spee = spee + speech_len
              
              if (spee >=  self.max_time):
                  p = just_filter(isii , mspec.squeeze() , sr = self.sample_rate )
                  if (p!=[]):
                    last_mfcc.append(p)
                    total_len = total_len + (p.size()[0])
                  return torch.cat(last_mfcc)[0:max_frame,:] , self.max_time
              else:
                  p=just_filter(isii , mspec.squeeze(),sr=self.sample_rate)
                  if (p!=[]):
                    last_mfcc.append(p)
                    total_len = total_len + (p.size()[0])
                  startfrom = startfrom +  need_speech
                

        if (len(last_mfcc)==0):
           return []
        
        if total_len >=max_frame:
           return torch.cat(last_mfcc)[0:max_frame,:] , self.max_time
        else:
          if (self.pad):
             return getnew(torch.cat(last_mfcc) , max_frame) , (total_len*hop)/self.sample_rate
          else:
              return torch.cat(last_mfcc)  , (total_len*hop)/self.sample_rate         

    

def just_filter(isig , mfccs , sr=8000):   #max_time in second

   if (len(isig)==0):
     return []   
   
   # filter_mfcc_smaller_than = 10 # smaller 10 frame ==  100msec 
     
   hop = int((10 / 1000) * sr) # hope len = 10 ms
   
   nmfccs = []   
   for si in isig:
   
      t0 = int(si[1] * sr / hop)
      t1 = int(si[2] * sr / hop)
      
      # if (t1-t0 <= filter_mfcc_smaller_than ):
            # continue
      
      nmfccs.append( mfccs[t0:t1])
    
   
   if (len(nmfccs) == 0):
        return []   
        
   return (torch.cat(nmfccs))   