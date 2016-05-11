import math
import numpy as np


def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def normalize(v):
    vmag = magnitude(v)
    return np.array([ v[i]/vmag  for i in range(len(v)) ])
