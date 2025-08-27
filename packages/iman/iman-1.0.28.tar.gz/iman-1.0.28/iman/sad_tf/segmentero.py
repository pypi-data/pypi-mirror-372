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
import onnxruntime
import warnings
warnings.filterwarnings("ignore")
import os
# os.environ["CUDA_DEVICE_ORDER"]= '0'
import sys
import math
from iman import Audio
import numpy as np
from tensorflow import keras
from tensorflow.compat.v1.keras.backend import set_session
from tqdm import tqdm
from .thread_returning import ThreadReturning

import shutil
import time
import random

from skimage.util import view_as_windows as vaw


from .viterbi import viterbi_decoding
from .viterbi_utils import pred2logemission, diag_trans_exp, log_trans_exp

from .features import media2feats
from .export_funcs import seg2csv, seg2textgrid



def _energy_activity(loge, ratio=0.4):   ##########0.9

    threshold = np.mean(loge[np.isfinite(loge)]) + np.log(ratio)
    raw_activity = (loge > threshold)
    return viterbi_decoding(pred2logemission(raw_activity),
                            log_trans_exp(50, cost0=-5))

#exp(150, cost0=-5)

def filter_sig(isig , wav , sr=16000):
    
    if (sr!=16000):
       wav = Audio.Resample(wav , 16000, sr)
    
    
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
      _addlen = min(e , 1) / 2      #حداکثر نیم ثانیه به انتهای سگمنت افزوده میشود
      isign[i] = [a,b,c+_addlen,d+_addlen,e-_addlen]
    
   return(isign) 
   
   
def filter_output_1(vad , max_silence=1 ,ignore_small_speech_segments=0.5 , max_speech_len=15,split_speech_bigger_than=20):
     
  isig = []
  i=0
  while (i <len(vad)):
      
     ml=0 
     inn = i
     st = (vad[i][1]) 
     
     while ( (i<len(vad)-1 )and ( (  (vad[i+1][1]) - (vad[i][2]) ) <= max_silence)):    
         ml = (vad[i][2]) - st
         if (ml > max_speech_len):
             if (i>inn and i>0):
                 i=i-1
             break
         i=i+1
     en = (vad[i][2])
     fa = en-st
     if (fa > ignore_small_speech_segments):
       if (fa>split_speech_bigger_than):
          _gc = math.ceil(fa/split_speech_bigger_than)
          m = fa/_gc
          print('Bigger-->' + str(fa) + '-->' + str(m))
          for jj in range(_gc):
            isig.append(('speech' , st + (m*jj) , st+ (m*(jj+1)) , m))
       else:
          isig.append(('speech', st , en,fa))
     i=i+1
  isign=[]
  for i,(a,b,c,d) in enumerate(isig):
    if (i == len(isig)-1):
        isign.append(isig[i]) 
        break
    _addlen = min(isig[i+1][1]-c , 1) / 2      #حداکثر نیم ثانیه به انتهای سگمنت افزوده میشود
    isign.append([a,b,c+_addlen ,d+_addlen])
   
  return(isign)  


def get_path_3d(data,batch_size):
    total_batches = data.shape[0] // batch_size
    last_batch_size = data.shape[0] % batch_size
    if last_batch_size != 0:
      batches = np.split(data[:total_batches * batch_size], total_batches)
      last_batch = np.expand_dims(data[total_batches * batch_size:], axis=0).squeeze()
      batches.append(last_batch)
    else:
      batches = np.split(data, total_batches)
    return  batches 

            
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
    def __init__(self, batch_size, vad_type,model_path,EP_list):
        # load the DNN model
      if (vad_type!='vad'):
        self.session = onnxruntime.InferenceSession(model_path,providers=EP_list)
        #self.nn = keras.models.load_model(model_path, compile=False)
        print('model Loded from--> ' + model_path)        
        # self.nn.summary()
        self.batch_size = batch_size
        
    def __call__(self, mspec, lseg, difflen = 0):
        """
        *** input
        * mspec: mel spectrogram
        * lseg: list of tuples (label, start, stop) corresponding to previous segmentations
        * difflen: 0 if the original length of the mel spectrogram is >= 68
                otherwise it is set to 68 - length(mspec)
        *** output
        a list of adjacent tuples (label, start, stop)
        """
        if self.nmel < 24:
            mspec = mspec[:, :self.nmel].copy()
        
        patches, finite = _get_patches(mspec, 68, 2)
        if difflen > 0:
            patches = patches[:-int(difflen / 2), :, :]
            finite = finite[:-int(difflen / 2)]
            
        assert len(finite) == len(patches), (len(patches), len(finite))
            
        batch = []
        for lab, start, stop in lseg:
            if lab == self.inlabel:
                batch.append(patches[start:stop, :])

        if len(batch) > 0:
           
            batch = np.concatenate(batch)
            batches = get_path_3d(batch , self.batch_size,)
            
            
            #rawpred = self.nn.predict(batch, batch_size=self.batch_size, verbose=1)
            input_name = self.session.get_inputs()[0].name
            rawpred=[]
            for batch in tqdm(batches):
                rawpred.append(self.session.run(None, {input_name: batch})[0])
            
            rawpred = np.concatenate(rawpred)
            

        ret = []
        for lab, start, stop in lseg:
            if lab != self.inlabel:
                ret.append((lab, start, stop))
                continue

            l = stop - start
            r = rawpred[:l] 
            rawpred = rawpred[l:]
            r[finite[start:stop] == False, :] = 0.5
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
    outlabels = ('speech', 'music', 'noise')
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


    def __init__(self, vad_type = 'sad' , vad_engine='smn', detect_gender=False, sr=16000, batch_size=32 , complete_output=False,model_path="c:\\keras_speech_music_noise_cnn.onnx",gender_path="c:\\keras_male_female_cnn.onnx" , ffmpeg_path='c:\\ffmpeg.exe',device='cuda'):
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
        self.complete_output = complete_output
        self.sample_rate = sr
        self.ffmpeg_path=ffmpeg_path
        
        
        if (device != 'cuda'):
              os.environ["CUDA_DEVICE_ORDER"]= '-1'  
              EP_list=[ 'CPUExecutionProvider']
        else:
               EP_list=['CUDAExecutionProvider']
               
        import tensorflow as tf
        
        config = tf.compat.v1.ConfigProto()
        config.gpu_options.allow_growth = True 
        config.log_device_placement = True 
        sess = tf.compat.v1.Session(config=config)
        set_session(sess)    



#        self.graph = KB.get_session().graph # To prevent the issue of keras with tensorflow backend for async tasks

        
        # select speech/music or speech/music/noise voice activity detection engine
        assert vad_engine in ['sm', 'smn']
        if vad_engine == 'sm':
            self.vad = SpeechMusic(batch_size)
        elif vad_engine == 'smn':
            self.vad = SpeechMusicNoise(batch_size , vad_type,model_path,EP_list)

        # load gender detection NN if required
        assert detect_gender in [True, False]
        self.detect_gender = detect_gender
        if detect_gender:
            self.gender = Gender(batch_size , vad_type ,gender_path,EP_list)
        self.vad_type = vad_type
        self.model_path = model_path
        self.gender_path = gender_path

    def segment_feats(self, mspec, loge, difflen, start_sec):
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
        lseg = self.vad(mspec, lseg, difflen)
        
        
        

        # perform gender segmentation on speech segments
        if self.detect_gender:
            lseg = self.gender(mspec, lseg, difflen)
        if (self.complete_output):
           return   [(lab, start_sec + start * .02, start_sec + stop * .02 , (stop-start) * .02) for lab, start, stop in lseg ]
        else:
           return   [[lab, start_sec + start * .02, start_sec + stop * .02 , (stop-start) * .02] for lab, start, stop in lseg if (lab=='male' or lab=="female" or lab=="speech")]   


    def __call__(self, medianame, input_type='file',start_sec=None, stop_sec=None):
        """
        Return segmentation of a given file
                * convert file to wav 16k mono with ffmpeg
                * call NN segmentation procedures
        * media_name: path to the media to be processed (including remote url)
                may include any format supported by ffmpeg
        * tmpdir: allow to define a custom path for storing temporary files
                fast read/write HD are a good choice
        * start_sec (seconds): sound stream before start_sec won't be processed
        * stop_sec (seconds): sound stream after stop_sec won't be processed
        """
        
        
        mspec, loge, difflen , me = media2feats(medianame, input_type ,self.sample_rate,ffmpeg_path=self.ffmpeg_path)
        
        if start_sec is None:
            start_sec = 0
        # do segmentation   
        return self.segment_feats(mspec, loge, difflen, start_sec),me

    
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
        fg = featGenerator(linput.copy(), loutput.copy(), skipifexist, nbtry, trydelay)
        i = 0
        for feats, msg in fg:
            lmsg += msg
            i += len(msg)
            if verbose:
                print('%d/%d' % (i, len(linput)), msg)
            if feats is None:
                break
            mspec, loge, difflen = feats
            #if verbose == True:
            #    print(i, linput[i], loutput[i])
            b = time.time()
            lseg = self.segment_feats(mspec, loge, difflen, 0)
            fexport(lseg, loutput[len(lmsg) -1])
            lmsg[-1] = (lmsg[-1][0], lmsg[-1][1], 'ok ' + str(time.time() -b))

        t_batch_dur = time.time() - t_batch_start
        nb_processed = len([e for e in lmsg if e[1] == 0])
        if nb_processed > 0:
            avg = t_batch_dur / nb_processed
        else:
            avg = -1
        return t_batch_dur, nb_processed, avg, lmsg


def medialist2feats(lin, lout, skipifexist, nbtry, trydelay,sampling_rete=16000):
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
                ret = media2feats(src, tmpdir, None, None, ffmpeg)
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

    
def featGenerator(ilist, olist, skipifexist=False, nbtry=1, trydelay=2., sampling_rate=16000):
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
        thread = ThreadReturning(target = medialist2feats, args=[ilist, olist, skipifexist, nbtry, trydelay,sampling_rate])
        thread.start()
        yield ret, msg
    yield ret, msg
