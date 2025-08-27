from iman import *
import re
from  iman.num2fa import words

rep_nothing=['ّ' , 'ِ','َ','ُ','ء','ـ','ً']
rep_space=['!','،','؟','؛','–',',',';','	' , '(',')', '[',']', '{','}', '~','!', '@','#', '$','%', '^','&','*','>','<','»','«','/',':','...'  , '.']


def conv_horoof(_str):
    t = _str.split(':')
    t0 = words(int(t[0].strip()))
    t1 = words(int(t[1].strip()))
    return " " + t0 + " و " + t1 + " دقیقه "

def cr(_str):
   return _str.replace('ي','ی').replace('ك','ک').replace('ى','ی').replace('إ','ا').replace('أ','ا').replace('ؤ','و')
   
def cf(_str):
      _str=cr(_str)
      for g in rep_nothing:
            _str = _str.replace(g , '')
      for g in rep_space:
            _str = _str.replace(g , ' ')   
      return (_str)      

def cn(text):

     pattern=r'[0-9]+[:][0-9]+'        
     x = re.search(pattern, text) 
     while(x!=None):
       y = text[x.span(0)[0]:x.span(0)[1]]
       yy = conv_horoof(y)
       text = text[:x.span(0)[0]] + yy + text[x.span(0)[1]:] 
       x = re.search(pattern, text) 
       
     pattern=r'[+-]?([0-9]*[.])?[0-9]+'    
     x = re.search(pattern, text) 
     while(x!=None):
       y = text[x.span(0)[0]:x.span(0)[1]]
       print(y)
       yy = " "  + words(y) + " "
       text = text[:x.span(0)[0]] + yy + text[x.span(0)[1]:] 
       x = re.search(pattern, text)  

    

     return text       
  

def getd(replist):
   mwords=[]
   words=[]
   ph=[]

   with open(replist , encoding='utf-8') as fr:
      for line in fr:
          t = cr(line).split('\t')
          mwords.append(t[0])
          words.append(t[1])
          ph.append(t[2].strip())
   return(mwords,words,ph)       
   
   
class normal():
  def __init__(self,replist='c:\\Replace_List.txt'):
    self.replist=replist
    self.mwords,self.words,self.ph = getd(replist) 
    
  def rep(self , _str):
     _str= cf(cn(_str))
     for i in range(len(self.words)):
       if (self.words[i] in _str):
           pattern = "(^|\s)" + self.words[i] + "($|\s)"
           _str = re.sub(pattern ," " + self.mwords[i] + " " ,  _str)
       if (self.ph[i] in _str):
           pattern = "(^|\s)" + self.ph[i] + "($|\s)"
           _str = re.sub(pattern ," " + self.mwords[i] + " " ,  _str)
                 
     return(_str.strip())  

  def from_file(self , filename ,file_out=None):

   matn  = Read(filename)

   if (file_out==None):
       file_out= PN(filename) + '_normal' + PE(filename)
   fid = open(file_out , 'w',encoding='utf-8')
   fid.write(self.rep(matn)) 
   fid.close()    

