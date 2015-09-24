import numpy as np

def frontToBack(rgbaValues):
    delta = 1.0
    xi = 20
    
    dst = np.zeros(4)
    
    for rgba in rgbaValues:        
        t = (1 - rgba[3])**(delta/xi)
        factor = (1 - t)*(1 - dst[3])
        dst[:3] += factor * rgba[:3]
        dst[3] += factor
    
        if dst[3] >= 1.0:
            break
        
    return dst
