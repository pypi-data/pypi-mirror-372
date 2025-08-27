import numpy as np
from sklearn.metrics import roc_curve as rc
from iman import *
import Levenshtein as Lev
import scipy.spatial as sp


def help():
   print('\nneed <Levenshtein> and <sklearn>\n')


def cosine_distance(v1,v2):
  return sp.distance.cdist(v1, v2, 'cosine')
  

def compute_eer(fpr,tpr,thresholds):
    fnr = 1-tpr
    abs_diffs = np.abs(fpr - fnr)
    min_index = np.argmin(abs_diffs)
    eer = np.mean((fpr[min_index], fnr[min_index]))
    return eer, thresholds[min_index]  ,min_index

def compute_FR(x , fpr, tpr):
    abs_diffs = np.abs(fpr*100 - x)  
    minval = np.min(abs_diffs)  
    aaa = np.where(abs_diffs == minval)  
    min_index = aaa[0][len(aaa[0])-1]
    fr = 1 - tpr[min_index]
    return fr

def EER(y, y_pred, pos_label=1): 
   fpr, tpr, threshold = rc(np.array(y), np.array(y_pred), pos_label=pos_label)
   eer , th,t =  compute_eer(fpr,tpr,threshold)
   fnr = 1-tpr
   recall = tpr / (tpr+fnr) 
   pre = tpr / (tpr + fpr)  
   fm = (2*recall*pre)   /(recall+pre)
   print("fpr , fnr , threshold , eer , th,t , recall , pre,fm")
   return (fpr , fnr , threshold , eer , th,t , recall , pre,fm)   
 
def roc(y , y_pred , pos_label=1):
    fpr , fnr , threshold ,eer , th,_,_,_,_=  EER(y , y_pred , pos_label=pos_label) 
    plt.figure()
    plt.title('EER=' + F(eer,2) + '   th=' + F(th,5))
    plt.plot(threshold,fpr )
    plt.plot(threshold,fnr )
    plt.show()
    print("fpr , fnr , threshold , eer , th")
    return (fpr , fnr , threshold , eer , th)  


def cer(ref, hyp):
    ref = ref.replace(' ', '').replace('‌','')
    hyp = hyp.replace(' ', '').replace('‌','')
    return Lev.distance(ref, hyp)/len(ref)

def wer(ref, hyp):
    ref = ref.replace('‌','')
    hyp = hyp.replace('‌','')
    b = set(ref.split() + hyp.split())
    word2char = dict(zip(b, range(len(b))))
    w1 = [chr(word2char[w]) for w in ref.split()]
    w2 = [chr(word2char[w]) for w in hyp.split()]
    return Lev.distance(''.join(w1), ''.join(w2)) / len(ref.split())
    
def wer_list(ref_list , hyp_list):
    x=[]
    for i in range(len(ref_list)):
       x.append(wer(ref_list[i] , hyp_list[i]))
    return np.mean(x)   
    
def cer_list(ref_list , hyp_list):
    x=[]
    for i in range(len(ref_list)):
       x.append(cer(ref_list[i] , hyp_list[i]))
    return np.mean(x)    
    
    
def DER(ref_list , res_list , file_dur=-1 , sr=8000):
    """ input--> [ [st1,en1] , [st2 , en2] , ....   ]
        just for speech parts
        Output--> Miss , FA , DER , miss_points, fa_points
    """        
    
    if (file_dur==-1):
        file_dur = max(ref_list[-1][1] , res_list[-1][1])
    
    ref = np.zeros((int(file_dur*sr)))
    
    for a,b in ref_list:
        ref[int(sr * a) : int(sr*b)]=1
              
    res = np.zeros((int(file_dur*sr)))
    
    for a,b in res_list:
        res[int(sr * a) : int(sr*b)]=1
     
    
    _miss_points=[]
    _y=np.where(ref==1)[0] 
    for i in _y:
        if (res[i]==0):
            _miss_points.append(i)
    x = len(_miss_points)
    miss = x / file_dur 
    

    _fa_points=[]
    _y=np.where(res==1)[0] 
    for i in _y:
        if (ref[i]==0):
            _fa_points.append(i)
    x1 = len(_fa_points)
    fa = x1 / file_dur 
    
    _der =(x+x1)/file_dur
    

    return (miss , fa ,_der ,_miss_points,_fa_points)