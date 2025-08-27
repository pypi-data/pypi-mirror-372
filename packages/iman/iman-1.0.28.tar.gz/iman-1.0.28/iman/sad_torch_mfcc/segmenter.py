#!/usr/bin/env python
# encoding: utf-8

# The MIT License

# Copyright (c) 2018 Ina (David Doukhan - http://www.ina.fr/)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

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
from .export_funcs import seg2csv, seg2textgrid



def _energy_activity(loge, ratio=0.4):   ##########0.9

    threshold = np.mean(loge[np.isfinite(loge)]) + np.log(ratio)
    raw_activity = (loge > threshold)
    return viterbi_decoding(pred2logemission(raw_activity),
                            log_trans_exp(150, cost0=-5))

#exp(150, cost0=-5)


def filter_sig1(isig , wav , sr):
    try:
      w=[]
      for i , [_,a,b,_] in enumerate(isig): 
          w.append(wav[int(a*sr) : int(b*sr)])
      return (np.concatenate(w)) 
    except:
      w=[]
      for i , [_,a,b,_,_] in enumerate(isig): 
          w.append(wav[int(a*sr) : int(b*sr)])
      return (np.concatenate(w)) 
      

def filter_sig(isig , wav , sr):
    try:
      w=[]
      wn=[]
      wn.append(wav[0 : int(isig[0][1]*sr)])
      for i , [_,a,b,_] in enumerate(isig): 
          
          w.append(wav[int(a*sr) : int(b*sr)])
          try:
            wn.append(wav[ int(isig[i][2]*sr) :  int(isig[i+1][1]*sr)])
          except:
            wn.append(wav[int(isig[i][2]*sr) : len(wav)])          
          
      return (np.concatenate(w),np.concatenate(wn)) 
    except:
      w=[]
      wn=[]
      wn.append(wav[0 : int(isig[0][1]*sr)])
      for i , [_,a,b,_,_] in enumerate(isig): 
          w.append(wav[int(a*sr) : int(b*sr)])
          try:
            wn.append(wav[ int(isig[i][2]*sr) :  int(isig[i+1][1]*sr)])
          except:
            wn.append(wav[int(isig[i][2]*sr) : len(wav)])          
          
      return (np.concatenate(w),np.concatenate(wn)) 
            
def filter_output(isig , max_silence=1 ,ignore_small_speech_segments=0.5 , max_speech_len=15,split_speech_bigger_than=20):

   if (len(isig)==0):
     return -1
     
   # _dels=[]
   # for i , [_,_,_,_d] in enumerate(isig):  
        # if (_d<=ignore_small_speech_segments) :
                 # _dels.append(i)
   # _dels.reverse()
   # for i in _dels:
       # del isig[i]
   
   # if (len(isig)==0):
     # return -1
      
  
   for i in range(len(isig)-1):
      t = isig[i+1][1] - isig[i][2] # silence between towo chunk
      isig[i].append(t)
   isig[-1].append(-1) 
   
   
   if (len(isig)>0):
          
          rang = np.arange(0.01,max_silence+0.1,0.1)
          for di in rang:
             for i , [_,_,_,_,_t] in enumerate(isig):
                        if (_t==-1):
                            break                 
                        if (_t <=di):  
                           try:                         
                            if (isig[i+1][2] -   isig[i][1] <= max_speech_len):
                              isig[i] =  [isig[i][0] , isig[i][1] , isig[i+1][2] ,  isig[i+1][2] -   isig[i][1] , isig[i+1][4] ] 
                              del isig[i+1]
                           except:
                               pass                           
          _dels=[]                    
          for i , [_,_,_,_d,_] in enumerate(isig):  
               if (_d<=ignore_small_speech_segments) :
                        _dels.append(i)
          _dels.reverse()
          
          for i in _dels:
              del isig[i]
              
          if (len(isig)==0):
            return -1
     
        
   isign=[]                 
   for i , [_,_,_,_d,_] in enumerate(isig):  
        if (_d> split_speech_bigger_than ) :
               
               _gc = math.ceil(_d/split_speech_bigger_than)
               m = _d/_gc 
               print('Bigger-->' + str(_d) + '-->' + str(m))
               for jj in range(_gc):
                    fas=0
                    if (jj== _gc-1):
                        fas= isig[i][4]
                    isign.append(  [isig[i][0] ,isig[i][1] + m*jj ,isig[i][1] + (m*(jj+1)), m, fas ]    )
        else:
               isign.append(isig[i]) 
   for i,(a,b,c,d,e) in enumerate(isign):
      if (e==-1):
          break 
      # _addlen = min(e , 1) / 2      #حداکثر نیم ثانیه به انتهای سگمنت افزوده میشود
      _addlen = 0
      isign[i] = [a,b,c+_addlen,d+_addlen,e-_addlen]
    
   return(isign) 
  

def filter_fea(isig , mfccs , sr=8000 , max_time=120):   #max_time in second

   if (len(isig)==0):
     return []
     
   
   filter_mfcc_smaller_than = 30 # smaller 30 frame ==   300msec 
     
   hop = int((10 / 1000) * sr) # hope len = 10 ms
   
   max_frame = int(max_time * sr / hop)
   
   x = 0
   nmfccs = []   
   for si in isig:
   
      t0 = int(si[1] * sr / hop)
      t1 = int(si[2] * sr / hop)
      
      if (t1-t0 <= filter_mfcc_smaller_than ):
            continue
      
      nmfccs.append( mfccs[t0:t1])
      x = x + (t1-t0)
      if (x>max_frame):
          break
   
   if (len(nmfccs) == 0):
        return []   
        
   return (torch.cat(nmfccs)[0:max_frame,:])   
    
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
        xx.load_state_dict(torch.load(model_path,map_location=torch.device(device)))  
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


class SpeechMusic(DnnSegmenter):
    # Voice activity detection: requires energetic activity detection
    outlabels = ('speech', 'music')
    inlabel = 'energy'
    nmel = 21
    viterbi_arg = 150


class SpeechMusicNoise(DnnSegmenter):
    # Voice activity detection: requires energetic activity detection
    outlabels = ('speech', 'noise', 'music')
    inlabel = 'energy'
    nmel = 21
    viterbi_arg = 80

    
class Gender(DnnSegmenter):
    # Gender Segmentation, requires voice activity detection
    outlabels = ('female', 'male')
    inlabel = 'speech'
    nmel = 24
    viterbi_arg = 80



class Segmenter:


    def __init__(self, vad_type = 'sad' , vad_engine='smn', detect_gender=False, sr=8000, batch_size=32 , complete_output=False,model_path=r"C:\sad_model_pytorch.pth" , max_time=120 , tq=1,ffmpeg_path='c:\\ffmpeg.exe', device='cuda',input_type="file"):
        """
        Load neural network models
        
        Input:

        'vad_engine' can be 'sm' (speech/music) or 'smn' (speech/music/noise)
                'sm' was used in the results presented in ICASSP 2017 paper
                        and in MIREX 2018 challenge submission
                'smn' has been implemented more recently and has not been evaluated in papers
        
        'detect_gender': if False, speech excerpts are return labelled as 'speech'
                if True, speech excerpts are splitted into 'male' and 'female' segments
        """      
        self.sample_rate = sr
        self.device = device
        self.complete_output = complete_output
        self.max_time = max_time #sec
        self.tq=tq
        self.input_type = input_type
        self.ffmpeg_path=ffmpeg_path
        


#        self.graph = KB.get_session().graph # To prevent the issue of keras with tensorflow backend for async tasks

        
        # select speech/music or speech/music/noise voice activity detection engine
        assert vad_engine in ['sm', 'smn']
        if vad_engine == 'sm':
            self.vad = SpeechMusic(batch_size)
        elif vad_engine == 'smn':
            self.vad = SpeechMusicNoise(batch_size , vad_type,model_path,tq , device)

        # load gender detection NN if required
        assert detect_gender in [True, False]
        self.detect_gender = detect_gender
        if detect_gender:
            self.gender = Gender(batch_size)
        self.vad_type = vad_type
        self.model_path = model_path

    def segment_feats(self, mspec, loge, start_sec):
        """
        do segmentation
        require input corresponding to wav file sampled at 16000Hz
        with a single channel
        """




        # perform energy-based activity detection
        lseg = []
        vadseg=[]
        for lab, start, stop in _binidx2seglist(_energy_activity(loge)[::2]):
            if lab == 0:
                lab = 'noEnergy'
            else:
                lab = 'energy'
                vadseg.append(('speech', start, stop))
            lseg.append((lab, start, stop))
        if (self.vad_type == 'vad'):
           return [(lab, start_sec + start * .02, start_sec + stop * .02 , stop-start) for lab, start, stop in vadseg]
        # perform voice activity detection
        lseg = self.vad(mspec, lseg)

        # perform gender segmentation on speech segments
        if self.detect_gender:
            lseg = self.gender(mspec, lseg)
        if (self.complete_output):
           return   [(lab, start_sec + start * .02, start_sec + stop * .02 , (stop-start) * .02) for lab, start, stop in lseg ]
        else:
           return   [[lab, start_sec + start * .02, start_sec + stop * .02 , (stop-start) * .02] for lab, start, stop in lseg if (lab=='speech')]   


    def __call__(self, medianame, start_sec=None, stop_sec=None):

        
        mspec, loge , me = media2feats(medianame, self.input_type,self.sample_rate,ffmpeg_path=self.ffmpeg_path)
        
        if (mspec==[]):
           return [],me,[]
        
        
        if start_sec is None:
            start_sec = 0
        # do segmentation  
        
        isii = self.segment_feats(mspec, loge, start_sec)

        # nmfcc = filter_fea(isii , mspec.squeeze(),self.sample_rate , self.max_time)
        nmfcc = mspec.squeeze()
        
        return isii,me ,nmfcc

    
    def batch_process(self, linput, loutput, verbose=False, skipifexist=False, nbtry=1, trydelay=2., output_format='csv'):
        
        if verbose:
            print('batch_processing %d files' % len(linput))

        if output_format == 'csv':
            fexport = seg2csv
        elif output_format == 'textgrid':
            fexport = seg2textgrid
        else:
            raise NotImplementedError()
            
        t_batch_start = time.time()
        
        lmsg = []
        fg = featGenerator(linput.copy(), loutput.copy(), skipifexist, nbtry, trydelay , self.sample_rate)
        i = 0
        for feats, msg in fg:
            lmsg += msg
            i += len(msg)
            if verbose:
                print('%d/%d' % (i, len(linput)), msg)
            if feats is None:
                break
            mspec, loge = feats
            #if verbose == True:
            #    print(i, linput[i], loutput[i])
            b = time.time()
            lseg = self.segment_feats(mspec, loge, 0)
            fexport(lseg, loutput[len(lmsg) -1])
            lmsg[-1] = (lmsg[-1][0], lmsg[-1][1], 'ok ' + str(time.time() -b))

        t_batch_dur = time.time() - t_batch_start
        nb_processed = len([e for e in lmsg if e[1] == 0])
        if nb_processed > 0:
            avg = t_batch_dur / nb_processed
        else:
            avg = -1
        return t_batch_dur, nb_processed, avg, lmsg


def medialist2feats(lin, lout, skipifexist, nbtry, trydelay,sampling_rete=8000):
    """
    To be used when processing batches
    if resulting file exists, it is skipped
    in case of remote files, access is tried nbtry times
    """
    ret = None
    msg = []
    while ret is None and len(lin) > 0:
        src = lin.pop(0)
        dst = lout.pop(0)
#        print('popping', src)
        
        # if file exists: skipp
        if skipifexist and os.path.exists(dst):
            msg.append((dst, 1, 'already exists'))
            continue

        # create storing directory if required
        dname = os.path.dirname(dst)
        if not os.path.isdir(dname):
            os.makedirs(dname)
        
        itry = 0
        while ret is None and itry < nbtry:
            try:
                ret = media2feats(src, sampling_rete)
            except:
                itry += 1
                errmsg = sys.exc_info()[0]
                if itry != nbtry:
                    time.sleep(random.random() * trydelay)
        if ret is None:
            msg.append((dst, 2, 'error: ' + str(errmsg)))
        else:
            msg.append((dst, 0, 'ok'))
            
    return ret, msg

    
def featGenerator(ilist, olist, skipifexist=False, nbtry=1, trydelay=2. , sampling_rate=8000):
#    print('init feat gen', len(ilist))
    thread = ThreadReturning(target = medialist2feats, args=[ilist, olist, skipifexist, nbtry, trydelay,sampling_rate])
    thread.start()
    while True:
        ret, msg = thread.join()
#        print('join done', len(ilist))
#        print('new list', ilist)
        #ilist = ilist[len(msg):]
        #olist = olist[len(msg):]
        if len(ilist) == 0:
            break
        thread = ThreadReturning(target = medialist2feats, args=[ilist, olist,skipifexist, nbtry, trydelay,sampling_rate])
        thread.start()
        yield ret, msg
    yield ret, msg
