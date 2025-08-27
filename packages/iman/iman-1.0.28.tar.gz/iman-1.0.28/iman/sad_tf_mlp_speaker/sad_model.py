import torch
import torch.nn as nn
import torch.nn.functional as F




class SAD_INA_MODEL(nn.Module):
    def __init__(self):
        super(SAD_INA_MODEL, self).__init__()
        
        self.conv2d_12 = nn.Conv2d(1, 64, (7,4) )   ####(7,4) with nmel==21
        self.conv2d_13 = nn.Conv2d(64, 128, (3,3))
        self.conv2d_14 = nn.Conv2d(128, 128, (3,3))
        self.conv2d_15 = nn.Conv2d(128, 256, (3,3))
               
        self.dense_6   = nn.Linear(256,256)
        self.dense_7   = nn.Linear(256,256)
        self.dense_8   = nn.Linear(256,256)
        self.dense_9   = nn.Linear(256,256)
        self.dense_10   = nn.Linear(256,3)
        
        self.flatten_2   = nn.Flatten()
               
        self.batch_normalization_15 = nn.BatchNorm2d(64)
        self.batch_normalization_16 = nn.BatchNorm2d(128)
        self.batch_normalization_17 = nn.BatchNorm2d(128)
        self.batch_normalization_18 = nn.BatchNorm2d(256)      
        self.batch_normalization_19 = nn.BatchNorm1d(256)
        self.batch_normalization_20 = nn.BatchNorm1d(256)
        self.batch_normalization_21 = nn.BatchNorm1d(256)
        self.batch_normalization_22 = nn.BatchNorm1d(256)

    
    def forward(self, x):
        

        out = x.view(x.size(0),-1,x.size(1),x.size(2))
         
        # print( '1-->' + str (out.size()))
        
        out = (self.conv2d_12(out))
        out = self.batch_normalization_15(out)
        out = F.relu(out)
        out = F.max_pool2d(out, (4,2) , padding=(1,0))

        # print( '2-->' + str (out.size()))
        
        out = (self.conv2d_13(out))
        out =  self.batch_normalization_16 (out)
        out = F.relu(out)
  
        # print( '3-->' + str (out.size()))
        
        out = (self.conv2d_14(out))
        out = self.batch_normalization_17 (out)
        out = F.relu(out)
        out = F.max_pool2d(out, (2,2) , padding=(0,1))
        
        # print( '4-->' + str (out.size()))
        
        out = (self.conv2d_15(out))
        out =  self.batch_normalization_18 (out)
        out = F.relu(out)
        out = F.max_pool2d(out, (4,1))

        # print( '5-->' + str (out.size()))
        
        out = self.flatten_2 (out)
        
        # print( '6-->' + str (out.size()))
        
        out =  (self.dense_6(out))
        out =  self.batch_normalization_19 (out)
        out = F.relu(out)
        out = F.dropout(out)
        
        # print( '7-->' + str (out.size()))
        # quit()        
        out =  (self.dense_7(out))
        out =  self.batch_normalization_20 (out)
        out = F.relu(out)
        out = F.dropout(out)
        
        out =  (self.dense_8(out))
        out =  self.batch_normalization_21 (out)
        out = F.relu(out)
        out = F.dropout(out)
        
        out =  (self.dense_9(out))
        out =  self.batch_normalization_22 (out)
        out = F.relu(out)
        out = F.dropout(out)
        
        out =  F.softmax(self.dense_10(out), dim=1)
       
        return out
    
