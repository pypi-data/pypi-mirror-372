from multiprocessing import Pool
from functools import partial
d=[1,2,3,4,5,6,7,8,9]

def fun2(fname):
    print(fname)

def fun(dd,b):
   print(b[0])

if (__name__ == '__main__'):
  with Pool(processes=4) as pool:
     fea = pool.map(partial(fun, b=['Sons',8000]), d)
	 
  with Pool(processes=4) as pool:
       pool.map(fun , d)