import numpy as np

from geometry import Geometry


class TrivialGeometry(Geometry):
    def __init__(self):
        super(TrivialGeometry, self).__init__()

    def min(self, axis):
        return 0.0

    def max(self, axis):
        return 1.0

    def evaluate(self, u, v):
        return np.array([u, v])

    def evaluatePartialDerivativeU(self, u, v):
        return np.array([1.0, 0.0])

    def evaluatePartialDerivativeV(self, u, v):
        return np.array([0.0, 1.0])

    def jacob(self, u, v):
        return np.matrix([[1.0, 0.0], [0.0, 1.0]])
