import numpy as np
from scipy import signal
import os
import scipy.io.wavfile as wave
from numpy.lib.stride_tricks import as_strided
import six
import subprocess
import platform
from iman import *

_system = platform.system().lower()



def Read_Alaw_1(filename):
    with open(filename, "rb") as binaryfile :
       myArr = bytearray(binaryfile.read())
    g=[ALawDecompressTable[x]/32768 for x in myArr]
    return np.array(g , dtype=np.float32)
    
    
def Read_Alaw(filename,sr=8000,start_from=0,dur=-1,ffmpeg_path='c:\\ffmpeg.exe'):

           ffmpeg_command = [ffmpeg_path, "-ss" , str(start_from) ,  "-ar","8000", "-f" ,"alaw" ,'-i', filename, '-ac', "1", '-ar', str(sr), '-f', 'wav', 'pipe:1']
           if (dur!=-1):
               ffmpeg_command = [ffmpeg_path, "-ss" , str(start_from) , "-t" ,str(dur) , "-ar","8000", "-f" ,"alaw" ,'-i', filename, '-ac', "1", '-ar', str(sr), '-f', 'wav', 'pipe:1']            
           
           pipe = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE,   stderr=subprocess.PIPE,  bufsize=10**8)
           
           audio_np = np.frombuffer(buffer=pipe.stdout, dtype=np.uint16, offset=8*44)
             
           x =np.where(audio_np>32768)    [0]    
           y =np.where(audio_np<=32768)    [0]  
           
           out_wav = np.zeros(len(audio_np) , dtype=np.float32)
           out_wav[x] = (audio_np[x] - 32768)/32768-1
           out_wav[y] = audio_np[y] /32768
           
          
           return(out_wav) 
       

def Resample(data , fs, sr):
    """Return Resampled Data.

    Parameters
    ----------
    data : input audio data
    fs : data sampling rate
    sr : resample data to sr
    
    Output
    ----------
    data with sampling rate --> sr

    """
    if (fs!=sr):
        nesbat = sr/fs
        m = np.max(np.abs(data))
        data = 0.5*(data/(m+1e-6))
        data = signal.resample(data, int(len(data)*nesbat))
    return (np.array(data , dtype=np.float32))    

def ReadMp3_miniaudio(filename,sr,mono=True):
    import miniaudio
    mp3file = miniaudio.read_file(filename,True)
    sample_rate = mp3file.sample_rate
    data =  np.array(mp3file.samples , dtype=np.float32)/32768
    if (mp3file.nchannels==1):
       if (sample_rate!=sr):
            data = Resample(data ,sample_rate ,sr )
    else:
         ch1=np.array( data[::2] , dtype=np.float32)
         ch2=np.array(data[1::2], dtype=np.float32)
         if (mono):
           cha = ch1+ch2
         if (sample_rate!=sr):
                if (mono):
                  cha = Resample(cha ,sample_rate ,sr )
                else:  
                   ch1 = Resample(ch1 ,sample_rate ,sr )
                   ch2 = Resample(ch2 ,sample_rate ,sr )
         if (mono):          
           data = cha
         else:
           data=  [ch1,ch2]       
    return(data)




def ReadFFMPEG(filename,sr=16000,start_from=0,dur=-1,mono = False , ffmpeg_path='c:\\ffmpeg.exe',ffprobe_path='c:\\ffprobe.exe'):
           
           chnumber = 1
           if (not mono):
             ffprobe_command = [ffprobe_path ,  "-v","error","-show_entries","stream=channels","-of","default=nw=1" ,filename ] 
             pipe1 = subprocess.run(ffprobe_command, stdout=subprocess.PIPE)
             chnumber = int(str(pipe1.stdout).strip().split('=')[1].split('\\')[0])
             
           
           
           ffmpeg_command = [ffmpeg_path,  '-i', filename,'-ss' , str(start_from),  '-ac' ,str(chnumber) , '-ar', str(sr), '-f', 'wav', 'pipe:1']
           
           if (dur!=-1):
                    ffmpeg_command = [ffmpeg_path, '-i', filename, '-ss' , str(start_from), '-t' , str(dur) , '-ac', str(chnumber), '-ar', str(sr), '-f', 'wav', 'pipe:1']
           
           pipe = subprocess.run(ffmpeg_command, stdout=subprocess.PIPE,   stderr=subprocess.PIPE,  bufsize=10**8)
           
           # audio_np = np.frombuffer(buffer=pipe.stdout, dtype=np.uint16, offset=8*44)
             
             
           import wave
           import io
           wav_data = io.BytesIO(pipe.stdout)
           with wave.open(wav_data) as wav_file:
               audio_data = wav_file.readframes(wav_file.getnframes())
               audio_np = np.frombuffer(audio_data, dtype=np.int16)
               
               
           x =np.where(audio_np>32768)    [0]    
           y =np.where(audio_np<=32768)    [0]  
           
           out_wav = np.zeros(len(audio_np) , dtype=np.float32)
           out_wav[x] = (audio_np[x] - 32768)/32768-1
           out_wav[y] = audio_np[y] /32768
           
           
           x=[]
           if (chnumber==1):
              x.append(out_wav)
              if (mono):
                 return x[0]
              else:   
                 return(x) 
           else:
              x.append(out_wav[1::2])
              x.append(out_wav[::2]) 
              return(x)



def Read(filename,sr=8000, start_from=0, dur=-1,mono = False,ffmpeg_path='c:\\ffmpeg.exe',ffprobe_path='c:\\ffprobe.exe' ):   # output sampling rate is sr
   """Return Audio Data. (Just Mono Files)

    Parameters
    ----------
    filename : input file path (PCM or alaw or [alaw_raw with .l or .r ext] or mp3)
    sr : desired sampling rate
    
    Output
    ----------
    data with sampling rate --> sr

   """   
   ext = os.path.basename(filename).split('.')[-1] 
   if (ext.lower() == 'l' or ext.lower() == 'r' or os.path.basename(filename).lower().endswith('.r.wav') or os.path.basename(filename).lower().endswith('.l.wav') or os.path.basename(filename).lower().endswith('.rtemp.wav') or os.path.basename(filename).lower().endswith('.ltemp.wav')):
         return( Read_Alaw(filename,sr=sr ,ffmpeg_path=ffmpeg_path ,start_from=start_from,dur=dur))
       
  
   return(ReadFFMPEG(filename,sr=sr, start_from=start_from,dur=dur,mono =mono ,  ffmpeg_path=ffmpeg_path,ffprobe_path=ffprobe_path ))
    
   
   
   # if (ext.lower() == 'mp3'):
         # return(ReadMp3(filename,sr=sr, mono=True,ffmpeg_path=ffmpeg_path))
   
   # File_Type_Header= np.fromfile(filename, dtype=np.byte, count=4, offset=8)
   # File_Type_Header = "".join(map(chr, File_Type_Header))   # Must be WAVE
   # if (File_Type_Header!="WAVE"):
       # return(ReadMp3(filename,sr=sr, mono=True,ffmpeg_path=ffmpeg_path))
       
   # Type_of_format = np.fromfile(filename, dtype=np.int8, count=1, offset=20)[0]  # 1 is PCM   6 is alaw

   # ch = np.fromfile(filename, dtype=np.int8, count=1, offset=22)[0]  
   
   # if (ch!=1):
       # return(ReadMp3(filename,sr=sr, mono=True,ffmpeg_path=ffmpeg_path))
   
   # fs = np.fromfile(filename, dtype=np.int32, count=1, offset=24)[0] # Hz
   
   # if (Type_of_format!=1 and Type_of_format!=6 ):
       # return(ReadMp3(filename,sr=sr, mono=True,ffmpeg_path=ffmpeg_path))
   
   # if (Type_of_format==6):   # if file is alaw
        # byte_length = np.fromfile(filename, dtype=np.int32, count=1, offset=40)[0]
        # data = np.fromfile(filename, dtype=np.byte, count=byte_length*4, offset=44)
        # data=np.array([ALawDecompressTable[x]/32768 for x in data], dtype=np.float32)
        # return (Resample(data,fs,sr))
   
   # chunk_header = np.fromfile(filename, dtype=np.byte, count=4, offset=36)
   # chunk_header = "".join(map(chr, chunk_header))
   # if (chunk_header!="data"):
     # if (_system == 'windows'):
      # data=ReadMp3(filename,sr=sr, mono=True,ffmpeg_path=ffmpeg_path)
     # else:
      # import librosa
      # data,_ = librosa.load(filename , sr)      
   # elif(chunk_header=="data"):
      # byte_length = np.fromfile(filename, dtype=np.int32, count=1, offset=40)[0]
      # data = np.fromfile(filename, dtype=np.int16, count=byte_length // 2, offset=44)/32768
      # data = Resample(data,fs,sr)
   # return (data)

def Write(filename, data ,fs):

   """Write Audio Data.

    Parameters
    ----------
    filename : Output file path (.wav)
    data : Audio data
    fs : sampling rate
    
    Output
    ----------
    Nothing

   """
   wave.write(filename, fs, np.int16(data*32768))
   
def WriteS(filename, data ,fs):

   """Write Audio Data Sterio.

    Parameters
    ----------
    filename : Output file path (.wav)
    data : Audio data
    fs : sampling rate
    
    Output
    ----------
    Nothing

   """
   xx = np.asarray( [np.int16(data*32768) , np.int16(data*32768)]).transpose()

   wave.write(filename, fs, xx)
def rmse(y=None, S=None, frame_length=2048, hop_length=512,
         center=True, pad_mode='reflect'):
    
    if y is not None and S is not None:
        raise ValueError('Either `y` or `S` should be input.')
    if y is not None:
        y = (y)
        if center:
            y = np.pad(y, int(frame_length // 2), mode=pad_mode)

        x = frame(y,
                       frame_length=frame_length,
                       hop_length=hop_length)
    elif S is not None:
        x, _ = _spectrogram(y=y, S=S,
                            n_fft=frame_length,
                            hop_length=hop_length)
    else:
        raise ValueError('Either `y` or `S` must be input.')
    return np.sqrt(np.mean(np.abs(x)**2, axis=0, keepdims=True))
def frame(y, frame_length=2048, hop_length=512):
   
    if not isinstance(y, np.ndarray):
        raise ParameterError('Input must be of type numpy.ndarray, '
                             'given type(y)={}'.format(type(y)))

    if y.ndim != 1:
        raise ParameterError('Input must be one-dimensional, '
                             'given y.ndim={}'.format(y.ndim))

    if len(y) < frame_length:
        raise ParameterError('Buffer is too short (n={:d})'
                             ' for frame_length={:d}'.format(len(y), frame_length))

    if hop_length < 1:
        raise ParameterError('Invalid hop_length: {:d}'.format(hop_length))

    if not y.flags['C_CONTIGUOUS']:
        raise ParameterError('Input buffer must be contiguous.')

    # Compute the number of frames that will fit. The end may get truncated.
    n_frames = 1 + int((len(y) - frame_length) / hop_length)

    # Vertical stride is one sample
    # Horizontal stride is `hop_length` samples
    y_frames = as_strided(y, shape=(frame_length, n_frames),
                          strides=(y.itemsize, hop_length * y.itemsize))
    return y_frames	
def power_to_db(S, ref=1.0, amin=1e-10, top_db=80.0):
   

    S = np.asarray(S)

    if amin <= 0:
        raise ParameterError('amin must be strictly positive')

    if np.issubdtype(S.dtype, np.complexfloating):
        warnings.warn('power_to_db was called on complex input so phase '
                      'information will be discarded. To suppress this warning, '
                      'call power_to_db(magphase(D, power=2)[0]) instead.')
        magnitude = np.abs(S)
    else:
        magnitude = S

    if six.callable(ref):
        # User supplied a function to calculate reference power
        ref_value = ref(magnitude)
    else:
        ref_value = np.abs(ref)

    log_spec = 10.0 * np.log10(np.maximum(amin, magnitude))
    log_spec -= 10.0 * np.log10(np.maximum(amin, ref_value))

    if top_db is not None:
        if top_db < 0:
            raise ParameterError('top_db must be non-negative')
        log_spec = np.maximum(log_spec, log_spec.max() - top_db)

    return log_spec
def _signal_to_frame_nonsilent(y_mono, frame_length=2048, hop_length=512, top_db=60,
                               ref=np.max):

    # Convert to mono
   

    # Compute the MSE for the signal
    mse = rmse(y=y_mono,
                       frame_length=frame_length,
                       hop_length=hop_length)**2

    return (power_to_db(mse.squeeze(),
                             ref=ref,
                             top_db=None) > - top_db)					 
def split(y, top_db=40, ref=np.max, frame_length=200, hop_length=80):

    non_silent = _signal_to_frame_nonsilent(y,
                                            frame_length=frame_length,
                                            hop_length=hop_length,
                                            ref=ref,
                                            top_db=top_db)

    edges = np.flatnonzero(np.diff(non_silent.astype(int)))

    # Pad back the sample lost in the diff
    edges = [edges + 1]

    # If the first frame had high energy, count it
    if non_silent[0]:
        edges.insert(0, [0])

    # Likewise for the last frame
    if non_silent[-1]:
        edges.append([len(non_silent)])

    # Convert from frames to samples
    edges = frames_to_samples(np.concatenate(edges),
                                   hop_length=hop_length)

    # Clip to the signal duration
    edges = np.minimum(edges, y.shape[-1])

    # Stack the results back as an ndarray
    return edges.reshape((-1, 2))
    
def frames_to_samples(frames, hop_length=512, n_fft=None):
 
    offset = 0
    if n_fft is not None:
        offset = int(n_fft // 2)

    return (np.asanyarray(frames) * hop_length + offset).astype(int)
    
def ReadT(filename, sr=8000 , mono=True): 
    import torchaudio
    
    wavs, fs = torchaudio.load(filename)
    
    if (fs!=sr):
       import torchaudio.transforms as T  
       resampler = T.Resample(fs, sr, dtype=wavs.dtype)
       wavs  = resampler(wavs)
    
    if (len(wavs)==2 and mono==True):
        return ( (wavs[0] +wavs[1]).unsqueeze(0))
        
    return wavs
    
def VAD(wav,top_db=40, frame_length=200, hop_length=80):
    a = split(wav,top_db=top_db, frame_length=frame_length, hop_length=hop_length)
    v_wav=[]
    for x in a:
        v_wav.append(wav[x[0]:x[1]])
    v = np.concatenate(v_wav)
    return(v)       
    
def change_format(fname , sr=16000 , ext='mp3' , mono=True ,ffmpeg_path='c:\\ffmpeg.exe' ,oname=None ):
    chnum=2
    if (mono):
      chnum=1
      
    forext = []
    if (PE(fname).lower()=='.l' or PE(fname).lower()=='.r') :
         forext = ['-ar', '8000', '-f' ,'alaw']    
      
      
    if (not ext.startswith('.')):
       ext = '.' + ext    

    if (oname==None):
       outfile =  PJ(PD(fname) , PN(fname)+ ext)
    else:
      if ('.' in oname):
        outfile =  oname
      else:
        outfile =  oname + ext
    
    if (PX(outfile)):
       print('File Exists--> ' + PB(outfile))
       return 0
       
    try:
    
      if (forext==[]):
         ffmpeg_command = [ffmpeg_path, '-i', fname, '-ac', str(chnum), '-ar', str(sr), 'outfile']
      else:
          ffmpeg_command = [ffmpeg_path]
          ffmpeg_command.extend(forext)
          ffmpeg_command.extend(['-i', fname, '-ac', str(chnum), '-ar', str(sr), 'outfile'])

      x = cmd(ffmpeg_command )
      if (PX(outfile) and PS(outfile)>1):
         return 1
      else:
          try:
             os.remove(outfile)
          except:
             pass 
          return 0             
          
    except:
      print('ffmpeg has Problem with --> ' + PB(outfile)) 
      try:
         os.remove(outfile)
      except:
         pass
      
      return 0
 

def fun(fname , b):
   change_format(fname , sr=b[0] , ext=b[1] , mono=b[2] , ffmpeg_path=b[3] , oname=PJ(b[4] , PN(fname) + b[1] ) )
 
def compress (fname_pattern , sr=16000 , ext='mp3' , mono=True ,ffmpeg_path='c:\\ffmpeg.exe' , ofolder=None , worker=4): 
    
    if (not ext.startswith('.')):
       ext = '.' + ext    
       
    files = gf(fname_pattern) 
    
    
    if (len(files)==0):
        print('no File!!!')
        return
    
   
    if (ofolder==None):
        pp = input('It is better to set ofolder\n press y to continue compression: ')
        if (pp.lower()=='y'):
          ofolder=""
        else:
           return        
    else:
       PM(ofolder)
    
    worker=min(len(files) , worker)     

    from multiprocessing import Pool
    from functools import partial  
    with Pool(processes=worker) as pool:
         pool.map(partial(fun, b=[sr , ext,mono , ffmpeg_path,ofolder]), files)     



def clip_value(wav):

    # wav must be output of sad
    wav = abs( wav / abs(wav).max())

    cli= np.where(wav>=0.99)[0]
    cli1 = np.insert(np.delete(cli-1 ,0) , len(cli)-1,0)
    cli2=np.delete(np.insert(cli+1,0,0) , len(cli))   
    
    a=(cli == cli1 ) 
    b=(cli == cli2)
    c = np.logical_or(a, b)
    
    x = len(np.where(c==True)[0])
        
    clip_percentage = 100*x / len(wav)
    return (clip_percentage)         
    
    

ALawDecompressTable =[

     -5504, -5248, -6016, -5760, -4480, -4224, -4992, -4736,

     -7552, -7296, -8064, -7808, -6528, -6272, -7040, -6784,

     -2752, -2624, -3008, -2880, -2240, -2112, -2496, -2368,

     -3776, -3648, -4032, -3904, -3264, -3136, -3520, -3392,

     -22016,-20992,-24064,-23040,-17920,-16896,-19968,-18944,

     -30208,-29184,-32256,-31232,-26112,-25088,-28160,-27136,

     -11008,-10496,-12032,-11520,-8960, -8448, -9984, -9472,

     -15104,-14592,-16128,-15616,-13056,-12544,-14080,-13568,

     -344,  -328,  -376,  -360,  -280,  -264,  -312,  -296,

     -472,  -456,  -504,  -488,  -408,  -392,  -440,  -424,

     -88,   -72,   -120,  -104,  -24,   -8,    -56,   -40,

     -216,  -200,  -248,  -232,  -152,  -136,  -184,  -168,

     -1376, -1312, -1504, -1440, -1120, -1056, -1248, -1184,

     -1888, -1824, -2016, -1952, -1632, -1568, -1760, -1696,

     -688,  -656,  -752,  -720,  -560,  -528,  -624,  -592,

     -944,  -912,  -1008, -976,  -816,  -784,  -880,  -848,

      5504,  5248,  6016,  5760,  4480,  4224,  4992,  4736,

      7552,  7296,  8064,  7808,  6528,  6272,  7040,  6784,

      2752,  2624,  3008,  2880,  2240,  2112,  2496,  2368,

      3776,  3648,  4032,  3904,  3264,  3136,  3520,  3392,

      22016, 20992, 24064, 23040, 17920, 16896, 19968, 18944,

      30208, 29184, 32256, 31232, 26112, 25088, 28160, 27136,

      11008, 10496, 12032, 11520, 8960,  8448,  9984,  9472,

      15104, 14592, 16128, 15616, 13056, 12544, 14080, 13568,

      344,   328,   376,   360,   280,   264,   312,   296,

      472,   456,   504,   488,   408,   392,   440,   424,

      88,    72,   120,   104,    24,     8,    56,    40,

      216,   200,   248,   232,   152,   136,   184,   168,

      1376,  1312,  1504,  1440,  1120,  1056,  1248,  1184,

      1888,  1824,  2016,  1952,  1632,  1568,  1760,  1696,

      688,   656,   752,   720,   560,   528,   624,   592,

      944,   912,  1008,   976,   816,   784,   880,   848]