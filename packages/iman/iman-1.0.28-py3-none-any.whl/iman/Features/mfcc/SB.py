import torch
from .sb_mfcc_class import MFCC
from .sb_mfcc_class import InputNormalization

def Get(wav,sample_rate=8000,deltas=False,context=False,n_mels=40,n_mfcc=24,win_length=25,hop_length=10,n_fft=256):
    v = MFCC(sample_rate=sample_rate,deltas=deltas,context=context,n_mels=n_mels,n_mfcc=n_mfcc,win_length=win_length,hop_length=hop_length,n_fft=n_fft)
    return v(wav)


def Normal(x,norm_type='global', mean_norm=True,std_norm=True):
      v = InputNormalization(norm_type=norm_type,mean_norm=mean_norm,std_norm=std_norm)
      return(v(x,torch.ones([x.shape[0]])))
    
    


