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

#os.environ['SIDEKIT'] = 'theano=false,libsvm=false,cuda=false'
#from sidekit.frontend.io import read_wav
#from sidekit.frontend.features import mfcc
from .sidekit_mfcc import  mfcc


def _wav2feats(wavname,input_type='file',sr=16000,ffmpeg_path='c:\\ffmpeg.exe'):
    """
    Extract features for wav 16k mono
    """
    
    if (input_type == 'file'):
        sig = Audio.Read(wavname , sr,mono = True, ffmpeg_path=ffmpeg_path)
    else:
        sig =  wavname   
        
    read_framerate=sr


    _, loge, _, mspec = mfcc(sig.astype(np.float32), get_mspec=True,fs=sr, maxfreq=int(sr/2))
        
    # Management of short duration segments
    difflen = 0
    if len(loge) < 68:
        difflen = 68 - len(loge)
        mspec = np.concatenate((mspec, np.ones((difflen, 24)) * np.min(mspec)))

    return mspec, loge, difflen,sig


def media2feats(medianame,input_type='file', sr=16000,ffmpeg_path='c:\\ffmpeg.exe'):
  
        return _wav2feats(medianame, input_type , sr,ffmpeg_path=ffmpeg_path)
