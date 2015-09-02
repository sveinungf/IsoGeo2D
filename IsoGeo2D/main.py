import math
import numpy as np
from plotter import Plotter
from splines import Spline2D

def makeSpline():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.01, 1.01, 1.01]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.01, 1.01, 1.01]
    coeffs = np.array([[[0.0,0.0], [0.1,0.2], [0.1,0.5], [0,0.9], [0.0,1.0]],
                       [[0.25,0.0], [0.1 ,0.2], [0.4,0.2], [0.5,0.9], [0.25,1.0]],
                       [[0.5,0.0], [0.5,0.2], [0.5,0.5], [0.6,0.9], [0.5,1.0]],
                       [[0.75,0.0], [0.7,0.2], [0.8,0.5], [0.7,0.9], [0.75,1.0]],
                       [[1.0,0.0], [0.9,0.2], [0.8,0.5], [0.9,0.9], [1.0,1.0]]])
    
    return Spline2D(p, uKnots, vKnots, coeffs)
    
def spline():
    spline = makeSpline()
    plotter = Plotter()
    
    plotter.plot(spline.evaluate, 10, 10)
    
def test1():
    def f(u, v):
        return [u**2, v]
    
    plotter = Plotter()
    plotter.plot(f, 10, 10)
    
def test2():
    def f(u, v):
        return [u*math.cos(v), math.sin(v)]
    
    plotter = Plotter()
    plotter.plot(f, 10, 10)
