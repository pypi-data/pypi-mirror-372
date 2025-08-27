# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 11:08:34 2019

@author: deepspeech
"""

import numpy as np
import soundfile as sf
import pyworld

wav ,fs = sf.read(r'rooh.wav' ,dtype='float64' )


f0, timeaxis = pyworld.harvest(wav, fs, frame_period = 10, f0_floor = 71.0, f0_ceil = 800.0)
sp = pyworld.cheaptrick(wav, f0, timeaxis, fs)
ap = pyworld.d4c(wav, f0, timeaxis, fs)

# Get Mel-cepstral coefficients (MCEPs)
#coded_sp = pyworld.code_spectral_envelope(sp, fs, 24)
#fftlen = pyworld.get_cheaptrick_fft_size(fs)
#decoded_sp = pyworld.decode_spectral_envelope(coded_sp, fs, fftlen)



wav2 = pyworld.synthesize(f0*2, sp*5, ap*5, fs,12)

wav2 = wav2.astype(np.float32)
sf.write(r'rooh2.wav', wav2, 16000, format='wav', subtype='PCM_16')

