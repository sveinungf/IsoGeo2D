import math
import newton
import numpy as np
import pylab as plt
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

def testNewton(uGuess, vGuess):
    spline = makeSpline()
    
    def f(u):
        return spline.evaluate(0, u)
    def df(u):
        return spline.evaluatePartialDerivativeY(0, u)
    
    def g(u):
        return spline.evaluate(u, 0.99999)
    def dg(u):
        return spline.evaluatePartialDerivativeX(u, 0.99999)
    
    def s(v):
        return np.array([v, v+0.2])
    def ds(v):
        return np.array([1, 1])

    u = np.linspace(0, 0.99999, 1000)
    v = np.linspace(-10, 10, 100)
    
    fxValues = []
    fyValues = []
    gxValues = []
    gyValues = []
    sxValues = []
    syValues = []
    
    for uValue in u:
        [fx,fy] = f(uValue)
        [gx, gy] = g(uValue)
        fxValues.append(fx)
        fyValues.append(fy)
        gxValues.append(gx)
        gyValues.append(gy)
    
    for vValue in v:
        [sx, sy] = s(vValue)
        sxValues.append(sx)
        syValues.append(sy)
        
    plt.plot(fxValues, fyValues)
    plt.plot(gxValues, gyValues)
    plt.plot(sxValues, syValues)
    
    uvIntersect = intersection2D(f, s, df, ds, uGuess, vGuess)
    [xIntersect, yIntersect] = f(uvIntersect[0])
    plt.plot(xIntersect, yIntersect, marker='x')
    [xIntersect, yIntersect] = s(uvIntersect[1])
    plt.plot(xIntersect, yIntersect, marker='o')
    
    uvIntersect = intersection2D(g, s, dg, ds, uGuess, vGuess)
    [xIntersect, yIntersect] = g(uvIntersect[0])
    plt.plot(xIntersect, yIntersect, marker='x')
    [xIntersect, yIntersect] = s(uvIntersect[1])
    plt.plot(xIntersect, yIntersect, marker='o')
    
    plt.axis((-0.1, 1.1, -0.1, 1.1))
    
    plt.show()

def intersection2D(f, g, df, dg, uGuess, vGuess):
    def h(u, v):
        return f(u) - g(v)
    
    def hJacob(u, v):
        return np.matrix([df(u), -dg(v)]).transpose()
    
    return newton.newtonsMethod2D(h, hJacob, uGuess, vGuess)
