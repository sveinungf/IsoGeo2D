import numpy as np
from skimage import color

def convertToLabs(rgbas):
    labs = np.empty((len(rgbas), 3))
    
    for i, rgba in enumerate(rgbas):
        rgb = rgba[:3]
        floatRgb = rgb * 2.0 - 1.0
        arg = np.array([[floatRgb]], dtype=np.float)
        labs[i] = color.rgb2lab(arg)
        
    return labs
    
def compare(referenceRgbas, comparisonRgbas):
    referenceLabs = convertToLabs(referenceRgbas)
    comparisonLabs = convertToLabs(comparisonRgbas)
    
    return color.deltaE_ciede2000(referenceLabs, comparisonLabs)
