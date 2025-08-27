# -*- coding: utf-8 -*-
import requests
from requests.adapters import HTTPAdapter
from urllib3 import Retry
import os

def requests_retry_session(
        retries=10,
        backoff_factor=0.3,
        status_forcelist=(500, 502, 504, 503),
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

def dl(url):               
   try:
         response = requests_retry_session().get(url, timeout=10)
         _str = response.text
         return _str
   except:
     return 'error'
   
def change_wallpaper():    
   url='https://www.bing.com/'           
   matn = dl(url)     
   if (matn!='error'):
       start_idx = 0
       end_idx =  len(matn) 
       idx = matn.index('href="/th?' , 0)
       ide = matn.index('.jpg' , idx+1)
       uu = url + matn[idx + 6 : ide] + '.jpg'
       r = requests.get(uu, allow_redirects=True)
       open('temp.jpg', 'wb').write(r.content)   
       import ctypes
       ctypes.windll.user32.SystemParametersInfoW(20, 0, os.path.abspath('temp.jpg'), 3)
       os.system('del %s' %('temp.jpg'))   
       
       
def links(url , filter_text=None):
    d = dl(url)
    x=[]
    idx=0
    while(idx>=0):
      try:  
       idx = d.index("href=" , idx+1)
       idy = d.index("\"" , idx+7)
       m = d[idx+6:idy]
       if (filter_text!=None):
           if (filter_text in m):
                x.append(m)
       else:
            x.append(m)        
      except:
        break
    return(x)    
    
def imgs(url , filter_text=None):
    d = dl(url)
    x=[]
    idx=0
    while(idx>=0):
      try:  
       idx = d.index("src=" , idx+1)
       idy = d.index("\"" , idx+6)
       m = d[idx+5:idy]
       if (filter_text!=None):
           if (filter_text in m):
                x.append(m)
       else:
            x.append(m)        
      except:
        break
    return(x)    
    
    
def save(url,filename):               
    try:
        response = requests.get(url, timeout=10)
        with open(filename, 'wb') as f:
            f.write(response.content)
        return 'Downloaded successfully!'
    except Exception as e:
        return 