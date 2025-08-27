from torch.utils.tensorboard import SummaryWriter


class rep():
    def __init__(self,log_dir=None):
      self.log_dir=log_dir  
      self.writer = SummaryWriter(log_dir=log_dir)      


    def WS(self,_type , _name , value , itr):
       self.writer.add_scalar(_type + '/' + _name, value, itr)
       
    def WT(self,_type , _name , _str , itr):  
        self.writer.add_text(_type + '/' + _name, _str, itr)
        
    def WG(self,pytorch_model , example_input):
       self.writer.add_graph(pytorch_model,example_input)
       
    def WI(self,_type , _name , images , itr):
        import torchvision
        grid = torchvision.utils.make_grid(images)
        self.writer.add_image(_type + '/' + _name, grid, itr) 
        
    def WC(self):
       self.writer.close()    
      