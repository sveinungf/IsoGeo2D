import numpy as np


class Summary(object):
    def __init__(self, colors, maxSamples):
        self.colors = colors
        self.maxSamples = maxSamples

    def printData(self):
        print "max #S = {}".format(self.maxSamples)


class Renderer(object):
    def __init__(self, delta, pixelPlot):
        self.delta = delta
        self.pixelPlot = pixelPlot

    def render(self, model, viewRays):
        numPixels = len(viewRays)
        pixelColors = np.zeros((numPixels, 4))
        maxSamples = 0

        for i, viewRay in enumerate(viewRays):
            result = model.raycast(viewRay, self.delta)

            if result.color is not None:
                pixelColors[i] = result.color
                maxSamples = max(result.samples, maxSamples)

        if self.pixelPlot is not None:
            self.pixelPlot.plotPixelColors(pixelColors)

        return Summary(pixelColors, maxSamples)
