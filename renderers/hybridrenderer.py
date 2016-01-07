import numpy as np

import colordiff
from comparerenderer import CompareRenderer, CompareSummary


class HybridRenderer(CompareRenderer):
    def __init__(self, delta, pixelPlot, diffPlot, refPixelColors, ratioPlot):
        super(HybridRenderer, self).__init__(delta, pixelPlot, diffPlot, refPixelColors)

        self.ratioPlot = ratioPlot

    def render(self, model, viewRays):
        numPixels = len(viewRays)
        pixelColors = np.zeros((numPixels, 4))
        ratios = np.zeros(numPixels)
        maxSamples = 0

        for i, viewRay in enumerate(viewRays):
            result = model.raycast(viewRay, self.delta)

            if result.color is not None:
                pixelColors[i] = result.color
                maxSamples = max(result.samples, maxSamples)

                ratios[i] = model.voxelRatio()

        colorDiffs = colordiff.compare(self.refPixelColors, pixelColors)

        if self.pixelPlot is not None:
            self.pixelPlot.plotPixelColors(pixelColors)

        if self.diffPlot is not None:
            self.diffPlot.plotPixelColorDiffs(colorDiffs)

        if self.ratioPlot is not None:
            self.ratioPlot.plotRatios(ratios)

        return CompareSummary(pixelColors, maxSamples, colorDiffs)
