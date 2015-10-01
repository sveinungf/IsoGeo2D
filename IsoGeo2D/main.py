import compositing
import itertools
import newton
import numpy as np
import transfer as trans
from boundingbox import BoundingBox
from plotter import Plotter
from ray import Ray2D
from samplingtag import SamplingTag
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

class Main:
    def __init__(self):
        self.splineInterval = [0, 0.99999]
        self.numPixels = 5
        self.samplingDefault = -1
        
        self.phi = createPhi()
        self.phiPlane = SplinePlane(self.phi, self.splineInterval, 0.00001)
        
        self.rho = createRho()
        self.transfer = trans.createTransferFunction(100)
        
        self.plotter = Plotter(self.splineInterval, self.numPixels)
        
        self.eye = np.array([-2, 0.55])
        
    def generateScalarTexture(self, boundingBox, width, height):
        phi = self.phi
        phiPlane = self.phiPlane
        rho = self.rho
        plotter = self.plotter
        
        rayCount = height
        samplingsPerRay = width
        
        xDelta = float(boundingBox.getWidth())/samplingsPerRay
        yDelta = float(boundingBox.getHeight())/rayCount
        
        xValues = np.linspace(boundingBox.left+xDelta/2, boundingBox.right-xDelta/2, samplingsPerRay)
        yValues = np.linspace(boundingBox.bottom+yDelta/2, boundingBox.top-yDelta/2, rayCount)
        
        samplingScalars = np.ones((rayCount, samplingsPerRay)) * self.samplingDefault    
        
        for i, y in enumerate(yValues):
            samplingRay = Ray2D(np.array([self.eye[0], y]), np.array([0, y]))
    
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
                                      
                paramPoint = newton.newtonsMethod2DClamped(f, fJacob, prevUV, self.splineInterval)
                paramPoints.append(paramPoint)
                
                scalar = rho.evaluate(paramPoint[0], paramPoint[1])
                samplingScalars[i][j] = scalar
                
                prevUV = paramPoint
                
            plotter.plotGeomPoints(geomPoints)
            plotter.plotParamPoints(paramPoints)
            plotter.draw()
            
        return Texture2D(samplingScalars)
    
    def raycast(self, viewRay, scalarTexture, textureBoundingBox):
        plotter = self.plotter
        
        viewRayDelta = 0.2
        samplePoints = viewRay.generateSamplePoints(0, 10, viewRayDelta)
        tags = []
        sampleColors = []
        sampleDeltas = []
        
        for samplePoint in samplePoints:
            bb = textureBoundingBox
            
            if bb.enclosesPoint(samplePoint):
                u = (samplePoint[0]-bb.left)/bb.getWidth()
                v = (samplePoint[1]-bb.bottom)/bb.getHeight()
                
                if not scalarTexture.closest([u, v]) == self.samplingDefault:
                    tags.append(SamplingTag.IN_TEXTURE)
                    
                    sampleScalar = scalarTexture.fetch([u, v])
                    sampleColors.append(self.transfer(sampleScalar))
                    sampleDeltas.append(viewRayDelta)
                else:
                    tags.append(SamplingTag.NOT_IN_TEXTURE)
            else:
                tags.append(SamplingTag.NOT_IN_BOUNDINGBOX)
            
        plotter.plotSamplePoints(samplePoints, tags)
        plotter.draw()
        
        return compositing.frontToBack(sampleColors, sampleDeltas) 
        
    def run(self):
        numPixels = self.numPixels
        plotter = self.plotter

        pixels = []
        pixelXs = [-0.5] * numPixels
        pixelYs = np.linspace(0.25, 0.85, numPixels)
        
        for pixelX,pixelY in itertools.izip(pixelXs,pixelYs):
            pixels.append(np.array([pixelX,pixelY]))
        
        plotter.plotGrids(self.phi.evaluate, 10, 10)
        plotter.plotScalarField(self.rho, self.transfer)
        plotter.draw()
        
        bb = self.phiPlane.createBoundingBox()
        plotter.plotBoundingBox(bb)
        plotter.draw()
        
        width = 10
        height = 10
        
        xDelta = float(bb.getWidth())/width
        yDelta = float(bb.getHeight())/height
        textureBoundingBox = BoundingBox(bb.left+xDelta/2, bb.right-xDelta/2, bb.bottom+yDelta/2, bb.top-yDelta/2)
        
        scalarTexture = self.generateScalarTexture(bb, width, height)
        
        plotter.plotSampleScalars(scalarTexture.textureData, bb)    
        plotter.plotScalarTexture(scalarTexture)
        plotter.draw()
        
        pixelColors = np.empty((numPixels, 4))
        
        for i, pixel in enumerate(pixels):
            viewRay = Ray2D(self.eye, pixel)
            plotter.plotViewRay(viewRay, [0, 10])
            
            pixelColors[i] = self.raycast(viewRay, scalarTexture, textureBoundingBox)
        
        plotter.plotPixelColors(pixelColors)
        plotter.draw()
    
def run():
    main = Main()
    main.run()

if __name__ == "__main__":
    run()
