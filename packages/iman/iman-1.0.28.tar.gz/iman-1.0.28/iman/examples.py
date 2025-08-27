from iman import *

x= cmd('conda info')
idx = x.index('active env location :')
idy=x.index('shell level' , idx)
p = PJ(x[idx+22:idy].strip() ,'Lib','site-packages','iman','examples_folder')

help_items = gf(PJ(p,'*.py'))

def read_lines(_path):
  lines=[]
  with open (_path ,'r' ,encoding='utf-8') as fid:
     for line in fid:
        lines.append(line.strip('\n'))
  return(lines)      
 
items =  [PN(x) for x in help_items]

def help(_str):
    for x in help_items:
          if (_str in PN(x)):
             print('')
             [print( y ) for y in read_lines(x)]
             print('')
             return
    return('Nothing Found')         



