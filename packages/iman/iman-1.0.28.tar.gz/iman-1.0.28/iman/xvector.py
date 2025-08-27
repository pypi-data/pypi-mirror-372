from iman import *
from iman import Audio
from tensorflow.keras.models import Model
import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Conv1D,Input,BatchNormalization,Activation,Dropout,Dense,multiply
c=tf.compat.v1.GPUOptions()
c.polling_inactive_delay_msecs = 10
VAR2STD_EPSILON = 1e-12
import librosa
from scipy import signal
from joblib import  load


def help():
     print('Requirements:\n\ntensorflow-gpu==2.0.0\nlibrosa==0.6.0\nnumba=0.48.0\nscikit-learn==0.21.3\n')


def apply_lda(x , mean_path , lda_path):
    meanvec = np.load(mean_path)
    x_mean= x - meanvec
    lda = load(lda_path) 
    x_lda = lda.transform(x_mean)
    return x_lda


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
    mel_db = librosa.amplitude_to_db(mel_spec)

    # Time-axis first
    if time_first:
        mel_db = mel_db.T  # (t, n_mels)

    return mel_db

def wav2spec(wav, n_fft, win_length, hop_length, time_first=True):
    stft = librosa.stft(y=wav, n_fft=n_fft, hop_length=hop_length, win_length=win_length)
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

    # Decibel-scaled mel-spectrogram
    mel_db = wav2melspec_db(wav_preem, sr, n_fft, win_length, hop_length, n_mels, time_first=False, **kwargs)

    # MFCCs
    mfccs = np.dot(librosa.filters.dct(n_mfccs, mel_db.shape[0]), mel_db)


    # Time-axis first
    if time_first:
        mfccs = mfccs.T  # (t, n_mfccs)

    return np.asarray(mfccs , dtype = np.float32)

def linear_to_mel(linear, sr, n_fft, n_mels, **kwargs):
    mel_basis = librosa.filters.mel(sr, n_fft, n_mels, **kwargs)  # (n_mels, 1+n_fft//2)
    mel = np.dot(mel_basis, linear)  # (n_mels, t) # mel spectrogram
    return mel
def local_MVN_2(X , num):
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

def dovad(wav , maxlen):
    wav /= max(abs(wav)) 
    wav -= np.mean(wav)     
    vad = librosa.effects.split(wav, top_db=40, frame_length=int(200), hop_length=int(80))   
    isig = []
    for v in vad:
        isig.append(np.arange(*v))
    isig = np.concatenate(isig, axis=0)
    vadsig = wav[isig][0:maxlen*80]
    return vadsig

def get_fea_file(wave_path,sr=8000)    : 
     wav= dovad(wave_path,12000)
     speech_mfccs = wav2mfcc (wav , sr=sr)
     feat = local_MVN_2(speech_mfccs,150)
     return feat


def statistics_pooling(features):
    with tf.compat.v1.variable_scope("stat_pooling"):
        mean = tf.math.reduce_mean(features, axis=1, keepdims=True, name="mean")
        variance = tf.math.reduce_mean(tf.math.squared_difference(features, mean), axis=1, keepdims=True, name="variance")
        mean = tf.squeeze(mean, 1)
        variance = tf.squeeze(variance, 1)
        mask = tf.compat.v1.to_float(tf.less_equal(variance, VAR2STD_EPSILON))
        variance = (1.0 - mask) * variance + mask * VAR2STD_EPSILON
        stddev = tf.sqrt(variance)
        stat_pooling = tf.concat([mean, stddev], 1, name="concat")
    return stat_pooling

def cmg(classe_nums , dimension):

  inputs = Input((None,dimension))
  x = Conv1D(512, 5, padding='same', strides= 1, kernel_initializer = 'he_normal')(inputs)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)

  x = Conv1D(512, 5, padding='same', strides= 1, kernel_initializer = 'he_normal')(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = Dropout(0.3)(x)

  x = Conv1D(512, 7, padding='same', strides= 1, kernel_initializer = 'he_normal')(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = Dropout(0.3)(x)

  x = Conv1D(512, 1, padding='same', strides= 1, kernel_initializer = 'he_normal')(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = Dropout(0.3)(x)

  x = Conv1D(3*512, 1, padding='same', strides= 1, kernel_initializer = 'he_normal')(x)
  x = BatchNormalization()(x)
  x = Activation('relu')(x)
  x = Dropout(0.3)(x)


  x = statistics_pooling(x)

  out_xvec = Dense(512, name = 'x_vector')(x)  
  x = BatchNormalization(name='xvec_bn')(out_xvec)
  x = Activation('relu' ,name='xvec_activation')(x)
  
  y = Dense(512, name='gender_dense_1')(x)
  y = BatchNormalization(name='gender_bn_1')(y)
  y = Activation('relu' , name='gender_activation_1')(y)
  
  y = Dense(2 ,name='gender_dense_2')(y)
  y = BatchNormalization(name='gender_bn_2')(y)
  y = Activation('softmax' , name='out2')(y)
  
  x = Dense(512,name='spk_dense_1')(x)
  x = BatchNormalization(name='spk_bn_1')(x)
  x = Activation('relu' , name = 'spk_activation_1')(x)

  x = Dense(classe_nums,name='spk_dense_2')(x)
  x = BatchNormalization(name='spk_bn_2')(x)
  x = Activation('softmax' , name='out1')(x)

  model_train = Model(inputs, [x,y])
  model_test = Model(inputs, [out_xvec,y])
  return model_train , model_test

def get_model(model_path , model_name, speaker_num):
  _,modelxvec = cmg(speaker_num,24)
  modelxvec.load_weights(PJ(model_path ,model_name ))
  return modelxvec

def get_xvec(feat, modelxvec ,batch_size):
 
  xvec,gender = modelxvec.predict(feat, batch_size = batch_size,verbose=1,use_multiprocessing=True)
  return xvec,gender


def model(model_path , model_name , model_speaker_num):
    return [get_model(model_path , model_name , model_speaker_num) , model_path]

def get(filename , _model):
   sample_rate=8000
   data =Audio.Read(filename , sample_rate)
   fea = get_fea_file(data , sample_rate)
   xvec, a = get_xvec(np.reshape(fea , (1 , np.shape(fea)[0], np.shape(fea)[1])), _model[0], batch_size=1)
   xvec_lda = apply_lda(xvec, PJ(_model[1], 'meanvec.npy'), PJ(_model[1], 'lda.job'))
   gender='male'
   if (a[0][0]>=a[0][1]):
       gender='female'
   return(np.squeeze(xvec),np.squeeze(xvec_lda),gender)
   
   