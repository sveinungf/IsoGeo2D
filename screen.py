import numpy as np


class Screen:
    def __init__(self, x, yTop, yBottom, numPixels):
        self.x = x
        self.yTop = yTop
        self.yBottom = yBottom
        self.numPixels = numPixels

        pixels = np.empty((numPixels, 2))
        pixelXs = np.ones(numPixels) * x

        deltaY = (yTop - yBottom) / numPixels
        firstPixelY = yBottom + (deltaY/2.0)
        lastPixelY = yTop - (deltaY/2.0)

        pixels[:, 0] = pixelXs
        pixels[:, 1] = np.linspace(firstPixelY, lastPixelY, numPixels)

        self.pixels = pixels
        self.pixelWidth = float(yTop - yBottom) / numPixels
