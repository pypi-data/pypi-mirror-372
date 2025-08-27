import os
import numpy as np
from iman import Audio
from iman import Features
import torch


def media2feats(wavname,sr=16000,start_from=0 ,dur=-1,ffmpeg_path='c:\\ffmpeg.exe'):
    try:
       sig1 = Audio.Read(wavname ,sr,start_from , dur ,True, ffmpeg_path)
    except :
        return [],[]
    sig=sig1+1e-7
    sig = torch.unsqueeze( torch.from_numpy(sig) , dim=0) 
    try:    
      mfccs, mspec,loge  = Features.SB.Get(sig , sr , n_mels=40 , n_mfcc=24 , n_fft=200)   
    except:
      print('error in mfcc extraction')
      return [] ,[]   
    if (len(loge)<68):   
           return [] ,[]
    return  mfccs , loge     
  
