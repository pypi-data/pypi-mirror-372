from matplotlib import pyplot as plt
from sklearn.manifold import TSNE
import numpy as np

def plot(fea , lab):
  lab= np.array(lab)
  fea = np.array(fea)
  if (len(np.shape(fea))==1):
      fea =fea.reshape(-1, 1)
      
  tsne = TSNE(n_components=2, random_state=0)

  X_2d = tsne.fit_transform(fea)
  
  for i in range(max(lab)+1):
    plt.scatter(X_2d[lab == i, 0], X_2d[lab == i,1])
  plt.show()  

