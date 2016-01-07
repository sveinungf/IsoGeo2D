import numpy as np

import colordiff
from renderer import Renderer, Summary


class CompareSummary(Summary):
    def __init__(self, colors, samples, colorDiffs):
        super(CompareSummary, self).__init__(colors, samples)

        self.colorDiffs = colorDiffs
        self.max = np.amax(colorDiffs)
        self.mean = np.mean(colorDiffs)
        self.var = np.var(colorDiffs)

    def printData(self):
        super(CompareSummary, self).printData()

        print "max    = {}".format(self.max)
        print "mean   = {}".format(self.mean)
        print "var    = {}".format(self.var)


class CompareRenderer(Renderer):
    def __init__(self, delta, pixelPlot, diffPlot, refPixelColors):
        super(CompareRenderer, self).__init__(delta, pixelPlot)

        self.diffPlot = diffPlot
        self.refPixelColors = refPixelColors

    def render(self, model, viewRays):
        summary = super(CompareRenderer, self).render(model, viewRays)

        colorDiffs = colordiff.compare(self.refPixelColors, summary.colors)

        if self.diffPlot is not None:
            self.diffPlot.plotPixelColorDiffs(colorDiffs)

        return CompareSummary(summary.colors, summary.maxSamples, colorDiffs)
