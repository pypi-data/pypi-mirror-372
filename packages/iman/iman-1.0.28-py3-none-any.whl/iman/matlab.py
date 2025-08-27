from iman import *
from scipy.io import savemat,loadmat

def np2mat(param , mat_file_name):
   mdic = {"param": np.array(param)}
   savemat(mat_file_name, mdic)
   
   
def dic2mat(param , mat_file_name):
   savemat(mat_file_name, param)
   
def mat2dic (mat_file_name):
   return loadmat(mat_file_name)   