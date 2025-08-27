import glob
import threading

def typethis(a):
   print (a)

threads=[]
for i in range(10):
   t = threading.Thread(target=typethis , args=(i ))
   t.start()
   threads.append(t)
   
for t in threads:
   t.join()  #wait to execute all threads

print('done')

