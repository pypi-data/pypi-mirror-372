from .lib_v5.vr_network import nets_new
from .lib_v5.vr_network.model_param_init import ModelParameters
import torch
from .lib_v5 import spec_utils
import librosa
from iman import Audio
from iman import gf,PN,PJ,os,np,PM
from tqdm import tqdm

cropsize=256

import warnings
warnings.filterwarnings('ignore')

def loading_mix(X, mp):

    X_wave, X_spec_s = {}, {}
    
    bands_n = len(mp['band'])
    
    for d in range(bands_n, 0, -1):        
        bp = mp['band'][d]

        wav_resolution = 'polyphase'#bp['res_type']
    
        if d == bands_n: # high-end band
            X_wave[d] = X

        else: # lower bands
            X_wave[d] = librosa.resample(X_wave[d+1], mp['band'][d+1]['sr'], bp['sr'], res_type=wav_resolution)
            
        X_spec_s[d] = spec_utils.wave_to_spectrogram(X_wave[d], bp['hl'], bp['n_fft'], mp, band=d, is_v51_model=True)
        
        # if d == bands_n and is_high_end_process:
        #     input_high_end_h = (bp['n_fft']//2 - bp['crop_stop']) + (mp['pre_filter_stop'] - mp['pre_filter_start'])
        #     input_high_end = X_spec_s[d][:, bp['n_fft']//2-input_high_end_h:bp['n_fft']//2, :]

    X_spec = spec_utils.combine_spectrograms(X_spec_s, mp)
    
    del X_wave, X_spec_s

    return X_spec


def Dereverb(pattern , out_fol , sr = 16000, batchsize=16 , device="cuda"  ,model_path=r"C:\UVR-DeEcho-DeReverb.pth"):
   print('Load Model...') 
   mp={'bins': 672, 'unstable_bins': 8, 'reduction_bins': 530, 'band': {1: {'sr': 7350, 'hl': 80, 'n_fft': 640, 'crop_start': 0, 'crop_stop': 85, 'lpf_start': 25, 'lpf_stop': 53, 'res_type': 'polyphase'}, 2: {'sr': 7350, 'hl': 80, 'n_fft': 320, 'crop_start': 4, 'crop_stop': 87, 'hpf_start': 25, 'hpf_stop': 12, 'lpf_start': 31, 'lpf_stop': 62, 'res_type': 'polyphase'}, 3: {'sr': 14700, 'hl': 160, 'n_fft': 512, 'crop_start': 17, 'crop_stop': 216, 'hpf_start': 48, 'hpf_stop': 24, 'lpf_start': 139, 'lpf_stop': 210, 'res_type': 'polyphase'}, 4: {'sr': 44100, 'hl': 480, 'n_fft': 960, 'crop_start': 78, 'crop_stop': 383, 'hpf_start': 130, 'hpf_stop': 86, 'res_type': 'kaiser_fast'}}, 'sr': 44100, 'pre_filter_start': 668, 'pre_filter_stop': 672, 'mid_side': False, 'mid_side_b': False, 'mid_side_b2': False, 'stereo_w': False, 'stereo_n': False, 'reverse': False}
   PM(out_fol)
   cpu = torch.device('cpu')
   nout, nout_lstm = 64, 128
   n_fft = mp['bins'] * 2
   model = nets_new.CascadedNet(n_fft, nout=nout, nout_lstm=nout_lstm)
   try:
      model.load_state_dict(torch.load(model_path, map_location=cpu))
   except:
      print("WARNING: Download model from 'https://huggingface.co/seanghay/uvr_models/resolve/main/UVR-DeEcho-DeReverb.pth' and then set model_path")   
      return
   model.to(device)
   
   files = gf(pattern)
   print('Find ' +  str(len(files)) + ' files.')
   print('Batch size= ' + str(batchsize))
   print('Sampling Rate= ' + str(sr))
   print('Start Dereverbing...')
   print('-----------------------------------------------------------------')
   for fname in files:
    print(fname)
    # XXX = librosa.load(fname, mono=False, sr=sr)[0]
    XXX = Audio.Read(fname , sr=sr,mono=False)
    chh=1 
    _w1=[]
    _w2=[]    
    for X in (XXX):
       print('Channel ' + str(chh))   
       chh=chh+1
       X_spec = loading_mix(X.T, mp)
       X_mag = np.abs(X_spec)
       X_phase = np.angle(X_spec)

       n_frame = X_mag.shape[2]
       pad_l, pad_r, roi_size = spec_utils.make_padding(n_frame, cropsize, model.offset)
       
       X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
       X_mag_pad /= X_mag_pad.max()
       
       X_dataset = []
       patches = (X_mag_pad.shape[2] - 2 * model.offset) // roi_size
       
       for i in range(patches):
               start = i * roi_size
               X_mag_crop = X_mag_pad[:, :, start:start + cropsize]
               X_dataset.append(X_mag_crop)
               
       X_dataset = np.asarray(X_dataset)
       
       model.eval()        
       with torch.no_grad():
               mask = []
               # To reduce the overhead, dataloader is not used.
               for i in tqdm(range(0, patches, batchsize)):
                   X_batch = X_dataset[i: i + batchsize]
                   X_batch = torch.from_numpy(X_batch).to(device)
       
                   pred = model.predict_mask(X_batch)
       
                   pred = pred.detach().cpu().numpy()
                   pred = np.concatenate(pred, axis=2)
                   mask.append(pred)
       
               mask = np.concatenate(mask, axis=2)
       mask = mask[:, :, :n_frame]
       
       v_spec = mask * X_mag * np.exp(1.j * X_phase)
       y_spec = (1 - mask) * X_mag * np.exp(1.j * X_phase)
       
       wave = spec_utils.cmb_spectrogram_to_wave(v_spec, mp, is_v51_model=True).T
       wave_2 = spec_utils.cmb_spectrogram_to_wave(y_spec, mp, is_v51_model=True).T

       _w1.append(wave[:,0])
       _w2.append(wave_2[:,0])
       
       

    
    Audio.Write(PJ(out_fol , PN(fname) + "_1.wav") ,np.array(_w1).T ,sr )
    print('out_path= ' + PJ(out_fol , PN(fname) + "_1.wav"))
    Audio.Write(PJ(out_fol , PN(fname) + "_2.wav") ,np.array(_w2).T ,sr )
    print('out_path= ' + PJ(out_fol , PN(fname) + "_2.wav"))
        
        

def Denoise(pattern , out_fol , sr = 16000, batchsize=16 , device="cuda"  ,model_path=r"C:\UVR-DeNoise-Lite.pth"):
   print('Load Model...') 
   PM(out_fol)
   cpu = torch.device('cpu')
   nout, nout_lstm = 16, 128
   hop_length=1024
   n_fft = 2048
   
   model = nets_new.CascadedNet(n_fft, nout=nout, nout_lstm=nout_lstm)
   try:
      model.load_state_dict(torch.load(model_path, map_location=cpu))
   except:
      print("WARNING: Download model from 'https://huggingface.co/seanghay/uvr_models/resolve/main/UVR-DeNoise-Lite.pth' and then set model_path")   
      return
   model.to(device)
   
   files = gf(pattern)
   print('Find ' +  str(len(files)) + ' files.')
   print('Batch size= ' + str(batchsize))
   print('Sampling Rate= ' + str(sr))
   print('Start DeNoising...')
   print('-----------------------------------------------------------------')
   for fname in files:
       print(fname)
       # X = Audio.Read(fname , sr , mono=False)
       X = librosa.load(fname, mono=False, sr=sr)[0]
       
       X_spec = spec_utils.wave_to_spectrogram_old(X, hop_length, n_fft)
       
      
       X_mag = np.abs(X_spec)
       X_phase = np.angle(X_spec)


       n_frame = X_mag.shape[2]
       pad_l, pad_r, roi_size = spec_utils.make_padding(n_frame, cropsize, model.offset)
       
       X_mag_pad = np.pad(X_mag, ((0, 0), (0, 0), (pad_l, pad_r)), mode='constant')
       X_mag_pad /= X_mag_pad.max()
       
       X_dataset = []
       patches = (X_mag_pad.shape[2] - 2 * model.offset) // roi_size
       
       for i in range(patches):
               start = i * roi_size
               X_mag_crop = X_mag_pad[:, :, start:start + cropsize]
               X_dataset.append(X_mag_crop)
               
       X_dataset = np.asarray(X_dataset)
       
       model.eval()        
       with torch.no_grad():
               mask = []
               # To reduce the overhead, dataloader is not used.
               for i in tqdm(range(0, patches, batchsize)):
                   X_batch = X_dataset[i: i + batchsize]
                   X_batch = torch.from_numpy(X_batch).to(device)
       
                   pred = model.predict_mask(X_batch)
       
                   pred = pred.detach().cpu().numpy()
                   pred = np.concatenate(pred, axis=2)
                   mask.append(pred)
       
               mask = np.concatenate(mask, axis=2)
       mask = mask[:, :, :n_frame]
       
       
       v_spec = (1 - mask) * X_mag * np.exp(1.j * X_phase)
       wave = spec_utils.spectrogram_to_wave_old(v_spec, hop_length=1024)
       
       import scipy.io.wavfile as __wave    
       
       if (X.ndim==2):
           xx = np.asarray( [np.int16(wave[0]*32768) , np.int16(wave[1]*32768)]).transpose()
       else:
           xx = np.int16(wave[0]*32768)       

       __wave.write(PJ(out_fol , PN(fname) + ".wav") , sr, xx)

       print('out_path= ' + PJ(out_fol , PN(fname) + ".wav"))
    