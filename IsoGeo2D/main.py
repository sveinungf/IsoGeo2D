import newton
import numpy as np
import transfer as trans
from intersection import Intersection
from plotter import Plotter
from splines import Spline2D
from splines import SplinePlane

def createPhi():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.0, 1.0, 1.0]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.0, 1.0, 1.0]
    coeffs = np.array([[[0.0,0.0], [-0.1,0.2], [-0.1,0.5], [0,0.9], [0.0,1.0]],
                       [[0.25,-0.05], [0.11 ,0.4], [0.4,0.41], [0.5,0.9], [0.25,1.1]],
                       [[0.5,-0.06], [0.5,0.2], [0.5,0.5], [0.6,0.9], [0.5,1.0]],
                       [[0.75,-0.05], [0.7,0.2], [0.8,0.5], [0.7,0.9], [0.75,1.0]],
                       [[1.0,0.0], [1.01,0.2], [1.02,0.5], [1.05,0.9], [1.0,1.0]]])
    
    return Spline2D(p, uKnots, vKnots, coeffs)

def createRho():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.0, 1.0, 1.0]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.0, 1.0, 1.0]
    coeffs = np.array([[[0.35], [0.1], [0.1], [0.0], [0.0]],
                       [[0.25], [0.11], [0.4], [0.9], [1.0]],
                       [[0.5], [0.0], [0.3], [0.3], [0.5]],
                       [[0.75], [0.3], [0.2], [0.7], [0.75]],
                       [[0.5], [1.0], [1.0], [1.0], [0.8]]])
    
    return Spline2D(p, uKnots, vKnots, coeffs)

def run():
    splineInterval = [0, 0.99999]
    plotter = Plotter(splineInterval)
    
    phi = createPhi()
    phiPlane = SplinePlane(phi, splineInterval)
    plotter.plotSurfaces(phiPlane.evaluate, 10, 10)
    
    rho = createRho()
    transfer = trans.createTransferFunction(100)
    plotter.plotScalarField(rho, transfer)
    
    eye = np.array([-0.5, 0.5])
    pixels = []
    pixels.append(np.array([-0.2, 0.55]))
    pixels.append(np.array([-0.2, 0.45]))
    
    for pixel in pixels:
        viewDir = pixel - eye
        
        def s(t):
            return np.array([t+eye[0], viewDir[1]/viewDir[0]*t+eye[1]])
        def ds(t):
            return np.array([1, viewDir[1]/viewDir[0]])

        plotter.plotLine(s, [0, 10])
        plotter.draw()

        intersections = findIntersections(phiPlane, s, ds)
    
        inLineParam = intersections[0].lineParam
        outLineParam = intersections[1].lineParam
        
        inOutGeomPoints = []
        inOutGeomPoints.append(s(inLineParam))
        inOutGeomPoints.append(s(outLineParam))
        plotter.plotIntersectionPoints(inOutGeomPoints)
        plotter.draw()
    
        sDelta = 0.01
        geomPoints = generateSamplePoints(s, inLineParam, outLineParam, sDelta)
        plotter.plotGeomPoints(geomPoints)
        plotter.draw()
    
        paramPoints = []
        prevUV = intersections[0].paramPoint
    
        for geomPoint in geomPoints:
            def f(u,v):
                return phi.evaluate(u,v) - geomPoint
            def fJacob(u, v):
                return np.matrix([phi.evaluatePartialDerivativeU(u, v), 
                                  phi.evaluatePartialDerivativeV(u, v)]).transpose()
            
            paramPoint = newton.newtonsMethod2DClamped(f, fJacob, prevUV, splineInterval)

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
