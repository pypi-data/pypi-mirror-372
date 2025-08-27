from iman import *
from scipy.signal import fftconvolve
import subprocess


def cut_noise(noise , le):
      n=[]
      mle = len(noise)
      if (mle > le):
         return noise[0:le]
      else:
         kt = le//mle    
         for i in range(kt):
             n = np.hstack((n , noise))
         nn = noise[0:le - mle*kt]
         n = np.hstack((n , nn))
         return n
     
def Add_Noise( data , noise , snr=15):
        cutnoise = cut_noise(noise , len(data))
        iPn = 1/np.mean(noise*noise)
        Px = np.mean(data*data)
        Msnr = np.sqrt( 10**(-snr/10) * iPn*Px )
        data_noise = data + cutnoise*Msnr
        return data_noise
 

def Add_Reverb( data , rir):
      return fftconvolve(data,rir)[1000:len(data)+1000]
 
def mp3(fname,fout,sr_out,ratio,ffmpeg_path='c:\\ffmpeg.exe'):
   try:
    
    command='%s -i "%s"  -ar %s -f mp3 pipe: | %s -f mp3 -i pipe: -y -ar %s "%s" ' %(ffmpeg_path,fname ,ratio,ffmpeg_path,sr_out, fout) 
    os.system(command)

    return 1  
   except:
    return 0        
  

def speed(fname,fout,ratio,ffmpeg_path='c:\\ffmpeg.exe'):
   try:
    command='%s -i "%s"   -af "atempo=%s" "%s"' %(ffmpeg_path,fname ,ratio,fout )   
    os.system(command) 
    return 1
   except:
     return 0  

def volume(fname ,fout,ratio,ffmpeg_path='c:\\ffmpeg.exe'):
   try:
    command='%s -i "%s"   -af "volume=%s" "%s"' %(ffmpeg_path,fname ,ratio,fout ) 
    os.system(command)
    return 1
   except:
     return 0  
   
	             
def Add_NoiseT( data , noise , snr=15):
        data = data.squeeze()
        noise = noise.squeeze()
        cutnoise = cut_noise(noise , data.size(0))
        iPn = 1/torch.mean(noise*noise)
        Px = torch.mean(data*data)
        Msnr = torch.sqrt( 10**(-snr/10) * iPn*Px )
        data_noise = data + cutnoise*Msnr
        return data_noise

    
def Add_ReverbT( data , rir):
      data = data.squeeze()
      rir = rir.squeeze()
      return fftconvolve(data,rir)[1000:data.size(0)+1000]                 