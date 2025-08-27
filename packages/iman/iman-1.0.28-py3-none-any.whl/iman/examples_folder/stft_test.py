# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 12:07:27 2019

@author: deepspeech
"""

import librosa as l
import numpy as np
import soundfile as sf

wav, sr = l.load('test.wav', sr=16000)
st = l.stft(y=wav , n_fft=256 , hop_length=128 , win_length=256)
mag = np.abs(st)
phase  = np.angle(st) 

stft = mag * np.exp(1.j * phase)

wav2 = l.istft(stft, win_length=256, hop_length=128)

sf.write('test2.wav', wav2, 16000, format='wav', subtype='PCM_16')


