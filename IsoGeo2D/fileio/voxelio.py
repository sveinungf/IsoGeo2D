import numpy as np
import os.path

def __filepath(dataset, width, height):
    filename = "voxel_{}x{}.npy".format(width, height)
    path = "datasets/{}/{}".format(dataset, filename)
    
    return path
    
def exist(dataset, width, height):
    path = __filepath(dataset, width, height)
    return os.path.isfile(path)

def read(dataset, width, height):
    path = __filepath(dataset, width, height)
    return np.load(path)
    
def write(dataset, array):
    height = array.shape[0]
    width = array.shape[1]
    
    path = __filepath(dataset, width, height)
    
    np.save(path, array)
