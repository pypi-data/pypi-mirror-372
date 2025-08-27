import numpy as np
import librosa
import math
import platform
import iman.Features.mfcc.getmfcc_from_librosa as libr 

OPERATING_SYSTEM = platform.system()
SYSTEM_ARCH = platform.platform()
SYSTEM_PROC = platform.processor()


if OPERATING_SYSTEM == 'Windows':
    from pyrubberband import pyrb
else:
    from . import pyrb

if OPERATING_SYSTEM == 'Darwin':
    wav_resolution = "polyphase" if SYSTEM_PROC == ARM or ARM in SYSTEM_ARCH else "sinc_fastest" 
    wav_resolution_float_resampling = "kaiser_best" if SYSTEM_PROC == ARM or ARM in SYSTEM_ARCH else wav_resolution 
    is_macos = True
else:
    wav_resolution = "sinc_fastest"
    wav_resolution_float_resampling = wav_resolution 
 
def spectrogram_to_wave_old(spec, hop_length=1024):
    if spec.ndim == 2:
        wave = libr.istft(spec, hop_length=hop_length)
    elif spec.ndim == 3:
        spec_left = np.asfortranarray(spec[0])
        spec_right = np.asfortranarray(spec[1])

        wave_left = libr.istft(spec_left, hop_length=hop_length)
        wave_right = libr.istft(spec_right, hop_length=hop_length)
        wave = np.asfortranarray([wave_left, wave_right])

    return wave

def wave_to_spectrogram_old(wave, hop_length, n_fft):


    if (wave.ndim != 2):
       wave_left = np.asfortranarray(wave)
    
    if (wave.ndim == 2):
        wave_left = np.asfortranarray(wave[0])
        wave_right = np.asfortranarray(wave[1])

    spec_left = libr.STFT(wave_left, n_fft, hop_length=hop_length)
    
    if (wave.ndim == 2):
        spec_right = libr.STFT(wave_right, n_fft, hop_length=hop_length)
    
    if (wave.ndim == 1):
       spec = np.asfortranarray([spec_left,spec_left]) 
    else:
       spec = np.asfortranarray([spec_left, spec_right])    
    

    return spec
 
def convert_channels(spec, mp, band):
    cc = mp['band'][band].get('convert_channels')

    if 'mid_side_c' == cc:
        spec_left = np.add(spec[0], spec[1] * .25)
        spec_right = np.subtract(spec[1], spec[0] * .25)
    elif 'mid_side' == cc:
        spec_left = np.add(spec[0], spec[1]) / 2
        spec_right = np.subtract(spec[0], spec[1])
    elif 'stereo_n' == cc:
        spec_left = np.add(spec[0], spec[1] * .25) / 0.9375
        spec_right = np.add(spec[1], spec[0] * .25) / 0.9375
    else:
        return spec
        
    return np.asfortranarray([spec_left, spec_right])
  
def wave_to_spectrogram(wave, hop_length, n_fft, mp, band, is_v51_model=False):

    if wave.ndim == 1:
        wave = np.asfortranarray([wave,wave])

    if not is_v51_model:
        if mp['reverse']:
            wave_left = np.flip(np.asfortranarray(wave[0]))
            wave_right = np.flip(np.asfortranarray(wave[1]))
        elif mp['mid_side']:
            wave_left = np.asfortranarray(np.add(wave[0], wave[1]) / 2)
            wave_right = np.asfortranarray(np.subtract(wave[0], wave[1]))
        elif mp['mid_side_b2']:
            wave_left = np.asfortranarray(np.add(wave[1], wave[0] * .5))
            wave_right = np.asfortranarray(np.subtract(wave[0], wave[1] * .5))
        else:
            wave_left = np.asfortranarray(wave[0])
            wave_right = np.asfortranarray(wave[1])
    else:
        wave_left = np.asfortranarray(wave[0])
        wave_right = np.asfortranarray(wave[1])

    spec_left = libr.STFT(wave_left, n_fft, hop_length=hop_length)
    spec_right = libr.STFT(wave_right, n_fft, hop_length=hop_length)
    
    spec = np.asfortranarray([spec_left, spec_right])

    if is_v51_model:
        spec = convert_channels(spec, mp, band)

    return spec
	
   
def combine_spectrograms(specs, mp, is_v51_model=False):
    l = min([specs[i].shape[2] for i in specs])    
    spec_c = np.zeros(shape=(2, mp['bins'] + 1, l), dtype=np.complex64)
    offset = 0
    bands_n = len(mp['band'])
    
    for d in range(1, bands_n + 1):
        h = mp['band'][d]['crop_stop'] - mp['band'][d]['crop_start']
        spec_c[:, offset:offset+h, :l] = specs[d][:, mp['band'][d]['crop_start']:mp['band'][d]['crop_stop'], :l]
        offset += h
        
    if offset > mp['bins']:
        raise ValueError('Too much bins')
        
    # lowpass fiter
    
    if mp['pre_filter_start'] > 0:
        if is_v51_model:
            spec_c *= get_lp_filter_mask(spec_c.shape[1], mp['pre_filter_start'], mp['pre_filter_stop'])
        else:
            if bands_n == 1:
                spec_c = fft_lp_filter(spec_c, mp['pre_filter_start'], mp['pre_filter_stop'])
            else:
                gp = 1        
                for b in range(mp['pre_filter_start'] + 1, mp['pre_filter_stop']):
                    g = math.pow(10, -(b - mp['pre_filter_start']) * (3.5 - gp) / 20.0)
                    gp = g
                    spec_c[:, b, :] *= g
                
    return np.asfortranarray(spec_c)
	
def make_padding(width, cropsize, offset):
    left = offset
    roi_size = cropsize - offset * 2
    if roi_size == 0:
        roi_size = cropsize
    right = roi_size - (width % roi_size) + left

    return left, right, roi_size
	

def spectrogram_to_wave(spec, hop_length=1024, mp={}, band=0, is_v51_model=True):
    spec_left = np.asfortranarray(spec[0])
    spec_right = np.asfortranarray(spec[1])
    
    
    
    wave_left = libr.istft(spec_left, hop_length=hop_length)
    wave_right = libr.istft(spec_right, hop_length=hop_length)
    
    if is_v51_model:
        cc = mp['band'][band].get('convert_channels')
        if 'mid_side_c' == cc:
            return np.asfortranarray([np.subtract(wave_left / 1.0625, wave_right / 4.25), np.add(wave_right / 1.0625, wave_left / 4.25)])    
        elif 'mid_side' == cc:
            return np.asfortranarray([np.add(wave_left, wave_right / 2), np.subtract(wave_left, wave_right / 2)])
        elif 'stereo_n' == cc:
            return np.asfortranarray([np.subtract(wave_left, wave_right * .25), np.subtract(wave_right, wave_left * .25)])
    else:
        if mp['reverse']:
            return np.asfortranarray([np.flip(wave_left), np.flip(wave_right)])
        elif mp['mid_side']:
            return np.asfortranarray([np.add(wave_left, wave_right / 2), np.subtract(wave_left, wave_right / 2)])
        elif mp['mid_side_b2']:
            return np.asfortranarray([np.add(wave_right / 1.25, .4 * wave_left), np.subtract(wave_left / 1.25, .4 * wave_right)])
    
    return np.asfortranarray([wave_left, wave_right])
    

def crop_center(h1, h2):
    h1_shape = h1.size()
    h2_shape = h2.size()

    if h1_shape[3] == h2_shape[3]:
        return h1
    elif h1_shape[3] < h2_shape[3]:
        raise ValueError('h1_shape[3] must be greater than h2_shape[3]')

    s_time = (h1_shape[3] - h2_shape[3]) // 2
    e_time = s_time + h2_shape[3]
    h1 = h1[:, :, :, s_time:e_time]

    return h1
    
def fft_hp_filter(spec, bin_start, bin_stop):
    g = 1.0
    for b in range(bin_start, bin_stop, -1):
        g -= 1 / (bin_start - bin_stop)
        spec[:, b, :] = g * spec[:, b, :]
    
    spec[:, 0:bin_stop+1, :] *= 0

    return spec
    
def cmb_spectrogram_to_wave(spec_m, mp, extra_bins_h=None, extra_bins=None, is_v51_model=False):
    bands_n = len(mp['band'])    
    offset = 0

    for d in range(1, bands_n + 1):
        bp = mp['band'][d]
        spec_s = np.ndarray(shape=(2, bp['n_fft'] // 2 + 1, spec_m.shape[2]), dtype=complex)
        h = bp['crop_stop'] - bp['crop_start']
        spec_s[:, bp['crop_start']:bp['crop_stop'], :] = spec_m[:, offset:offset+h, :]
                
        offset += h
        if d == bands_n: # higher
            if extra_bins_h: # if --high_end_process bypass
                max_bin = bp['n_fft'] // 2
                spec_s[:, max_bin-extra_bins_h:max_bin, :] = extra_bins[:, :extra_bins_h, :]
            if bp['hpf_start'] > 0:
                if is_v51_model:
                    spec_s *= get_hp_filter_mask(spec_s.shape[1], bp['hpf_start'], bp['hpf_stop'] - 1)
                else:
                    spec_s = fft_hp_filter(spec_s, bp['hpf_start'], bp['hpf_stop'] - 1)
            if bands_n == 1:
                wave = spectrogram_to_wave(spec_s, bp['hl'], mp, d, is_v51_model)
            else:
                wave = np.add(wave, spectrogram_to_wave(spec_s, bp['hl'], mp, d, is_v51_model))
        else:
            sr = mp['band'][d+1]['sr']
            if d == 1: # lower
                if is_v51_model:
                    spec_s *= get_lp_filter_mask(spec_s.shape[1], bp['lpf_start'], bp['lpf_stop'])
                else:
                    spec_s = fft_lp_filter(spec_s, bp['lpf_start'], bp['lpf_stop'])
                wave = librosa.resample(spectrogram_to_wave(spec_s, bp['hl'], mp, d, is_v51_model), bp['sr'], sr, res_type=wav_resolution)
            else: # mid
                if is_v51_model:
                    spec_s *= get_hp_filter_mask(spec_s.shape[1], bp['hpf_start'], bp['hpf_stop'] - 1)
                    spec_s *= get_lp_filter_mask(spec_s.shape[1], bp['lpf_start'], bp['lpf_stop'])
                else:
                    spec_s = fft_hp_filter(spec_s, bp['hpf_start'], bp['hpf_stop'] - 1)
                    spec_s = fft_lp_filter(spec_s, bp['lpf_start'], bp['lpf_stop'])
                    
                wave2 = np.add(wave, spectrogram_to_wave(spec_s, bp['hl'], mp, d, is_v51_model))
                wave = librosa.resample(wave2, bp['sr'], sr, res_type=wav_resolution)
        
    return wave


def get_lp_filter_mask(n_bins, bin_start, bin_stop):
    mask = np.concatenate([
        np.ones((bin_start - 1, 1)),
        np.linspace(1, 0, bin_stop - bin_start + 1)[:, None],
        np.zeros((n_bins - bin_stop, 1))
    ], axis=0)

    return mask
    
def get_hp_filter_mask(n_bins, bin_start, bin_stop):
    mask = np.concatenate([
        np.zeros((bin_stop + 1, 1)),
        np.linspace(0, 1, 1 + bin_start - bin_stop)[:, None],
        np.ones((n_bins - bin_start - 2, 1))
    ], axis=0)

    return mask