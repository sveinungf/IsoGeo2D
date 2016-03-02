from scipy import interpolate
import numpy as np


def createTransferFunction():
    scalars = np.array([0.0, 1.0])

    colors = np.array([[1.0, 0.0, 0.0, 0.5],
                       [0.0, 0.0, 1.0, 0.5]])

    return interpolate.interp1d(scalars, colors, axis=0)
