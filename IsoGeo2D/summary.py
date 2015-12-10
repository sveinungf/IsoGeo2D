import numpy as np

class Summary:
    def __init__(self, colordiffs, maxSamplePoints):
        self.colordiffs = colordiffs
        self.maxSamplePoints = maxSamplePoints
        
        self.max = np.amax(colordiffs)
        self.mean = np.mean(colordiffs)
        self.var = np.var(colordiffs)
        
    def printData(self):
        print "max #S = {}".format(self.maxSamplePoints)
        print "max    = {}".format(self.max)
        print "mean   = {}".format(self.mean)
        print "var    = {}".format(self.var)
