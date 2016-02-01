import numpy as np

from ray import Ray2D


class RenderingResult:
    def __init__(self, colors, maxSamplePoints):
        self.colors = colors
        self.maxSamplePoints = maxSamplePoints


class Renderer:
    def __init__(self, eye, screen):
        self.eye = eye
        self.screen = screen

        self.plotViewRays = True

        self.maxSamplePoints = 0

    def render(self, model, delta, plotter=None):
        numPixels = self.screen.numPixels
        pixels = self.screen.pixels
        pixelWidth = self.screen.pixelWidth

        colors = np.zeros((numPixels, 4))
        maxSamplePoints = 0

        for i, pixel, in enumerate(pixels):
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)

            if plotter is not None and self.plotViewRays:
                plotter.plotViewRay(viewRay, [0, 10])

            result = model.raycast(viewRay, delta, plotter)

            if result.color is not None:
                colors[i] = result.color
                maxSamplePoints = max(result.samples, maxSamplePoints)

        return RenderingResult(colors, maxSamplePoints)
