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

import os
import numpy as np
from iman import Audio
from iman import Features
import torch



#os.environ['SIDEKIT'] = 'theano=false,libsvm=false,cuda=false'
#from sidekit.frontend.io import read_wav
#from sidekit.frontend.features import mfcc


def _wav2feats(wavname,input_type='file',sr=16000,ffmpeg_path='c:\\ffmpeg.exe'):
    if (input_type == 'file'):
      sig1 = Audio.Read(wavname ,sr=sr,mono=True , ffmpeg_path=ffmpeg_path)     
    else:
      sig1 = wavname
      
    sig=sig1+1e-7
    sig = torch.unsqueeze( torch.from_numpy(sig) , dim=0)   
    try:    
      mfccs, mspec,loge  = Features.SB.Get(sig , sr , n_mels=40 , n_mfcc=24 , n_fft=200)   
    except:
      print('error in feature extraction')
      print('upgrade your pytorch')
      return [] ,[],sig1   
    if (len(loge)<68):   
           return [] , [] , sig1
    return  mfccs , loge ,sig1    
  

def media2feats(medianame,input_type='file', sr=16000,ffmpeg_path='c:\\ffmpeg.exe'):
  
        return _wav2feats(medianame,input_type,sr,ffmpeg_path=ffmpeg_path)
