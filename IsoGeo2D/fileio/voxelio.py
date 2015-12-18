import numpy as np
import os.path

def __filedir(dataset):
    return "textures/{},{}".format(dataset.rhoNumber, dataset.phiNumber)

def __filename(width, height):
    return "{}x{}.npy".format(width, height)

def __filepath(dataset, width, height):
    directory = __filedir(dataset)
    filename = __filename(width, height)
    return "{}/{}".format(directory, filename)
    
def exist(dataset, width, height):
    path = __filepath(dataset, width, height)
    return os.path.isfile(path)

def read(dataset, width, height):
    path = __filepath(dataset, width, height)
    return np.load(path)
    
def write(dataset, array):
    height = array.shape[0]
    width = array.shape[1]
    
    directory = __filedir(dataset)
    
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    path = __filepath(dataset, width, height)
    
    np.save(path, array)
