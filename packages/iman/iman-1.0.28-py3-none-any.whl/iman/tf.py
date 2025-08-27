import tensorflow as tf
from tensorflow.python.framework.convert_to_constants import convert_variables_to_constants_v2

def cpu():
   import os
   os.environ["CUDA_DEVICE_ORDER"]= '-1'

def flops(model):
    # Convert the model
    full_model = tf.function(lambda x: model(x))
    full_model = full_model.get_concrete_function(
        tf.TensorSpec(model.inputs[0].shape, model.inputs[0].dtype))

    # Get the frozen ConcreteFunction
    frozen_func = convert_variables_to_constants_v2(full_model)
    frozen_func.graph.as_graph_def()

    # Calculate FLOPs with tf.profiler
    run_meta = tf.compat.v1.RunMetadata()
    opts = tf.compat.v1.profiler.ProfileOptionBuilder.float_operation()
    
    flops = tf.compat.v1.profiler.profile(graph=frozen_func.graph,
                                          run_meta=run_meta, cmd='op', options=opts)
    
    return flops.total_float_ops
    
    
def paramp(model):
    from prettytable import PrettyTable
    table = PrettyTable()
    table.field_names = ["Layer Type", "Output Shape", "Param #"]
    for layer in model.layers:
        table.add_row([layer.__class__.__name__, layer.output_shape, layer.count_params()])
    print(table)    
    return(model.count_params())    
    
def param(model):
    return(model.count_params())        
    
    
def gpu():
    x = tf.test.is_gpu_available()
    print(x)
    return(x)


def gpun():
    gpus =   tf.config.list_physical_devices('GPU')
    try:
      num_of_gpus = len(gpus)
      print('Number of GPUs Available: ', num_of_gpus)    
      return num_of_gpus
    except:
         print('No GPU')
         return 0         
    
    
def limit():  #only allocate as much GPU memory based on runtime allocations
     gpus = tf.config.experimental.list_physical_devices('GPU')
     if gpus:
       try:
          for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
       except RuntimeError as e:
            print(e)