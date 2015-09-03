import math
import newton
import numpy as np
from plotter import Plotter
from splines import Spline2D

def makeSpline():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.0, 1.0, 1.0]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.0, 1.0, 1.0]
    coeffs = np.array([[[0.0,0.0], [0.1,0.2], [0.1,0.5], [0,0.9], [0.0,1.0]],
                       [[0.25,0.1], [0.1 ,0.2], [0.4,0.2], [0.5,0.9], [0.25,0.9]],
                       [[0.5,0.0], [0.5,0.2], [0.5,0.5], [0.6,0.9], [0.5,1.0]],
                       [[0.75,-0.05], [0.7,0.2], [0.8,0.5], [0.7,0.9], [0.75,0.9]],
                       [[1.0,0.0], [0.9,0.2], [0.8,0.5], [0.9,0.9], [1.0,1.0]]])
    
    return Spline2D(p, uKnots, vKnots, coeffs)
    
def spline():
    def s(v):
        return np.array([v, v+0.2])
    def ds(v):
        return np.array([1, 1])
    
    spline = makeSpline()
    splineInterval = [0, 0.99999]
    inOut = findInOut(spline, s, ds)
    
    plotter = Plotter()
    plotter.plotSurfaces(spline.evaluate, splineInterval, splineInterval, 10, 10)
    plotter.plotLine(s, [-10, 10])
    plotter.plotPoints(inOut)
    plotter.show()
    
def findInOut(spline, s, ds):
    '''
    spline - Spline2D object
    s - line function
    ds - first derivative of line function
    '''
    uGuess = 0.5
    vGuess = 0
    result = []
    
    def left(u):
        return spline.evaluate(0, u)
    def dleft(u):
        return spline.evaluatePartialDerivativeY(0, u)
    
    def top(u):
        return spline.evaluate(u, 0.99999)
    def dtop(u):
        return spline.evaluatePartialDerivativeX(u, 0.99999)
    
    def right(u):
        return spline.evaluate(0.99999, u)
    def dright(u):
        return spline.evaluatePartialDerivativeY(0.99999, u)
    
    def bottom(u):
        return spline.evaluate(u, 0)
    def dbottom(u):
        return spline.evaluatePartialDerivativeX(u, 0)
    
    uvIntersect = intersection2D(left, s, dleft, ds, uGuess, vGuess)
    result.append(s(uvIntersect[1]))
    
    uvIntersect = intersection2D(top, s, dtop, ds, uGuess, vGuess)
    result.append(s(uvIntersect[1]))

    return result
    
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

def intersection2D(f, g, df, dg, uGuess, vGuess):
    def h(u, v):
        return f(u) - g(v)
    
    def hJacob(u, v):
        return np.matrix([df(u), -dg(v)]).transpose()
    
    return newton.newtonsMethod2D(h, hJacob, uGuess, vGuess)
