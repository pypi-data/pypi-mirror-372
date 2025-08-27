from iman import * 
==================

1-plt

2-now() ``get time``

3-F ``format floating point``

4-D ``format int number``

5-Write_List(MyList,Filename)

6-Write_Dic(MyDic,Filename)

7-Read(Filename) ``read txt file``

8-Read_Lines(Filename) ``read txt file line by line and return list``

9-Write(_str,Filename)

10-gf(pattern) ``Get files in a directory``

11-gfa(directory_pattern , ext="*.*") ``Get Files in a Directory and SubDirectories``

12-ReadE(Filename) ``Read Excel files``

13-PM(dir) ``creat directory``

14-PB(fname) ``get basename``

15-PN(fname) ``get file name``

16-PE(fname) ``get ext``

17-PD(fname) ``get directory``

18-PS(fname) ``get size``

19-PJ(segments) ``Join Path``

20-clear() ``clear cmd``

21-os

22-np

23-RI(start_int , end_int , count=1) ``random int``

24-RF(start_float , end_float , count=1) ``random float``

25-RS(Arr) ``shuffle``

26-LJ(job_file_name)

27-SJ(value , job_file_name)

28-LN(np_file_name)

29-SN(arr , np_file_name)

30-cmd(command , redirect=True) ``Run command in CMD``

31-PX(fname) ``check existance of file``

32-RC(Arr , size=1) ``Random Choice``

33-onehot(data, nb_classes)

34-exe(pyfile) ``need pyinstaller``

35-FWL(wavfolder , sr) ``Get Folder Audio Length``

36-norm(vector) ``vector/magnitude(vector)``

37-delete(pattern) 

38-rename(fname , fout) 

39-separate(pattern,folout) ``separate vocal from music``

40-dll(fname) ``create a pyd file from py file``

41-get_hard_serial()

42-mute_mic() ``on and off microphone``

43-PA(fname) ``get abs path``

from iman import Audio 
======================
1-Read(filename,sr,start_from,dur,mono,ffmpeg_path,ffprobe_path) ``Read wav alaw and mp3 and others``

2-Resample(data , fs, sr)

3-Write(filename, data ,fs)

4-frame(y)

5-split(y)

6-ReadT(filename, sr , mono=True) ``Read and resample wav file with torchaudio``

7-VAD(y,top_db=40, frame_length=200, hop_length=80)

8-compress(fname_pattern , sr=16000 , ext='mp3' , mono=True ,ffmpeg_path='c:\\ffmpeg.exe' , ofolder=None, worker=4)

9-clip_value(wav) ``return clipping percentage in audio file``

10-WriteS(filename, data ,fs) ``Convert to Sterio``

from iman import info 
=====================

1-get() info about cpu and gpu ``need torch``

2-cpu() ``get cpu percentage usage``

3-gpu() ``get gpu memory usage``

4-memory() ``get ram usage GB``

5-plot(fname="log.txt" , delay=1)


from iman import metrics 
========================
1-EER(lab,score)

2-cosine_distance(v1,v2)

3-roc(lab,score)

4-wer(ref, hyp)

5-cer(ref, hyp)

6-wer_list(ref_list , hyp_list)

7-cer_list(ref_list , hyp_list)

8-DER(ref_list , res_list , file_dur=-1 , sr=8000) ``Detection Error Rate``

from iman import tsne 
=====================

1-plot(fea , label)

from iman import xvector 
========================
1-xvec,lda_xvec,gender = get(filename , model(model_path , model_name , model_speaker_num))


from iman import web 
====================
1-change_wallpaper()

2-dl(url)

3-links(url , filter_text=None)

4-imgs(url , filter_text=None)

from iman import matlab 
=======================
1-np2mat(param , mat_file_name)

2-dic2mat(param , mat_file_name)

3-mat2dic (mat_file_name)

from iman import Features
=========================
1- mfcc_fea,mspec,log_energy = mfcc.SB.Get(wav,sample_rate) ``Compute MFCC with speechbrain - input must read with torchaudio``

2-mfcc.SB.Normal(MFCC) ``Mean Var Normalization Utt with speechbrain``

3- mfcc_fea,log_energy = mfcc.LS.Get(wav,sample_rate,le=False) ``Compute MFCC with Librosa - input is numpy array``

4-mfcc.LS.Normal(MFCC , win_len=150) ``Mean Var Normalization Local 150 left and 150 right``

from iman import AUG  
====================
1-Add_Noise(data , noise , snr) 

2-Add_Reverb( data , rir) 

3-Add_NoiseT(data , noise , snr) ``(torchaudio)``

4-Add_ReverbT( data , rir) ``(torchaudio)``

5-mp3(fname , fout,sr_out,ratio,ffmpeg_path='c:\\ffmpeg.exe')

6-speed(fname,fout,ratio,ffmpeg_path='c:\\ffmpeg.exe')

7-volume(fname ,fout,ratio,ffmpeg_path='c:\\ffmpeg.exe')

from iman.[sad_torch_mfcc | sad_tf] import *
===============================================================================
seg = Segmenter(batch_size, vad_type=['sad'|'vad'] , sr=8000 , model_path="c:\\sad_model_pytorch.pth" , tq=1,ffmpeg_path='c:\\ffmpeg.exe',complete_output=False , device='cuda',input_type='file')  ``TORCH``

seg = Segmenter(batch_size, vad_type=['sad'|'vad'] , sr=16000 , model_path="c:\\keras_speech_music_noise_cnn.hdf5",gender_path="c:\\keras_male_female_cnn.hdf5",ffmpeg_path='c:\\ffmpeg.exe',detect_gender=False,complete_output=False,device='cuda',input_type='file') ``TensorFlow``

isig,wav,mfcc = seg(fname)  ``mfcc output Just in torch model`` 

nmfcc = filter_fea(isig , mfcc , sr , max_time) ``Just in torch model``

mfcc = MVN(mfcc) ``Just in torch model`` 

isig = filter_output(isig , max_silence ,ignore_small_speech_segments , max_speech_len ,split_speech_bigger_than)  ``Do when complete_output=False``

seg2aud(isig , filename)
  
seg2json(isig)   

seg2Gender_Info(isig)  

seg2Info(isig)    

wav_speech , wav_noise = filter_sig(isig , wav , sr) ``Get Speech and Noise Parts of file - Do when complete_output=False``

from sad_tf.segmentero import Segmenter ``to use onnx models - need to install onnxruntime``

from iman.sad_torch_mfcc_speaker import *
================================================
seg = Segmenter(batch_size, vad_type=['sad'|'vad'] , sr=8000 , model_path="c:\\sad_model_pytorch.pth" , max_time=120(sec) , tq=1,ffmpeg_path='c:\\ffmpeg.exe', device='cuda' , pad=False)  ``TORCH - max_time in second to split fea output``
mfcc, len(sec)  = seg(fname)   ``mfcc pad to max_time length if pad=True``

from iman.sad_tf_mlp_speaker import *
================================================
seg = Segmenter(batch_size, vad_type=['sad'|'vad'] , sr=8000 , model_path="sad_tf_mlp.h5" , max_time=120(sec) , tq=1,ffmpeg_path='c:\\ffmpeg.exe', device='cuda' , pad=False)  ``Tensorflow (small mlp model) - max_time in second to split fea output``
mfcc, len(sec)  = seg(fname)   ``mfcc pad to max_time length if pad=True``

from iman import Report   ``Tensorboard Writer``
==================================================
r=Report.rep(log_dir=None)

r.WS(_type , _name , value , itr)  ``Add_scalar``

r.WT(_type , _name , _str , itr)   ``Add_text``

r.WG(pytorch_model , example_input)   ``Add_graph``

r.WI(_type , _name , images , itr)   ``Add_image``

from iman import par
========================
if (__name__ == '__main__'):  
 
res = par.par(files , func , worker=4 , args=[])   ``def func(fname , _args): ...``

from iman import Image
=========================
Image.convert(fname_pattern ,ext ='jpg',ofolder=None , w=-1 , h=-1,level=100,  worker=4,ffmpeg_path='c:\\ffmpeg.exe')

Image.resize(fname_pattern ,ext ='jpg',ofolder=None , w=2 , h=2,  worker=4,ffmpeg_path='c:\\ffmpeg.exe') ``resize to 1/h and 1/w``

from iman import Boors
==========================
Boors.get(sahm)  ``get sahm info``

from iman import Text
=====================
norm = Text.normal("c:\\Replace_List.txt")

norm.rep(str)

norm.from_file(filename ,file_out=None)

from iman.num2fa import words
=============================
words(number)

from iman import examples
==========================
examples.items   ``get items in examples folder``

examples.help(topic)

from iman import Rar  
====================
1-rar(fname , out="" , rar_path=r"C:\\Program Files\\WinRAR\\winrar.exe") 

2-zip(fname , out="" , rar_path=r"C:\\Program Files\\WinRAR\\winrar.exe") 

3-unrar(fname , out="" , rar_path=r"C:\\Program Files\\WinRAR\\winrar.exe") 

4-unzip(fname , out="" , rar_path=r"C:\\Program Files\\WinRAR\\winrar.exe") 

from iman import Enhance
=========================
1-Enhance.Dereverb(pattern , out_fol , sr = 16000, batchsize=16 , device="cuda"  ,model_path=r"C:\\UVR-DeEcho-DeReverb.pth")

2-Enhance.Denoise(pattern , out_fol , sr = 16000, batchsize=16 , device="cuda"  ,model_path=r"C:\UVR-DeNoise-Lite.pth")

from iman.tf import *
=====================
1-flops(model)   ``get flops of tf model``

2-param(model)   ``return parameter number of tf model``

3-paramp(model)  ``return parameter number of tf model and print model layers``

4-gpu()    ``return True if available``

5-gpun()   ``return number of gpus``

6-limit()   ``Tf model only allocate as much GPU memory based on runtime allocations``

from iman.torch import *
========================
1-param(model)   ``return parameter number and trainable number of torch model``

2-paramp(model)  ``return parameter number of torch model and print model layers``

3-layers(model)  ``return layers of torch model``

4-gpu()    ``return True if available``

5-gpun()   ``return number of gpus``

from iman.yt import *
========================
1-dl(url)   ``Download youtube link``

2-list_formats(url)  ``return all available formats for yt link``

