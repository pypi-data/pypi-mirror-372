import multiprocessing
from iman import gpu_info
import psutil
from iman import *

      
def plot(fname='log.txt', delay=1):
    import time
    import sys
    print("cpu\tmemory\tgpu\tgpu-usage")
    try:
        while True:
            y = gpu()
            x = F(cpu()) + '\t' + F(memory()) + '\t' + y[1] + '\t' + y[2]
            print(x.strip(), end='\r')
            with open(fname, 'a') as ff:
                ff.write(x + '\n')
            time.sleep(delay)
    except KeyboardInterrupt:
        print("\nProcess interrupted by user. Exiting gracefully.")


def gpu():
   x = gpu_info.showUtilization().split('|')
   return([y.strip() for y in x if y.strip()!=""])

def cpu():
   cpu_usage = psutil.cpu_percent()
   return(cpu_usage)
   
def memory():
   mem_usage = psutil.virtual_memory()[3]/1000000000
   return(mem_usage)   
   
def get(backend='torch'):
 if (backend=='torch'):
  import torch
  device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
  if (str(device) == "cuda"):
     a = torch.cuda.get_device_properties(device)
     memory = a.total_memory*1e-9
     GPU_Name = a.name
     multi_processor_count=a.multi_processor_count  
  else:
    memory=0
    GPU_Name ='No GPU'
    multi_processor_count=0
    
  cpu_count  = multiprocessing.cpu_count()
  
  print('Device== ' + str(device))
  print('GPU Memory== ' + str(memory) + ' GB')
  print('GPU_Name== ' + str(GPU_Name))
  print('multi_processor_count== ' + str(multi_processor_count))
  print('CPU Count== ' + str(cpu_count))
  
  return({'device':str(device) , 'memory':memory , 'cpu_count':cpu_count , 'multi_processor_count':multi_processor_count , 'name':GPU_Name })  
 else:
   cpu_count  = multiprocessing.cpu_count()
   from tensorflow.python.client import device_lib
   import tensorflow as tf
   device = 'CPU'
   if (tf.test.is_gpu_available()):
      device = 'GPU'
   x = device_lib.list_local_devices()
   print('Device== ' + str(device))
   print('CPU Count== ' + str(cpu_count))
   print(x) 
   return(x)
    
