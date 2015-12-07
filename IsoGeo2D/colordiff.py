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
    
    return ColorDiffData(diff)

class ColorDiffData:
    def __init__(self, colordiffs):
        self.colordiffs = colordiffs
        
        self.max = np.amax(colordiffs)
        self.mean = np.mean(colordiffs)
        self.var = np.var(colordiffs)
    
    def printData(self):
        print "max  = {}".format(self.max)
        print "mean = {}".format(self.mean)
        print "var  = {}".format(self.var)
