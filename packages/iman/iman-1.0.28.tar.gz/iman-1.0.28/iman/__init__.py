import matplotlib.pyplot as plt
import time
from glob import glob as gf
import os
import numpy as np
from joblib import load,dump


def help():
    from iman import web
    x=web.dl(r'https://pypi.org/project/iman/')
    idx = x.index('class="project-description"')
    idy = x.index('</div>' , idx+1)
    y= (x[idx+29:idy].strip().replace('<span class="docutils literal">','<').replace('</span>','>').replace('</section>','').replace('<h2>','').replace('</h2>','').replace('<p>','').replace('</p>','').replace('<section id=from-iman-import>',''))
    

    while(True):
       try:
        idx=0
        idx = y.index('<section',idx+1)

        idy = y.index('>' , idx+1)

        y = y.replace(y[idx:idy+1] , '')
       except:
         break       
    print(y)
   
def clear():
    if os.name == 'nt':
        _ = os.system('cls')  
    else:
        _ = os.system('clear')
        
def now():
   return time.time()
     
def F(float_number , float_number_count = 2):
   _str=("{:." + str(float_number_count) +"f}").format(float_number)
   return(_str) 

def D(int_number , int_number_count = 3):
   _str=("{:0>" + str(int_number_count) +"d}").format(int(int_number))
   return(_str) 
   
def Write(_str,Filename):
   with open(Filename , 'w' , encoding='utf-8') as fid:
              fid.write(_str)    

def Write_List(MyList,Filename):
   with open(Filename , 'w' , encoding='utf-8') as fid:
        for x in MyList:
              fid.write(str(x) + '\n')    

def Write_Dic(MyDic,Filename):
   with open(Filename , 'w' , encoding='utf-8') as fid:
        for x,y in MyDic.items():
              fid.write(str(x) + '\t' + str(y) + '\n')                 
              
def Read(Filename):
    with open(Filename , 'r' , encoding='utf-8') as fid:
         return(fid.read())

def Read_Lines(Filename):
    with open(Filename , 'r' , encoding='utf-8') as fid:
         return([x.strip() for x in fid if (x.strip()!="")])    

def gfa(directory , ext="*.*"):
 fols = gf(directory)
 a=[]
 for _fol in fols: 
   [a.append(x) for x in gf(os.path.join(_fol , ext))]
   for root, dirs, files in os.walk(_fol):
      for dirname in dirs:
         _dir =os.path.join(root, dirname)         
         [a.append(x) for x in gf(os.path.join(_dir , ext))]           
 return a         

def ReadE(Filename):
    import pandas as pd
    pp = pd.read_excel(Filename , engine='openpyxl')
    return pp
    
def PB(filename):
   return os.path.basename(filename)    
         
def PD(filename):
   return os.path.dirname(filename)  
   
def PM(folname):
   return os.makedirs(folname , exist_ok=True)
       
def PN(filename):
   return os.path.basename(os.path.splitext(filename)[0])  

def PE(filename):
   return os.path.splitext(filename)[1]   

def PX(filename):
   return os.path.exists(filename)    
   
def PJ(*_segments):
   x=""
   for p in _segments:
      x = os.path.join(x,p)
   return x   
   
def PS(filename):
   return os.path.getsize(filename)  
   
def PA(filename):
   return os.path.abspath(filename)  
   
def RI(start_int , end_int , count=1):
   return np.random.randint(low=int(start_int), high=int(end_int), size=(count,))
   
def RF(start_float , end_float , count=1):
  return np.random.uniform(start_float, end_float , count)
  
def RS(Arr):
  np.random.shuffle(Arr)
  return Arr
  
def RC(Arr , _size=1):
   return np.random.choice(Arr , _size)


def LJ(job_file_name):
   return load(job_file_name)
   
def SJ(value , job_file_name):
   dump(value , job_file_name)   
   
def LN(np_file_name):
   return np.load(np_file_name) 
   
def SN(arr , np_file_name):
   return np.save(np_file_name , arr)   
   
def cmd(command , redirect=True):
  if (redirect):
   return os.popen(command).read()   
  else:
    os.system(command)  
    
    
def onehot(data, nb_classes):
    """Convert an iterable of indices to one-hot encoded labels."""
    targets = np.array(data).reshape(-1)
    return np.eye(nb_classes)[targets]
    
    
def exe(fname):
    cmd('pyinstaller --onefile ' + fname , False)    
    
def FWL(wavfolder , sr): #Get Audio Lenth Exist in this folder    
    files=gfa(wavfolder , '*.wav')
    n=0
    for filename in files:
         n=n+PS(filename)
    header=len(files)*44       
    print((n-header)/(sr*2*60*60))
    return  ((n-header)/(sr*2*60*60))       
    
    
def norm(vector):
   m = np.linalg.norm(vector)
   return (vector/m)   
   

def delete(pattern):
    files = gf(pattern)
    for fname in files:
       isFile = os.path.isfile(fname)
       isDirectory = os.path.isdir(fname)
       if (isFile):
           cmd('del /Q "%s"' %(fname) )  
       if (isDirectory):           
           cmd('rmdir /S/Q "%s"' %(fname) )    
       
       
def rename(fname , fout):
       cmd('move "%s" "%s"' %(fname , fout) )         
       
       
def separate(pattern,folout=None,model_path_folder=None):   #model_path_folder contain .th model of Dmucs
    files = gf(pattern)
    for fname in files:
        print(fname)
        if (folout):
            PM(folout)
            if (model_path_folder):
                cmd('python -m demucs.separate --repo "%s" -o "%s" "%s"' %(model_path_folder,folout,fname))  
            else:
                cmd('python -m demucs.separate -o "%s" "%s"' %(folout,fname))  
        else:
           if (model_path_folder):
                cmd('python -m demucs.separate --repo "%s" "%s"' %(model_path_folder,fname)) 
           else:
               cmd('python -m demucs.separate "%s"' %(fname))               


def dll(fname):
    text="from Cython.Distutils import build_ext\n"
    text+="from setuptools import Extension, setup\n"
    text+=('ext_modules = [Extension("%s", ["%s.py"])]\n' %(PN(fname),PN(fname)))
    text+="setup(\n"
    text+="    name='Test Program',\n"
    text+="    cmdclass={'build_ext': build_ext},\n"
    text+="    ext_modules=ext_modules,\n"
    text+=")\n"
    Write(text , "setup.py")
    cmd('python setup.py build_ext --inplace')
    delete('setup.py')    
    delete('build')    
    delete(PN(fname)+'.c')    
    
def get_hard_serial():
   x = cmd("vol c:",True)  
   return(x.split('\n')[1].split('is')[1].strip())   
   
def mute_mic():
   import win32api
   import win32gui
   WM_APPCOMMAND = 0x319
   APPCOMMAND_MICROPHONE_VOLUME_MUTE = 0x180000
   hwnd_active = win32gui.GetForegroundWindow()   
   win32api.SendMessage(hwnd_active, WM_APPCOMMAND, None, APPCOMMAND_MICROPHONE_VOLUME_MUTE)