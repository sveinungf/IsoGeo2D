import compositing
import newton
import numpy as np
import transfer as trans
from boundingbox import BoundingBox
from intersection import Intersection
from plotter import Plotter
from ray import Ray2D
from splines import Spline2D
from splines import SplinePlane

def createPhi():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.0, 1.0, 1.0]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.0, 1.0, 1.0]
    coeffs = np.array([[[0.0,0.0], [-0.1,0.2], [-0.2,0.5], [0,0.9], [0.0,1.0]],
                       [[0.25,-0.05], [0.11 ,0.4], [0.4,0.41], [0.5,0.9], [0.25,1.05]],
                       [[0.5,-0.06], [0.5,0.2], [0.5,0.5], [0.6,0.9], [0.5,1.03]],
                       [[0.75,-0.05], [0.7,0.2], [0.8,0.5], [0.7,0.9], [0.75,0.95]],
                       [[1.0,0.0], [1.01,0.2], [1.02,0.5], [1.05,0.7], [1.0,0.8]]])
    
    return Spline2D(p, uKnots, vKnots, coeffs)

def createRho():
    p = 2
    uKnots = [0, 0, 0, 0.2, 0.7, 1.0, 1.0, 1.0]
    vKnots = [0, 0, 0, 0.3, 0.6, 1.0, 1.0, 1.0]
    coeffs = np.array([[[0.6], [0.1], [0.6], [1.0], [1.0]],
                       [[0.25], [0.11], [1.0], [0.9], [1.0]],
                       [[0.5], [0.0], [0.3], [0.3], [0.5]],
                       [[0.75], [0.3], [0.0], [0.7], [0.75]],
                       [[0.5], [1.0], [1.0], [1.0], [0.8]]])
    
    return Spline2D(p, uKnots, vKnots, coeffs)

def run():
    splineInterval = [0, 0.99999]
    
    eyeX = -2
    pixelX = -0.4

    rayCount = 10
    samplingsPerRay = 10
    
    boundingBox = BoundingBox(1.0, 0.0, -0.2, 1.1)
    
    plotter = Plotter(splineInterval, rayCount)
    
    phi = createPhi()
    phiPlane = SplinePlane(phi, splineInterval)
    plotter.plotGrids(phiPlane.evaluate, 10, 10)
    
    rho = createRho()
    transfer = trans.createTransferFunction(100)
    plotter.plotScalarField(rho, transfer)
    
    plotter.plotBoundingBox(boundingBox)
    
    plotter.draw()
    
    samplingDefault = -1
    samplingScalars = np.ones((rayCount, samplingsPerRay)) * samplingDefault
    
    xDelta = float(boundingBox.getWidth())/samplingsPerRay
    yDelta = float(boundingBox.getHeight())/rayCount
    
    xValues = np.linspace(boundingBox.left+xDelta/2, boundingBox.right-xDelta/2, samplingsPerRay)
    yValues = np.linspace(boundingBox.bottom+yDelta/2, boundingBox.top-yDelta/2, rayCount)    
    
    for i, y in enumerate(yValues):
        eye = np.array([eyeX, y])
        pixel = np.array([pixelX, y])
        ray = Ray2D(eye, pixel)

        plotter.plotRay(ray, [0, 10])
        plotter.draw()
        
        intersections = findIntersections(phiPlane, ray)
        
        if intersections == None:
            continue
        
        inLineParam = intersections[0].lineParam
        outLineParam = intersections[1].lineParam
        
        inGeomPoint = ray.eval(inLineParam)
        outGeomPoint = ray.eval(outLineParam)

        plotter.plotIntersectionPoints([inGeomPoint, outGeomPoint])
        plotter.draw()
        
        geomPoints = []
        paramPoints = []
        
        prevUV = intersections[0].paramPoint
        
        for j, x in enumerate(xValues):
            if x < inGeomPoint[0] or x > outGeomPoint[0]:
                continue
            
            geomPoint = np.array([x, y])
            geomPoints.append(geomPoint)

            def f(u,v):
                return phi.evaluate(u,v) - geomPoint
            def fJacob(u, v):
                return np.matrix([phi.evaluatePartialDerivativeU(u, v), 
                                  phi.evaluatePartialDerivativeV(u, v)]).transpose()
                                  
            paramPoint = newton.newtonsMethod2DClamped(f, fJacob, prevUV, splineInterval)
            paramPoints.append(paramPoint)
            
            scalar = rho.evaluate(paramPoint[0], paramPoint[1])
            samplingScalars[i][j] = scalar
            
            prevUV = paramPoint
            
        plotter.plotGeomPoints(geomPoints)
        plotter.plotParamPoints(paramPoints)
        plotter.draw()
    
    samplingColors = np.empty((rayCount, samplingsPerRay, 4))
    
    for (i, j), scalar in np.ndenumerate(samplingScalars):
        if scalar == samplingDefault:
            samplingColors[i][j] = [0] * 4
        else:
            samplingColors[i][j] = transfer(scalar)
         
    plotSampleColors = True
    
    if plotSampleColors:
        plotter.plotSampleColors(samplingColors, boundingBox)
    else:    
        plotter.plotSampleScalars(samplingScalars, boundingBox)
        
    plotter.draw()
    
    pixelColors = np.empty((rayCount, 4))
    
    for i in range(len(samplingColors)):
        rayColors = samplingColors[i]
        pixelColors[i] = compositing.frontToBack(rayColors, xDelta)
    
    plotter.plotPixelColors(pixelColors)
    plotter.draw()

def generateSamplePoints(f, begin, end, delta):
    result = []
    current = begin + delta
    
    while current < end:
        result.append(f(current))
        current += delta
        
    return result
    
def findIntersections(splinePlane, ray):
    result = []
    s = ray.eval
    ds = ray.deval
    
    uvLeft = intersection2D(splinePlane.left, s, splinePlane.dleft, ds, 0.5, 0)
    uvTop = intersection2D(splinePlane.top, s, splinePlane.dtop, ds, 0.5, 0)
    uvRight = intersection2D(splinePlane.right, s, splinePlane.dright, ds, 0.5, 0)
    uvBottom = intersection2D(splinePlane.bottom, s, splinePlane.dbottom, ds, 0.5, 0)
    
    if uvLeft != None:
        result.append(Intersection(np.array([0, uvLeft[0]]), uvLeft[1]))
        
    if uvTop != None:
        result.append(Intersection(np.array([0.99999, uvTop[0]]), uvTop[1]))
        
    if uvRight != None:
        result.append(Intersection(np.array([0.99999, uvRight[0]]), uvRight[1]))
        
    if uvBottom != None:
        result.append(Intersection(np.array([0, uvBottom[0]]), uvBottom[1]))

    if len(result) < 2:
        return None
        
    if result[0].lineParam < result[1].lineParam:
        return np.asarray(result)
    else:
        return np.asarray([result[1], result[0]])

def intersection2D(f, g, df, dg, uGuess, vGuess):
    def h(u, v):
        return f(u) - g(v)
    
    def hJacob(u, v):
        return np.matrix([df(u), -dg(v)]).transpose()
    
    return newton.newtonsMethod2DClamped(h, hJacob, [uGuess, vGuess], [0, 0.99999])

if __name__ == "__main__":
    run()
