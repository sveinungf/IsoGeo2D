import math
import numpy as np
from plotter import Plotter
from splines import Spline2D

def spline():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.1, 1.1, 1.1]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.1, 1.1, 1.1]
    coeffs = np.array([[[0.7,0.1], [0.8,0.2], [0.4,0.5], [0,0.9], [0.2,0.91]], [[0.7,0.1], [0.8,0.2], [0.2,0.2], [0,0.9], [0.2,0.91]], [[0.7,0.1], [0.8,0.2], [0.2,0.5], [0,0.9], [0.2,0.91]], [[0.7,0.1], [0.8,0.2], [0.2,0.5], [0,0.9], [0.2,0.91]], [[0.7,0.1], [0.8,0.2], [0.2,0.5], [0,0.9], [0.2,0.91]]])

    spline = Spline2D(p, uKnots, vKnots, coeffs)
    plotter = Plotter()
    
    plotter.plot(spline.evaluate)
    
def test():
    plotter = Plotter()
    plotter.plot(testFunction)
    
def testFunction(u, v):
    return [u*math.cos(v), math.sin(v)]
