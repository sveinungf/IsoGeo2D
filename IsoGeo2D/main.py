import colordiff
import compositing
import itertools
import newton
import numpy as np
import transfer as trans
from plotter import Plotter
from ray import Ray2D
from samplinglocation import SamplingLocation
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
        self.numPixelsRef = 5
        self.pixelX = -0.5
        self.firstPixelY = 0.25
        self.lastPixelY = 0.85
        
        self.samplingDefault = -1
        
        self.phi = createPhi()
        self.phiPlane = SplinePlane(self.phi, self.splineInterval, 0.00001)
        
        self.rho = createRho()
        self.transfer = trans.createTransferFunction(100)
        
        self.plotter = Plotter(self.splineInterval)
        
        self.eye = np.array([-2.0, 0.55])
        self.viewRayDelta = 0.2
        self.viewRayDeltaRef = 0.05
        
    def phiInverse(self, geomPoint, uvGuess):
        phi = self.phi
        
        def f(u,v):
            return phi.evaluate(u,v) - geomPoint
        def fJacob(u, v):
            return np.matrix([phi.evaluatePartialDerivativeU(u, v), 
                              phi.evaluatePartialDerivativeV(u, v)]).transpose()
                              
        return newton.newtonsMethod2DClamped(f, fJacob, uvGuess, self.splineInterval)
        
    def generateScalarMatrix(self, boundingBox, width, height):
        phiPlane = self.phiPlane
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
            
            intersections = phiPlane.findTwoIntersections(samplingRay)
            
            if intersections == None:
                continue

            inGeomPoint = intersections[0].geomPoint
            outGeomPoint = intersections[1].geomPoint
    
            plotter.plotIntersectionPoints([inGeomPoint, outGeomPoint])
            
            geomPoints = []
            paramPoints = []
            
            prevUV = intersections[0].paramPoint
            
            for j, x in enumerate(xValues):
                if x < inGeomPoint[0] or x > outGeomPoint[0]:
                    continue
                
                geomPoint = np.array([x, y])
                geomPoints.append(geomPoint)

                paramPoint = self.phiInverse(geomPoint, prevUV)
                paramPoints.append(paramPoint)
                
                scalar = self.rho.evaluate(paramPoint[0], paramPoint[1])
                samplingScalars[i][j] = scalar
                
                prevUV = paramPoint
                
            plotter.plotGeomPoints(geomPoints)
            plotter.plotParamPoints(paramPoints)
            
        return samplingScalars
    
    def getDirectSamplePointLocations(self, samplePoints, intersections, boundingBox):
        locations = np.empty(len(samplePoints))
        
        if intersections == None:
            for i, samplePoint in enumerate(samplePoints):
                if boundingBox.enclosesPoint(samplePoint):
                    locations[i] = SamplingLocation.OUTSIDE_OBJECT
                else:
                    locations[i] = SamplingLocation.OUTSIDE_BOUNDINGBOX
        else:
            inGeomPoint = intersections[0].geomPoint
            outGeomPoint = intersections[1].geomPoint
            
            for i, samplePoint in enumerate(samplePoints):
                if boundingBox.enclosesPoint(samplePoint):
                    if inGeomPoint[0] <= samplePoint[0] <= outGeomPoint[0]:
                        locations[i] = SamplingLocation.INSIDE_OBJECT
                    else:
                        locations[i] = SamplingLocation.OUTSIDE_OBJECT
                else:
                    locations[i] = SamplingLocation.OUTSIDE_BOUNDINGBOX
                    
        return locations

    def getVoxelizedSamplePointLocations(self, samplePoints, scalarTexture, boundingBox):
        locations = np.empty(len(samplePoints))
        bb = boundingBox
        
        for i, samplePoint in enumerate(samplePoints):
            if bb.enclosesPoint(samplePoint):
                u = (samplePoint[0]-bb.left)/bb.getWidth()
                v = (samplePoint[1]-bb.bottom)/bb.getHeight()
                
                if not scalarTexture.closest([u, v]) == self.samplingDefault:
                    locations[i] = SamplingLocation.INSIDE_OBJECT
                else:
                    locations[i] = SamplingLocation.OUTSIDE_OBJECT
            else:
                locations[i] = SamplingLocation.OUTSIDE_BOUNDINGBOX
            
        return locations
            
    def raycastDirect(self, viewRay, delta, boundingBox, plot):
        sampleColors = []
        sampleDeltas = []
        
        samplePoints = viewRay.generateSamplePoints(0, 10, delta)
        intersections = self.phiPlane.findTwoIntersections(viewRay)
        locations = self.getDirectSamplePointLocations(samplePoints, intersections, boundingBox)
        
        if not intersections == None:
            prevUV = intersections[0].paramPoint
            
            for samplePoint, location in itertools.izip(samplePoints, locations):
                if location == SamplingLocation.INSIDE_OBJECT:
                    pixelFrustum = viewRay.frustumBoundingEllipse(samplePoint, delta)
                    
                    pApprox = self.phiInverse(samplePoint, prevUV)
                    gApprox = self.phi.evaluate(pApprox[0], pApprox[1])
                    
                    if not pixelFrustum.enclosesPoint(gApprox):
                        print "NOT ENCLOSED"
                    
                    sampleScalar = self.rho.evaluate(pApprox[0], pApprox[1])
                    sampleColors.append(self.transfer(sampleScalar))
                    sampleDeltas.append(delta)
                            
                    prevUV = pApprox
                
        if plot:
            plotter = self.plotter
            
            #frustumBoundingCircle = viewRay.frustumBoundingCircle(samplePoints[3])
            #plotter.plotCircle(frustumBoundingCircle)
            
            plotter.plotSamplePointsDirect(samplePoints, locations)
        
        return compositing.frontToBack(sampleColors, sampleDeltas)
        
    def raycastVoxelized(self, viewRay, scalarTexture, boundingBox):
        plotter = self.plotter
        bb = boundingBox
        
        sampleColors = []
        sampleDeltas = []
        
        samplePoints = viewRay.generateSamplePoints(0, 10, self.viewRayDelta)
        locations = self.getVoxelizedSamplePointLocations(samplePoints, scalarTexture, boundingBox)
        
        for samplePoint, location in itertools.izip(samplePoints, locations):
            if location == SamplingLocation.INSIDE_OBJECT:
                u = (samplePoint[0]-bb.left)/bb.getWidth()
                v = (samplePoint[1]-bb.bottom)/bb.getHeight()
                
                sampleScalar = scalarTexture.fetch([u, v])
                sampleColors.append(self.transfer(sampleScalar))
                sampleDeltas.append(self.viewRayDelta)
            
        plotter.plotSamplePointsVoxelized(samplePoints, locations)
        
        return compositing.frontToBack(sampleColors, sampleDeltas)
        
    def createPixels(self, numPixels):
        pixels = np.empty((numPixels, 2))
        pixelXs = np.ones(numPixels) * self.pixelX
        pixels[:,0] = pixelXs
        pixels[:,1] = np.linspace(self.firstPixelY, self.lastPixelY, numPixels)
        
        return pixels
        
    def run(self):
        plotter = self.plotter
        
        plotter.plotGrids(self.phi.evaluate, 10, 10)
        plotter.plotScalarField(self.rho, self.transfer)
        
        bb = self.phiPlane.createBoundingBox()
        plotter.plotBoundingBox(bb)
        
        width = 10
        height = 10
        
        samplingScalars = self.generateScalarMatrix(bb, width, height)
        scalarTexture = Texture2D(samplingScalars)
        
        plotter.plotSampleScalars(samplingScalars, bb)    
        plotter.plotScalarTexture(scalarTexture)
        
        numPixelsRef = self.numPixelsRef
        refPixels = self.createPixels(numPixelsRef)
        refPixelWidth = (self.lastPixelY-self.firstPixelY)/(numPixelsRef-1)
        refPixelColors = np.empty((numPixelsRef, 4))
        
        for i, refPixel in enumerate(refPixels):
            viewRay = Ray2D(self.eye, refPixel, refPixelWidth)
            refPixelColors[i] = self.raycastDirect(viewRay, self.viewRayDeltaRef, bb, False)
        
        numPixels = self.numPixels
        pixels = self.createPixels(numPixels)
        pixelWidth = (self.lastPixelY-self.firstPixelY)/(numPixels-1)
        directPixelColors = np.empty((numPixels, 4))
        voxelizedPixelColors = np.empty((numPixels, 4))
        
        for i, refPixel in enumerate(pixels):
            viewRay = Ray2D(self.eye, refPixel, pixelWidth)
            plotter.plotViewRay(viewRay, [0, 10])
            
            #plotter.plotViewRayFrustum(viewRay, [0, 10])
            
            directPixelColors[i] = self.raycastDirect(viewRay, self.viewRayDelta, bb, True)
            voxelizedPixelColors[i] = self.raycastVoxelized(viewRay, scalarTexture, bb)
        
        plotter.plotPixelColorsReference(refPixelColors)
        plotter.plotPixelColorsDirect(directPixelColors)
        plotter.plotPixelColorsVoxelized(voxelizedPixelColors)
        
        directDiffs = colordiff.compare(refPixelColors, directPixelColors)
        plotter.plotPixelColorDiffsDirect(directDiffs)
        
        voxelizedDiffs = colordiff.compare(refPixelColors, voxelizedPixelColors)
        plotter.plotPixelColorDiffsVoxelized(voxelizedDiffs)
        
        plotter.draw()
    
def run():
    main = Main()
    main.run()

if __name__ == "__main__":
    run()
