import newton
import numpy as np
from intersection import Intersection
from plotter import Plotter
from splines import Spline2D
from splines import SplinePlane

def makeSpline2D():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.0, 1.0, 1.0]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.0, 1.0, 1.0]
    coeffs = np.array([[[0.0,0.0], [0.1,0.2], [0.1,0.5], [0,0.9], [0.0,1.0]],
                       [[0.25,0.3], [0.11 ,0.4], [0.4,0.41], [0.5,0.9], [0.25,0.91]],
                       [[0.5,0.0], [0.5,0.2], [0.5,0.5], [0.6,0.9], [0.5,1.0]],
                       [[0.75,-0.09], [0.7,0.2], [0.8,0.5], [0.7,0.9], [0.75,0.91]],
                       [[1.0,0.0], [0.9,0.2], [0.81,0.5], [0.9,0.9], [1.0,1.0]]])
    
    return Spline2D(p, uKnots, vKnots, coeffs)

def makeSplinePlane():
    return SplinePlane(makeSpline2D(), [0, 0.99999])

def spline():
    def s(v):
        return np.array([v, -0.25*v+0.75])
    def ds(v):
        return np.array([1, -0.25])
    
    def hAtPoint(point):
        def h(u, v):
            return spline.evaluate(u, v) - point
        return h
    def hJacob(u, v):
        return np.matrix([spline.evaluatePartialDerivativeU(u, v), 
                          spline.evaluatePartialDerivativeV(u, v)]).transpose()

    
    spline = makeSpline2D()
    splineInterval = [0, 0.99999]
    splinePlane = SplinePlane(spline, splineInterval)
    
    plotter = Plotter()
    plotter.plotSurfaces(splinePlane.evaluate, splineInterval, splineInterval, 10, 10)
    plotter.plotLine(s, [-10, 10])
    plotter.draw()
    
    intersections = findIntersections(splinePlane, s, ds)
    
    inOutParamPoints = []
    inOutGeomPoints = []
    
    for intersection in intersections:
        inOutParamPoints.append(intersection.paramPoint)
        inOutGeomPoints.append(s(intersection.lineParam))
        
    plotter.plotIntersectionPoints(inOutGeomPoints)
    plotter.draw()
    
    inLineParam = intersections[0].lineParam
    outLineParam = intersections[1].lineParam
    
    sDelta = 0.005
    geomPoints = generateSamplePoints(s, inLineParam, outLineParam, sDelta)
    
    plotter.plotGeomPoints(geomPoints)
    plotter.draw()
    
    paramPoints = []
    prevUV = intersections[0].paramPoint
    
    for geomPoint in geomPoints:
        paramPoint = newton.newtonsMethod2DClamped(hAtPoint(geomPoint), hJacob, prevUV, splineInterval)

        paramPoints.append(paramPoint)
        prevUV = paramPoint

    plotter.plotParamPoints(paramPoints)
    plotter.draw()

def generateSamplePoints(f, begin, end, delta):
    result = []
    current = begin + delta
    
    while current < end:
        result.append(f(current))
        current += delta
        
    return result
    
def findIntersections(splinePlane, s, ds):
    result = []
    
    uv = intersection2D(splinePlane.left, s, splinePlane.dleft, ds, 0.5, 0)
    result.append(Intersection(np.array([0, uv[0]]), uv[1]))
    
    uv = intersection2D(splinePlane.right, s, splinePlane.dright, ds, 0.5, 0)
    result.append(Intersection(np.array([0.99999, uv[0]]), uv[1]))

    return np.asarray(result)

def intersection2D(f, g, df, dg, uGuess, vGuess):
    def h(u, v):
        return f(u) - g(v)
    
    def hJacob(u, v):
        return np.matrix([df(u), -dg(v)]).transpose()
    
    return newton.newtonsMethod2DClamped(h, hJacob, [uGuess, vGuess], [0, 0.99999])
