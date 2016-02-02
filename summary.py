import numpy as np


class Summary:
    def __init__(self, renderData, colorDiffs):
        self.renderData = renderData

        self.max = np.amax(colorDiffs)
        self.mean = np.mean(colorDiffs)
        self.var = np.var(colorDiffs)

    def printData(self):
        print "{}".format(self.renderData.name)
        print "---------------------"
        print "max #S = {}".format(self.renderData.renderResult.maxSamplePoints)
        print "max    = {}".format(self.max)
        print "mean   = {}".format(self.mean)
        print "var    = {}".format(self.var)
