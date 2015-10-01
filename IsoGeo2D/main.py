import compositing
import itertools
import newton
import numpy as np
import transfer as trans
from plotter import Plotter
from ray import Ray2D
from splineplane import SplinePlane
from splines import Spline2D
from texture import Texture2D

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
    
    eye = np.array([-2, 0.55])
    pixels = []
    numPixels = 3
    pixelXs = [-0.5] * numPixels
    pixelYs = np.linspace(0.85, 0.25, numPixels)
    
    for pixelX,pixelY in itertools.izip(pixelXs,pixelYs):
        pixels.append(np.array([pixelX,pixelY]))

    rayCount = 10
    samplingsPerRay = 10
    
    plotter = Plotter(splineInterval, rayCount)
    
    phi = createPhi()
    phiPlane = SplinePlane(phi, splineInterval, 0.00001)
    plotter.plotGrids(phi.evaluate, 10, 10)
    
    rho = createRho()
    transfer = trans.createTransferFunction(100)
    plotter.plotScalarField(rho, transfer)
    
    boundingBox = phiPlane.createBoundingBox()
    plotter.plotBoundingBox(boundingBox)
    
    plotter.draw()
    
    samplingDefault = -1
    samplingScalars = np.ones((rayCount, samplingsPerRay)) * samplingDefault
    
    xDelta = float(boundingBox.getWidth())/samplingsPerRay
    yDelta = float(boundingBox.getHeight())/rayCount
    
    xValues = np.linspace(boundingBox.left+xDelta/2, boundingBox.right-xDelta/2, samplingsPerRay)
    yValues = np.linspace(boundingBox.bottom+yDelta/2, boundingBox.top-yDelta/2, rayCount)    
    
    for i, y in enumerate(yValues):
        samplingRay = Ray2D(np.array([eye[0], y]), np.array([0, y]))

        plotter.plotSamplingRay(samplingRay, [0, 10])
        plotter.draw()
        
        intersections = phiPlane.findTwoIntersections(samplingRay)
        
        if intersections == None:
            continue
        
        inLineParam = intersections[0].lineParam
        outLineParam = intersections[1].lineParam
        
        inGeomPoint = samplingRay.eval(inLineParam)
        outGeomPoint = samplingRay.eval(outLineParam)

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
         
    plotSampleColors = False
    
    if plotSampleColors:
        plotter.plotSampleColors(samplingColors, boundingBox)
    else:    
        plotter.plotSampleScalars(samplingScalars, boundingBox)
        
    plotter.draw()
    
    for pixel in pixels:
        viewRay = Ray2D(eye, pixel)
        plotter.plotViewRay(viewRay, [0, 10])
        
        samplePoints = viewRay.generateSamplePoints(0, 10, 0.2)
        plotter.plotSamplePoints(samplePoints)
        plotter.draw()
    
    pixelColors = np.empty((rayCount, 4))
    
    scalarTexture = Texture2D(samplingScalars)
    plotter.plotScalarTexture(scalarTexture)
    plotter.draw()
    
    for i in range(len(samplingColors)):
        rayColors = samplingColors[i]
        pixelColors[i] = compositing.frontToBack(rayColors, xDelta)
    
    plotter.plotPixelColors(pixelColors)
    plotter.draw()

if __name__ == "__main__":
    run()
