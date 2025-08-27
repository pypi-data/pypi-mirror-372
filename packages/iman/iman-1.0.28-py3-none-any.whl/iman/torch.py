from torch import nn


def param(model):
    return(sum(p.numel() for p in model.parameters()) , sum(p.numel() for p in model.parameters() if p.requires_grad))
    
    
def paramp(model):
    from prettytable import PrettyTable
    table = PrettyTable(["Modules", "Parameters"])
    total_params = 0
    for name, parameter in model.named_parameters():
        if not parameter.requires_grad:
            continue
        params = parameter.numel()
        table.add_row([name, params])
        total_params += params
    print(table)
    print(f"Total Trainable Params: {total_params}")
    return total_params

def layers(model):
    children = list(model.children())
    return [model] if len(children) == 0 else [ci for c in children for ci in layers(c)]
    

def gpu():
    import torch
    x = torch.cuda.is_available()  
    print(x)
    return(x)

def gpun():
    import torch
    num_of_gpus =   torch.cuda.device_count()  
    print('Number of GPUs Available: ', num_of_gpus)    
    for i in range(num_of_gpus):
        print('GPU ', i, ' : ', torch.cuda.get_device_name(i))
    return num_of_gpus
    
    
def flops(model , dummy_input ):
     from thop import profile
     _flops, _params = profile(model, inputs=(dummy_input,))
     print(f"FLOPs: {_flops / 1e9:.2f} GFLOPs")  # Convert to Giga FLOPs
     return (_flops / 1e9)
          
