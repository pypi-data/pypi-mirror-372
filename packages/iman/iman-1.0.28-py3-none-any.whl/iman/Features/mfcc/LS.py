# -*- coding: utf-8 -*-
"""
Created on Wed Jun 10 14:09:03 2020

@author: user
"""
#Extract MFCC with Librosa

import numpy as np
from scipy import signal
from .getmfcc_from_librosa import *


def framing(sig, win_size, win_shift=1, context=(0, 0), pad='zeros'):
    """
    :param sig: input signal, can be mono or multi dimensional
    :param win_size: size of the window in term of samples
    :param win_shift: shift of the sliding window in terme of samples
    :param context: tuple of left and right context
    :param pad: can be zeros or edge
    """
    dsize = sig.dtype.itemsize
    if sig.ndim == 1:
        sig = sig[:, np.newaxis]
    # Manage padding
    c = (context, ) + (sig.ndim - 1) * ((0, 0), )
    _win_size = win_size + sum(context)
    shape = (int((sig.shape[0] - win_size) / win_shift) + 1, 1, _win_size, sig.shape[1])
    strides = tuple(map(lambda x: x * dsize, [win_shift * sig.shape[1], 1, sig.shape[1], 1]))
    if pad == 'zeros':
        return np.lib.stride_tricks.as_strided(np.lib.pad(sig, c, 'constant', constant_values=(0,)),
                                                  shape=shape,
                                                  strides=strides).squeeze()
    elif pad == 'edge':
        return np.lib.stride_tricks.as_strided(np.lib.pad(sig, c, 'edge'),
                                                  shape=shape,
                                                  strides=strides).squeeze()
    
    
def preemphasis(wav, coeff=0.975):
    preem_wav = signal.lfilter([1, -coeff], [1], wav)
    return preem_wav

def wav2melspec(wav, sr, n_fft, win_length, hop_length, n_mels, time_first=True, **kwargs):
    # Linear spectrogram
    mag_spec, phase_spec = wav2spec(wav, n_fft, win_length, hop_length, time_first=False)

    # Mel-spectrogram
    mel_spec = linear_to_mel(mag_spec, sr, n_fft, n_mels, **kwargs)

    # Time-axis first
    if time_first:
        mel_spec = mel_spec.T  # (t, n_mels)

    return mel_spec

def wav2melspec_db(wav, sr, n_fft, win_length, hop_length, n_mels,time_first=True, **kwargs):
    # Mel-spectrogram
    mel_spec = wav2melspec(wav, sr, n_fft, win_length, hop_length, n_mels, time_first=False, **kwargs)

    # Decibel
    mel_db = amplitude_to_db(mel_spec)

    # Time-axis first
    if time_first:
        mel_db = mel_db.T  # (t, n_mels)

    return mel_db

def wav2spec(wav, n_fft, win_length, hop_length, time_first=True):
    stft = STFT(y=wav, n_fft=n_fft, hop_length=hop_length, win_length=win_length)
    mag = np.abs(stft)
    phase = np.angle(stft)

    if time_first:
        mag = mag.T
        phase = phase.T

    return mag, phase

def wav2mfcc(wav, sr, n_fft=256, win_length=200, hop_length=80, n_mels=40, n_mfccs=24, preemphasis_coeff=0.975, time_first=True,
             **kwargs):
    # Pre-emphasis
    wav_preem = preemphasis(wav, coeff=preemphasis_coeff)
    
    
    framed = framing(wav, win_length, win_shift=hop_length).copy()
    framed = preemphasis(framed, 0.97)
   
  
    log_energy = np.log((framed**2).sum(axis=1))
    

    # Decibel-scaled mel-spectrogram
    mel_db = wav2melspec_db(wav_preem, sr, n_fft, win_length, hop_length, n_mels, time_first=False, **kwargs)

    # MFCCs
    mfccs = np.dot(dct(n_mfccs, mel_db.shape[0]), mel_db)


    # Time-axis first
    if time_first:
        mfccs = mfccs.T  # (t, n_mfccs)

    return np.asarray(mfccs , dtype = np.float32),log_energy

def linear_to_mel(linear, sr, n_fft, n_mels, **kwargs):
    mel_basis = MEL(sr, n_fft, n_mels, **kwargs)  # (n_mels, 1+n_fft//2)
    mel = np.dot(mel_basis, linear)  # (n_mels, t) # mel spectrogram
    return mel
    
def local_MVN(X , num):
    feat=np.empty((0,np.shape(X)[1]))
    window = num*2
    le = len(X)//window
    for i in range(le+1):
       xx = X[(i*window) : ((i+1)*window)]
       if (len(xx)==0):
          break
       m = xx.mean(axis=0)
       s = xx.std(axis=0)
       xx_mvn = (xx-m)/(s+(2**-30))
       feat=np.insert(feat,i*window,xx_mvn , axis=0)
    return(feat)
 

def Get(wav,sample_rate,le=False):
     mfccs,log_energy = wav2mfcc (wav , sr=sample_rate)
     if (le):
         return mfccs,log_energy
     else:
         return mfccs
         
def Normal(mfccs , win_len=150):
   mfccs = local_MVN(mfccs,win_len)
   mfccs = np.nan_to_num(mfccs, nan=0.0) 
   return(mfccs)
