import numpy as np
from skimage import color

def convertToLabs(rgbas):
    labs = np.empty((len(rgbas), 3))
    
    for i, rgba in enumerate(rgbas):
        rgb = rgba[:3]
        arg = np.array([[rgb]], dtype=np.float)
        labs[i] = color.rgb2lab(arg)
        
    return labs
    
def compare(referenceRgbas, comparisonRgbas):
    referenceLabs = convertToLabs(referenceRgbas)
    comparisonLabs = convertToLabs(comparisonRgbas)
    
    n = len(comparisonLabs)
    m = len(referenceLabs) / n
    
    diff = np.zeros(n)
    
    for i in range(m):
        diff += color.deltaE_ciede2000(referenceLabs[i::m], comparisonLabs)
        
    diff /= m
    
    return diff
