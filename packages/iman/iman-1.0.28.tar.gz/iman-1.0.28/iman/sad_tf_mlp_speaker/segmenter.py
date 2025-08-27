
import warnings
warnings.filterwarnings("ignore")
import os
# os.environ["CUDA_DEVICE_ORDER"]= '0'
import sys
import math
import numpy as np
from .thread_returning import ThreadReturning

import shutil
import time
import random
from tqdm import tqdm
from tensorflow import keras
from tensorflow.compat.v1.keras.backend import set_session

from skimage.util import view_as_windows as vaw
from .viterbi import viterbi_decoding
from .viterbi_utils import pred2logemission, diag_trans_exp, log_trans_exp

from .features import media2feats


def getnew(aa, _len):
    
   
    while(len(aa)<_len):
        
      di = _len - len(aa)
      
      a2 = aa[0:di]
      
      aa = np.vstack((aa , a2))
      
    return aa


def _energy_activity(loge, ratio=0.4):   ##########0.9

    threshold = np.mean(loge[np.isfinite(loge)]) + np.log(ratio)
    raw_activity = (loge > threshold)
    return viterbi_decoding(pred2logemission(raw_activity),
                            log_trans_exp(150, cost0=-5))

   
def _get_patches(mspec, w, step):
    h = mspec.shape[1]
    data = vaw(mspec, (w,h), step=step)
    data.shape = (len(data), w*h)
    data = (data - np.mean(data, axis=1).reshape((len(data), 1))) / np.std(data, axis=1).reshape((len(data), 1))
    lfill = [data[0,:].reshape(1, h*w)] * (w // (2 * step))
    rfill = [data[-1,:].reshape(1, h*w)] * (w // (2* step) - 1 + len(mspec) % 2)
    data = np.vstack(lfill + [data] + rfill )
    finite = np.all(np.isfinite(data), axis=1)
    data.shape = (len(data), w, h)
    return data, finite    


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
        self.nn = keras.models.load_model(model_path, compile=False)   
        print('model Loded from--> ' + model_path)  
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

        mspec =mspec[:,0:21].copy()
        
        patches ,_= _get_patches(mspec, 68, 2)

        batch = []
        for lab, start, stop in lseg:
            if lab == self.inlabel:
                batch.append(patches[start:stop, :])
        

        if len(batch) > 0:
            batch = np.concatenate(batch)
            rawpred = self.nn.predict(batch, batch_size=self.batch_size, verbose=self.tq)
          
        
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

   


class Segmenter:


    def __init__(self, vad_type = 'sad', sr=8000, batch_size=32 ,model_path=r"C:\sad_tf_mlp.hdf5" , max_time=120 ,tq=1,ffmpeg_path='c:\\ffmpeg.exe', device='cuda' , pad=False):
     
     
        if (device != 'cuda'):
              os.environ["CUDA_DEVICE_ORDER"]= '-1'  
        else:
           pass       


        import tensorflow as tf
        
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True 
        config.log_device_placement = True 
        sess = tf.compat.v1.Session(config=config)
        set_session(sess)    
     
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
                  p = just_filter(isii , np.squeeze(mspec) , sr = self.sample_rate )
                  if (p!=[]):
                    last_mfcc.append(p)
                    total_len = total_len + (p.shape[0])
                  return np.concatenate(last_mfcc)[0:max_frame,:] , self.max_time
              else:
                  p=just_filter(isii ,np.squeeze(mspec),sr=self.sample_rate)
                  if (p!=[]):
                    last_mfcc.append(p)
                    total_len = total_len + (p.shape[0])
                  startfrom = startfrom +  need_speech
                

        if (len(last_mfcc)==0):
           return []
        
        if total_len >=max_frame:
           return np.concatenate(last_mfcc)[0:max_frame,:] , self.max_time
        else:
          if (self.pad):
             return getnew(np.concatenate(last_mfcc) , max_frame) , (total_len*hop)/self.sample_rate
          else:
              return np.concatenate(last_mfcc)  , (total_len*hop)/self.sample_rate         

    

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
        
   return (np.concatenate(nmfccs))   