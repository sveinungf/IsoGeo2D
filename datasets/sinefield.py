import math
import numpy as np

from field import Field


class SineField(Field):
    def __init__(self):
        super(SineField, self).__init__()

    def evaluate(self, u, v):
        a = 0.5 + 0.5 * math.sin(2 * math.pi * u)
        b = 0.5 + 0.5 * math.sin(2 * math.pi * v)

        return np.array([a * b])
