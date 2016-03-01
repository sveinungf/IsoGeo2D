import numpy as np

import colordiff
from modeltype import ModelType


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

def createSummaries(fileHandler, dataset):
    result = []

    for i in range(ModelType._COUNT):
        result.append([])

    files = fileHandler.findAll()
    refObj = fileHandler.load(files[0])

    for i in range(1, len(files)):
        obj = fileHandler.load(files[i])

        colorDiffs = colordiff.compare(refObj.renderResult.colors, obj.renderResult.colors)
        summary = Summary(obj, colorDiffs)
        result[obj.modelType].append(summary)

    return result
