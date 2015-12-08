import numpy as np

import colordiff
import splineexample
import transfer as trans
from plotter.plotter import Plotter
from voxelcriterion.geometriccriterion import GeometricCriterion
from hybridmodel import HybridModel
from ray import Ray2D
from splinemodel import SplineModel
from splineplane import SplinePlane
from texture import Texture2D
from voxelmodel import VoxelModel

class Main:
    def __init__(self):
        self.splineInterval = [0, 0.99999]
        
        self.numPixels = 10
        self.numPixelsRef = self.numPixels * 1
        self.pixelX = -0.5
        self.screenTop = 0.90
        self.screenBottom = 0.2
        
        self.phi = splineexample.createPhi()
        self.phiPlane = SplinePlane(self.phi, self.splineInterval, 0.00001)
        
        self.rho = splineexample.createRho()
        self.transfer = trans.createTransferFunction(100)
        
        self.plotter = Plotter(self.splineInterval)
        
        self.eye = np.array([-2.0, 0.65])
        self.viewRayDeltaRef = 0.01
        self.viewRayDeltaDirect = 0.01
        self.viewRayDeltaVoxelized = 0.01
        
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
        phi = self.phi
        plotter = self.plotter
        
        refSplinePlotter = plotter.refSplineModelPlotter
        directSplinePlotter = plotter.directSplineModelPlotter
        voxelPlotter = plotter.voxelModelPlotter
        
        refSplinePlotter.plotGrid(phi.evaluate, 10, 10)
        directSplinePlotter.plotGrid(phi.evaluate, 10, 10)
        
        plotter.plotGrids(self.phi.evaluate, 10, 10)
        plotter.plotScalarField(self.rho, self.transfer)
        
        bb = self.phiPlane.createBoundingBox()
        refSplinePlotter.plotBoundingBox(bb)
        directSplinePlotter.plotBoundingBox(bb)
        voxelPlotter.plotBoundingBox(bb)
        
        splineModel = SplineModel(self.phiPlane, self.rho, self.transfer)
        
        numPixelsRef = self.numPixelsRef
        refPixels = self.createPixels(numPixelsRef)
        refPixelWidth = (self.screenTop-self.screenBottom) / numPixelsRef
        refPixelColors = np.empty((numPixelsRef, 4))
        
        for i, refPixel in enumerate(refPixels):
            viewRay = Ray2D(self.eye, refPixel, 10, refPixelWidth)
            refSplinePlotter.plotViewRay(viewRay, [0, 10])
            
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                refPixelColors[i] = splineModel.raycast(viewRay, intersections, self.viewRayDeltaRef)
            else:
                refPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
        
        numPixels = self.numPixels
        pixels = self.createPixels(numPixels)
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels
        
        viewRays = np.empty(numPixels, dtype=object)
        directPixelColors = np.empty((numPixels, 4))
        voxelizedPixelColors = np.empty((numPixels, 4))

        for i in range(numPixels):
            pixel = pixels[i]
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)
            viewRays[i] = viewRay
            
            directSplinePlotter.plotViewRay(viewRay, [0, 10])
            voxelPlotter.plotViewRay(viewRay, [0, 10])
        
        for i, viewRay in enumerate(viewRays):
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                directPixelColors[i] = splineModel.raycast(viewRay, intersections, self.viewRayDeltaDirect, directSplinePlotter)
            else:
                directPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
            
        plotter.pixelReferencePlot.plotPixelColors(refPixelColors)
        plotter.pixelDirectPlot.plotPixelColors(directPixelColors)
        
        directDiff = colordiff.compare(refPixelColors, directPixelColors)
        plotter.pixelDirectDiffPlot.plotPixelColorDiffs(directDiff.colordiffs)
        
        print "Direct color diffs:"
        print "---------------------"
        directDiff.printData()
        print ""
        
        plotter.draw()
        
        print "Voxelized color diffs"
        print "---------------------"
            
        texDimSize = 16
        
        for _ in range(3):
            samplingScalars = splineModel.generateScalarMatrix(bb, texDimSize, texDimSize)
            scalarTexture = Texture2D(samplingScalars)
            
            voxelModel = VoxelModel(scalarTexture, self.transfer, bb, voxelPlotter)
            voxelWidth = bb.getHeight() / float(texDimSize)
            criterion = GeometricCriterion(pixelWidth, voxelWidth)
            #model = VoxelModel(scalarTexture, self.transfer, bb, voxelPlotter)
            model = HybridModel(splineModel, voxelModel, criterion, voxelPlotter)
            model.plotSamplePoints = True

            for i, viewRay in enumerate(viewRays):
                intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
                
                if intersections != None:
                    voxelizedPixelColors[i] = model.raycast(viewRay, intersections, self.viewRayDeltaVoxelized)
                else:
                    voxelizedPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
        
            voxelizedDiff = colordiff.compare(refPixelColors, voxelizedPixelColors)
            
            print "Texture size: {}x{}".format(texDimSize, texDimSize)
            voxelizedDiff.printData()
            print ""
       
            texDimSize += 2
        

        voxelPlotter.plotScalars(samplingScalars, bb)    
        plotter.plotScalarTexture(scalarTexture)
        plotter.pixelVoxelizedPlot.plotPixelColors(voxelizedPixelColors)
        plotter.pixelVoxelizedDiffPlot.plotPixelColorDiffs(voxelizedDiff.colordiffs)
        
        plotter.draw()
    
def run():
    main = Main()
    main.run()

if __name__ == "__main__":
    run()
