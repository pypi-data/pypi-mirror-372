import os
import numpy as np
from iman import Audio
from iman import Features


def media2feats(wavname,sr=8000,start_from=0 ,dur=-1,ffmpeg_path='c:\\ffmpeg.exe'):
    try:
       sig1 = Audio.Read(wavname ,sr,start_from , dur ,True, ffmpeg_path)
    except :
        return [],[]
    sig=sig1+1e-7
    try:    
      mfccs,loge  = Features.LS.Get(sig , sr , True)   
    except:
      print('error in mfcc extraction')
      return [] ,[]   
    if (len(loge)<68):   
           return [] ,[]
    return  mfccs , loge     
  
