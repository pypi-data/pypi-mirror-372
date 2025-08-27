from iman import *

def help():
   print('\nneed to install winrar\n')
   
   
def rar(fname , out="" , rar_path=r"C:\Program Files\WinRAR\winrar.exe"):

    if (out==""):
        out = PJ(PD(fname) , PN(fname))
    else:
        out =  PJ(PD(out) , PN(out))   
        
    command = '"%s" a -r "%s.rar" "%s" ' %(rar_path , out , fname)
    cmd(command)
     
def unrar(fname , out="" , rar_path=r"C:\Program Files\WinRAR\winrar.exe"):
    
    if (PE(fname)!=".rar"):
        print("Just Extract rar files")
        return
    if (out!=""):
       out = out + "\\"
       command = '"%s" x -ad -c- -cfg- -inul -o+ -y "%s" "%s" ' %(rar_path , fname , out)
    else:
        command = '"%s" x -ad -c- -cfg- -inul -o+ -y "%s"' %(rar_path , fname )  
    cmd(command)
  
   
def zip(fname , out="" , rar_path=r"C:\Program Files\WinRAR\winrar.exe"):

    if (out==""):
        out = PJ(PD(fname) , PN(fname))
    else:
        out =  PJ(PD(out) , PN(out))   
        
    command = '"%s" a -afzip -r "%s.zip" "%s" ' %(rar_path , out , fname)
    cmd(command)
   
def unzip(fname , out="" , rar_path=r"C:\Program Files\WinRAR\winrar.exe"):
    
    if (PE(fname)!=".zip"):
        print("Just Extract zip files")
        return
    if (out!=""):
       out = out + "\\"
       command = '"%s" x -ibck "%s" "%s" ' %(rar_path , fname , out)
    else:
         command = '"%s" x -ibck "%s"' %(rar_path , fname)  
    cmd(command)
   
   
   
   