import math
import numpy as np


def magnitude(v):
    return math.sqrt(sum(v[i]*v[i] for i in range(len(v))))

def normalize(v):
    vmag = magnitude(v)
    return np.array([ v[i]/vmag  for i in range(len(v)) ])


class Screen:
    def __init__(self, bottom, top, numPixels):
        self.bottom = bottom
        self.top = top
        self.numPixels = numPixels

        pixels = np.empty((numPixels, 2))
        dir = normalize(top - bottom)
        length = magnitude(top - bottom)
        delta = length / numPixels

        for i in range(numPixels):
            pixels[i] = bottom + dir*(i*delta + delta/2)

        self.pixels = pixels
        self.pixelWidth = delta
