import numpy as np

import colordiff
import transfer as trans
from plotter import Plotter
from ray import Ray2D
from splinemodel import SplineModel
from splineplane import SplinePlane
from splines import Spline2D
from texture import Texture2D
from voxelmodel import VoxelModel

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
        
        self.numPixels = 10
        self.numPixelsRef = self.numPixels * 1
        self.pixelX = -0.5
        self.screenTop = 0.95
        self.screenBottom = 0.15
        
        self.phi = createPhi()
        self.phiPlane = SplinePlane(self.phi, self.splineInterval, 0.00001)
        
        self.rho = createRho()
        self.transfer = trans.createTransferFunction(100)
        
        self.plotter = Plotter(self.splineInterval)
        
        self.eye = np.array([-2.0, 0.65])
        self.viewRayDeltaRef = 0.01
        self.viewRayDeltaDirect = 0.10
        self.viewRayDeltaVoxelized = 0.01
        
    def generateScalarMatrix(self, boundingBox, width, height):
        phiPlane = self.phiPlane
        #plotter = self.plotter
        
        rayCount = height
        samplingsPerRay = width
        
        xDelta = float(boundingBox.getWidth())/samplingsPerRay
        yDelta = float(boundingBox.getHeight())/rayCount
        
        xValues = np.linspace(boundingBox.left+xDelta/2, boundingBox.right-xDelta/2, samplingsPerRay)
        yValues = np.linspace(boundingBox.bottom+yDelta/2, boundingBox.top-yDelta/2, rayCount)
        
        samplingScalars = np.ones((rayCount, samplingsPerRay)) * VoxelModel.samplingDefault    
        
        for i, y in enumerate(yValues):
            samplingRay = Ray2D(np.array([self.eye[0], y]), np.array([0, y]), 10, yDelta)
            #plotter.plotSamplingRay(samplingRay, [0, 10])
            
            intersections = phiPlane.findTwoIntersections(samplingRay)
            
            if intersections == None:
                continue

            inGeomPoint = intersections[0].geomPoint
            outGeomPoint = intersections[1].geomPoint
    
            #plotter.plotIntersectionPoints([inGeomPoint, outGeomPoint])
            
            geomPoints = []
            paramPoints = []
            
            prevUV = intersections[0].paramPoint
            
            for j, x in enumerate(xValues):
                if x < inGeomPoint[0] or x > outGeomPoint[0]:
                    continue
                
                samplePoint = np.array([x, y])
                
                pixelFrustum = samplingRay.frustumBoundingEllipseParallel(samplePoint, xDelta)
                #plotter.plotEllipse(pixelFrustum)
                
                pApprox = phiPlane.inverseInFrustum(samplePoint, prevUV, pixelFrustum)
                gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])
                geomPoints.append(gApprox)

                paramPoints.append(pApprox)
                
                scalar = self.rho.evaluate(pApprox[0], pApprox[1])
                samplingScalars[i][j] = scalar
                
                prevUV = pApprox
                
            #plotter.plotGeomPoints(geomPoints)
            #plotter.plotParamPoints(paramPoints)
            
        return samplingScalars
        
    def createPixels(self, numPixels):
        pixels = np.empty((numPixels, 2))
        pixelXs = np.ones(numPixels) * self.pixelX
        
        deltaY = (self.screenTop - self.screenBottom) / numPixels
        firstPixelY = self.screenBottom + (deltaY/2.0)
        lastPixelY = self.screenTop - (deltaY/2.0)
        
        pixels[:,0] = pixelXs
        pixels[:,1] = np.linspace(firstPixelY, lastPixelY, numPixels)
        
        return pixels
        
    def run(self):
        plotter = self.plotter
        
        plotter.plotGrids(self.phi.evaluate, 10, 10)
        plotter.plotScalarField(self.rho, self.transfer)
        
        bb = self.phiPlane.createBoundingBox()
        plotter.plotBoundingBox(bb)
        
        splineModel = SplineModel(self.phiPlane, self.rho, self.transfer)
        
        numPixelsRef = self.numPixelsRef
        refPixels = self.createPixels(numPixelsRef)
        refPixelWidth = (self.screenTop-self.screenBottom) / numPixelsRef
        refPixelColors = np.empty((numPixelsRef, 4))
        
        for i, refPixel in enumerate(refPixels):
            viewRay = Ray2D(self.eye, refPixel, 10, refPixelWidth)
            #plotter.plotViewRayReference(viewRay, [0, 10])
            
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                refPixelColors[i] = splineModel.raycast(viewRay, intersections, self.viewRayDeltaRef)
        
        numPixels = self.numPixels
        pixels = self.createPixels(numPixels)
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels
        
        viewRays = np.empty(numPixels, dtype=object)
        for i, pixel in enumerate(pixels):
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)
            plotter.plotViewRay(viewRay, [0, 10])
            viewRays[i] = viewRay
            
        directPixelColors = np.empty((numPixels, 4))
        voxelizedPixelColors = np.empty((numPixels, 4))
        
        for i, viewRay in enumerate(viewRays):
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                directPixelColors[i] = splineModel.raycast(viewRay, intersections, self.viewRayDeltaDirect)
            
        plotter.plotPixelColorsReference(refPixelColors)
        #plotter.plotPixelColorsDirect(directPixelColors)
        
        #directDiff = colordiff.compare(refPixelColors, directPixelColors)
        #plotter.plotPixelColorDiffsDirect(directDiff.colorDiffs)
        #print "Direct color diffs:"
        #directDiff.printData()
        #print ""
        
        plotter.draw()
        
        print "Voxelized color diffs"
        print "---------------------"
            
        texDimSize = 8
        
        for _ in range(4):
            samplingScalars = self.generateScalarMatrix(bb, texDimSize, texDimSize)
            scalarTexture = Texture2D(samplingScalars)
            
            voxelModel = VoxelModel(scalarTexture, self.transfer, bb)

            for i, viewRay in enumerate(viewRays):
                intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
                
                if intersections != None:
                    voxelizedPixelColors[i] = voxelModel.raycast(viewRay, intersections, self.viewRayDeltaVoxelized)
        
            voxelizedDiff = colordiff.compare(refPixelColors, voxelizedPixelColors)
            
            print "Texture size: {}x{}".format(texDimSize, texDimSize)
            voxelizedDiff.printData()
            print ""
       
            texDimSize *= 2
        

        plotter.plotSampleScalars(samplingScalars, bb)    
        plotter.plotScalarTexture(scalarTexture)
        plotter.plotPixelColorsVoxelized(voxelizedPixelColors)
        plotter.plotPixelColorDiffsVoxelized(voxelizedDiff.colordiffs)
        
        plotter.draw()
    
def run():
    main = Main()
    main.run()

if __name__ == "__main__":
    run()
