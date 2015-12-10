import numpy as np


def write(dataset, array):
    height = array.shape[0]
    width = array.shape[1]
    
    filename = "voxel_{}x{}".format(width, height)
    path = "datasets/{}/{}".format(dataset, filename)
    
    np.save(path, array)
