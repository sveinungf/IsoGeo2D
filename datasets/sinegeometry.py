import math
import numpy as np

from geometry import Geometry


class SineGeometry(Geometry):
    def __init__(self):
        super(SineGeometry, self).__init__()

        self.modifier = 0.4

    def min(self, axis):
        if axis == 0:
            return 0.0 - self.modifier
        else:
            return 0.0

    def max(self, axis):
        if axis == 0:
            return 1.0 + self.modifier
        else:
            return 1.0

    def evaluate(self, x, y):
        return np.array([x + self.modifier * math.sin(2 * math.pi * y), y])

    def evaluatePartialDerivativeU(self, x, y):
        return np.array([1.0, 0.0])

    def evaluatePartialDerivativeV(self, x, y):
        return np.array([self.modifier * 2 * math.pi * math.cos(2 * math.pi * y), 1.0])

    def jacob(self, u, v):
        return np.matrix([self.evaluatePartialDerivativeU(u, v),
                          self.evaluatePartialDerivativeV(u, v)]).transpose()
