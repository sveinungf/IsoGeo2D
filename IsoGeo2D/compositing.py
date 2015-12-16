import itertools
import numpy as np

def frontToBack(rgbaValues, deltas):
    dst = np.zeros(4)
    
    for rgba, delta in itertools.izip(rgbaValues, deltas):
        dst = accumulate(dst, rgba, delta)
    
        if dst[3] >= 1.0:
            break
        
    return dst

def accumulate(dst, src, delta):
    xi = 1.0
    
    t = (1 - src[3])**(delta/xi)
    factor = (1 - t)*(1 - dst[3])
    
    dst[:3] += factor * src[:3]
    dst[3] += factor
    
    return dst
