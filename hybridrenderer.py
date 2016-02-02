import numpy as np

from ray import Ray2D
from renderer import Renderer, RenderingResult


class HybridRenderingResult(RenderingResult):
    def __init__(self, colors, maxSamplePoints, ratios):
        super(HybridRenderingResult, self).__init__(colors, maxSamplePoints)
        self.ratios = ratios


class HybridRenderer(Renderer):
    def __init__(self, eye, screen):
        super(HybridRenderer, self).__init__(eye, screen)

    def render(self, model, delta, plotter=None):
        numPixels = self.screen.numPixels
        pixels = self.screen.pixels
        pixelWidth = self.screen.pixelWidth

        colors = np.zeros((numPixels, 4))
        maxSamplePoints = 0

        ratios = np.zeros(numPixels)

        for i, pixel, in enumerate(pixels):
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)

            if plotter is not None and self.plotViewRays:
                plotter.plotViewRay(viewRay, [0, 10])

            result = model.raycast(viewRay, delta, plotter)

            if result.color is not None:
                colors[i] = result.color
                maxSamplePoints = max(result.samples, maxSamplePoints)
                ratios[i] = model.voxelRatio()

        return HybridRenderingResult(colors, maxSamplePoints, ratios)
