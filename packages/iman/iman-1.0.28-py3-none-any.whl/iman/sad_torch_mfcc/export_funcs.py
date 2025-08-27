#!/usr/bin/env python
# encoding: utf-8

# The MIT License

# Copyright (c) 2018 Ina (David Doukhan - http://www.ina.fr/)

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import pandas as pd
from pytextgrid.PraatTextGrid import PraatTextGrid, Interval, Tier
import os
import json

def seg2csv(lseg, fout=None):
    df = pd.DataFrame.from_records(lseg, columns=['labels', 'start', 'stop'])
    df.to_csv(fout, sep='\t', index=False)

def seg2textgrid1(lseg, fout=None):
    tier = Tier(name='inaSpeechSegmenter')
    for label, start, stop,_ in lseg:
        if (label=='noEnergy'):
            label=''
        tier.append(Interval(start, stop, label))
    ptg = PraatTextGrid(xmin=lseg[0][1], xmax=lseg[-1][2])
    ptg.append(tier)
    ptg.save(fout)


def seg2json(lseg)   :
    try:
        return(seg2json5(lseg))
    except:    
         return(seg2json4(lseg))




def seg2Info(lseg):
   
    
    x=[]
    nch=0
    for segs in lseg:
      f=0
      nch = nch+1
      data_list=[]
      if (segs!=-1):
        for y in segs:
           if (y[0]!='noEnergy'):
                 f = f + y[2] - y[1]

    
      data = {
                    'channel' : nch,
                    'speech': f
             }      
      x.append(data)              
    return(json.dumps(x))  
    

def seg2Gender_Info(lseg):
   
    
    x=[]
    nch=0
    for segs in lseg:
      f=0
      m=0
      nch = nch+1
      data_list=[]
      if (segs!=-1):
        for y in segs:
           if (y[0]!='noEnergy'):
             if (y[0] == "female"):
                 f = f + y[2] - y[1]
             elif(y[0] == "male"):
                   m = m + y[2] - y[1]              
               
    
      data = {
                    'channel' : nch,
                    'male': m,
                    'female': f
             }      
      x.append(data)              
    return(json.dumps(x))  

def seg2json5(lseg):
   
    
    x=[]
    nch=0
    for segs in lseg:
      nch = nch+1
      data_list=[]
      if (segs!=-1):
        for label, start, stop ,_,_ in segs:
           if (label!='noEnergy'):
             data = {
                    'startTime': start,
                    'endTime': stop,
                    'gender': label[0]
                   }
             data_list.append(data)   
      data = {
                    'channel' : nch,
                    'segments' : data_list
             }      
      x.append(data)              
    return(json.dumps(x))          
              
def seg2json4(lseg):
    
    x=[]
    nch=0
    for segs in lseg:
      nch = nch+1
      data_list=[]
      if (segs!=-1):
        for label, start, stop ,_ in segs:
           if (label!='noEnergy'):
             data = {
                    'startTime': start,
                    'endTime': stop,
                    'gender': label[0]
                   }
             data_list.append(data)   
      data = {
                    'channel' : nch,
                    'segments' : data_list
             }      
      x.append(data)              
    return(json.dumps(x)) 


    
    
def seg2aud(lseg , fout=None)   :
    try:
        seg2aud5(lseg , fout)
    except:    
          seg2aud4(lseg , fout)
          
def seg2aud5(lseg , fout=None):
    if (lseg==-1):
       return
    with open(fout , 'w') as fid:
      for label, start, stop ,_,_ in lseg:
           if (label!='noEnergy'):
              fid.write('%s\t%s\t%s\n' %(start , stop , label))
              
def seg2aud4(lseg , fout=None):
    if (lseg==-1):
       return
    with open(fout , 'w') as fid:
      for label, start, stop ,_ in lseg:
           if (label!='noEnergy'):
              fid.write('%s\t%s\t%s\n' %(start , stop , label))
              
def seg2textgrid(data , fout=None):
    ghabli=False  
    kh=[] 
    if (True):   
       kh.append('File type = "ooTextFile"\n')
       kh.append('Object class = "TextGrid"\n')
       kh.append('\n')
       kh.append('xmin = 0 \n')
       kh.append('xmax = %s \n' %(data[-1][2]))
       kh.append('tiers? <exists> \n')
       kh.append('size = 1 \n')
       kh.append('item []: \n')
       kh.append('    item [1]:\n')
       kh.append('        class = "IntervalTier" \n')
       kh.append('        name = "sen" \n')
       kh.append('        xmin = 0 \n')
       kh.append('        xmax = %s \n' %(data[-1][2]))
       kh.append('        intervals: size = %s \n' %(0))
       x=1
    
       if (float(data[0][1])>0):
           kh.append('        intervals [%s]:\n' %(x))
           kh.append('            xmin = 0\n')
           kh.append('            xmax = %s \n' %(data[0][1]))
           kh.append('            text = "" \n')
           x=x+1
       
    
       for i in range(len(data)):
             kh.append('        intervals [%s]:\n' %(x))
             if (ghabli):
                 kh.append('            xmin = %s \n' %(data[i-1][2]))
             else:
                 kh.append('            xmin = %s \n' %(data[i][1]))
             kh.append('            xmax = %s \n' %(data[i][2]))
             kh.append('            text = "%s" \n' %(data[i][0].strip()))
             x=x+1
             
             if (i+1 >= len(data)):
                break
            
             if (data[i][2] != data[i+1][1]):
                

              if (float(data[i+1][1]) - float(data[i][2]) > 0.5):
                 kh.append('        intervals [%s]:\n' %(x))
    
                 kh.append('            xmin = %s \n' %(data[i][2]))
                 kh.append('            xmax = %s \n' %(data[i+1][1]))
                 kh.append('            text = "" \n')
                 x=x+1
                 ghabli=False
              else:
                 ghabli=True
    
       
    kh[13] = ('        intervals: size = %s \n' %(kh[-4].strip().split(' ')[1].replace('[','').replace(']','').replace(':','')))
       
          
    with open(fout, mode='w') as fid:
        for line in kh:
            fid.write(line)                  