
from queue import Queue
import threading

q= Queue()


def worker():
    while True:  
         item = q.get()
        
         #train
        
         q.task_done()
         
threading.Thread(target=worker, daemon=True).start()




while(True):
     while (q.qsize()>5):
         time.sleep(1)  
         
     #create data
     
     q.put(data)
 
            
q.join()   