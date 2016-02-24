from scipy import interpolate
import numpy as np


def createTransferFunction():
    scalars = np.array([0.0, 0.2, 0.25, 0.3, 0.58, 0.60, 0.61, 0.9, 0.95, 1.0])

    colors = np.array([[0.0, 0.0, 0.0, 0.0],
                       [0.0, 0.0, 0.0, 0.0],
                       [1.0, 0.0, 0.0, 0.5],
                       [0.0, 0.0, 0.0, 0.0],
                       [0.0, 0.0, 0.0, 0.0],
                       [0.0, 0.7, 0.9, 0.8],
                       [0.0, 0.0, 0.0, 0.0],
                       [0.0, 0.0, 0.0, 0.0],
                       [0.0, 0.0, 0.9, 0.18],
                       [0.0, 0.0, 1.0, 0.2]])

    return interpolate.interp1d(scalars, colors, axis=0)
