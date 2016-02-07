import numpy as np

from field import Field


class TrivialField(Field):
    def __init__(self):
        super(TrivialField, self).__init__()

    def evaluate(self, u, v):
        return np.array([v])
