from iman import *


def fun(fname , b):
    ffmpeg_command =  '%s -y -i "%s" -vf "scale=w=%s:h=%s" -compression_level %s "%s"' %(b[3] ,fname , b[0],b[1] ,b[5], PJ(b[4],PN(fname)+b[2]) )
    cmd(ffmpeg_command)
   
   
 
def convert (fname_pattern ,ext ='jpg',ofolder=None , w=-1 , h=-1,level=100,  worker=4,ffmpeg_path='c:\\ffmpeg.exe'): 
    
    if (not ext.startswith('.')):
       ext = '.' + ext    
       
    files = gf(fname_pattern) 
    

    
    if (len(files)==0):
        print('no File!!!')
        return
    
   
    if (ofolder==None):
        pp = input('It is better to set ofolder\n press y to continue conversion: ')
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
         pool.map(partial(fun, b=[w , h,ext , ffmpeg_path,ofolder,level]), files)     


def fun2(fname , b):
    ffmpeg_command =  '%s -y -i "%s" -vf "scale=iw/%s:ih/%s" "%s"' %(b[3] ,fname , b[0],b[1] , PJ(b[4],PN(fname)+b[2]) )
    cmd(ffmpeg_command)
   
   
 
def resize (fname_pattern ,ext ='jpg',ofolder=None , w=2 , h=2,  worker=4,ffmpeg_path='c:\\ffmpeg.exe'): 
    
    if (not ext.startswith('.')):
       ext = '.' + ext    
       
    files = gf(fname_pattern) 
    

    
    if (len(files)==0):
        print('no File!!!')
        return
    
   
    if (ofolder==None):
        pp = input('It is better to set ofolder\n press y to continue conversion: ')
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
         pool.map(partial(fun2, b=[w , h,ext , ffmpeg_path,ofolder]), files)     

