import newton
import numpy as np
from plotter import Plotter
from splines import Spline2D
from splines import SplinePlane

def makeSpline2D():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.0, 1.0, 1.0]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.0, 1.0, 1.0]
    coeffs = np.array([[[0.0,0.0], [0.1,0.2], [0.1,0.5], [0,0.9], [0.0,1.0]],
                       [[0.25,0.3], [0.1 ,0.4], [0.4,0.4], [0.5,0.9], [0.25,0.9]],
                       [[0.5,0.0], [0.5,0.2], [0.5,0.5], [0.6,0.9], [0.5,1.0]],
                       [[0.75,-0.09], [0.7,0.2], [0.8,0.5], [0.7,0.9], [0.75,0.9]],
                       [[1.0,0.0], [0.9,0.2], [0.8,0.5], [0.9,0.9], [1.0,1.0]]])
    
    return Spline2D(p, uKnots, vKnots, coeffs)
    
def spline():
    def s(v):
        return np.array([v, 0.5*v+0.6])
    def ds(v):
        return np.array([1, 0.5])
    
    def hAtPoint(point):
        def h(u, v):
            return spline.evaluate(u, v) - point
        return h
    def hJacob(u, v):
        return np.matrix([spline.evaluatePartialDerivativeU(u, 0), 
                          spline.evaluatePartialDerivativeV(0, v)]).transpose()

    spline = makeSpline2D()
    splineInterval = [0, 0.99999]
    splinePlane = SplinePlane(spline, splineInterval)
    sDelta = 0.005
    inOutParams = findInOutParams(splinePlane, s, ds)
    
    samplePointsG = generateSamplePoints(s, inOutParams[0][1], inOutParams[1][1], sDelta)
    
    samplePointsP = []
    prevUV = inOutParams[0]
    
    for gPoint in samplePointsG:
        pPoint = newton.newtonsMethod2DClamped(hAtPoint(gPoint), hJacob, prevUV, splineInterval)
        samplePointsP.append(pPoint)
        prevUV = pPoint
        
    inOutPoints = []
    
    for inOutParam in inOutParams:
        inOutPoints.append(s(inOutParam[1]))
    
    plotter = Plotter()
    plotter.plotSurfaces(splinePlane.evaluate, splineInterval, splineInterval, 10, 10)
    plotter.plotLine(s, [-10, 10])
    plotter.plotSamplePointsInG(samplePointsG)
    plotter.plotIntersectionPoints(inOutPoints)
    plotter.plotSamplePointsInP(samplePointsP)
    plotter.show()

def generateSamplePoints(f, begin, end, delta):
    result = []
    current = begin + delta
    
    while current < end:
        result.append(f(current))
        current += delta
        
    return result
    
def findInOutParams(splinePlane, s, ds):
    result = []
    
    result.append(intersection2D(splinePlane.left, s, splinePlane.dleft, ds, 0.5, 0))
    result.append(intersection2D(splinePlane.top, s, splinePlane.dtop, ds, 0.5, 0))

    return result
    
    
def spline2():
    def s(v):
        return np.array([v, 0.2*v+0.1])
    def ds(v):
        return np.array([1, 0.2])
    
    splineInterval = [0, 0.99999]
    splinePlane = SplinePlane(makeSpline2D(), splineInterval)
    inOutParams = findInOutParams2(splinePlane, s, ds)
    inOutPoints = []
    
    for inOutParam in inOutParams:
        inOutPoints.append(s(inOutParam[1]))
    
    plotter = Plotter()
    plotter.plotSurfaces(splinePlane.evaluate, splineInterval, splineInterval, 10, 10)
    plotter.plotLine(s, [-10, 10])
    plotter.plotIntersectionPoints(inOutPoints)
    plotter.show()
    
    
def findInOutParams2(splinePlane, s, ds):
    '''
    spline - Spline2D object
    s - line function
    ds - first derivative of line function
    '''
    result = []

    result.append(intersection2D(splinePlane.left, s, splinePlane.dleft, ds, 0.5, 0))
    result.append(intersection2D(splinePlane.bottom, s, splinePlane.dbottom, ds, 0, 0))
    result.append(intersection2D(splinePlane.bottom, s, splinePlane.dbottom, ds, 0.5, 0))
    result.append(intersection2D(splinePlane.right, s, splinePlane.dright, ds, 0.5, 0))

    return result

def intersection2D(f, g, df, dg, uGuess, vGuess):
    def h(u, v):
        return f(u) - g(v)
    
    def hJacob(u, v):
        return np.matrix([df(u), -dg(v)]).transpose()
    
    return newton.newtonsMethod2DClamped(h, hJacob, [uGuess, vGuess], [0, 0.99999])
