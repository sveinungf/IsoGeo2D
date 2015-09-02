import math
import newton
import numpy as np
import pylab as plt
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

def f(u):
    return np.array([u, u**3])

def df(u):
    return np.array([1, 3*u**2])

def g(v):
    return np.array([v, -50*v+100])

def dg(v):
    return np.array([1, -50])

def h(u, v):
    return f(u) - g(v)

def hJacob(u, v):
    dfu = df(u)
    dgv = dg(v)
    return np.matrix([[dfu[0], -dgv[0]], [dfu[1], -dgv[1]]])

def testNewton():
    u = np.linspace(-10, 10, 100)
    v = np.linspace(-10, 10, 100)
    
    fxValues = []
    fyValues = []
    gxValues = []
    gyValues = []
    
    for i in range(len(u)):
        [fx,fy] = f(u[i])
        [gx,gy] = g(v[i])
        fxValues.append(fx)
        fyValues.append(fy)
        gxValues.append(gx)
        gyValues.append(gy)
        
        
    plt.plot(fxValues, fyValues)
    plt.plot(gxValues, gyValues)
    
    uGuess = 4
    vGuess = 4
    uvIntersect = newton.newtonsMethod2D(h, hJacob, uGuess, vGuess)
    [xIntersect, yIntersect] = f(uvIntersect[0])
    plt.plot(xIntersect, yIntersect, marker='x')
    
    plt.show()
