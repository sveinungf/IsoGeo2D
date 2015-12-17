import numpy as np

import colordiff
import transfer as trans
from model.boundaryhybridmodel import BoundaryHybridModel
from model.hybridmodel import HybridModel
from model.splinemodel import SplineModel
from model.voxelmodel import VoxelModel
from plotting.plotter import Plotter
from voxelcriterion.geometriccriterion import GeometricCriterion
from dataset import Dataset
from ray import Ray2D
from splineplane import SplinePlane
from summary import Summary
from texture import Texture2D

class Main:
    def __init__(self):
        self.dataset = Dataset(1, 1)
        
        self.splineInterval = [0, 0.99999]
        self.transfer = trans.createTransferFunction(100)
        
        self.numPixels = 10
        self.numPixelsRef = self.numPixels * 1
        self.pixelX = -0.5
        self.screenTop = 0.90
        self.screenBottom = 0.2
        
        self.plotter = Plotter(self.splineInterval)
        
        self.eye = np.array([-2.0, 0.65])
        self.viewRayDeltaRef = 0.01
        self.viewRayDeltaDirect = 0.01
        self.viewRayDeltaVoxelized = 0.01
        
        self.voxelizationTolerance = 1e-5
        
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
        
        rho = self.dataset.rho
        phi = self.dataset.phi
        phiPlane = SplinePlane(phi, self.splineInterval, 0.00001)
        
        refSplinePlotter = plotter.refSplineModelPlotter
        directSplinePlotter = plotter.directSplineModelPlotter
        voxelPlotter = plotter.voxelModelPlotter
        paramPlotter = plotter.paramPlotter
        
        refSplinePlotter.plotGrid(phi.evaluate, 10, 10)
        directSplinePlotter.plotGrid(phi.evaluate, 10, 10)
        
        plotter.plotGrids(phi.evaluate, 10, 10)
        plotter.plotScalarField(rho, self.transfer)
        
        bb = phiPlane.createBoundingBox()
        refSplinePlotter.plotBoundingBox(bb)
        directSplinePlotter.plotBoundingBox(bb)
        voxelPlotter.plotBoundingBox(bb)
        
        splineModel = SplineModel(self.transfer, phiPlane, rho)
        
        numPixelsRef = self.numPixelsRef
        refPixels = self.createPixels(numPixelsRef)
        refPixelWidth = (self.screenTop-self.screenBottom) / numPixelsRef
        refPixelColors = np.empty((numPixelsRef, 4))
        
        for i, refPixel in enumerate(refPixels):
            viewRay = Ray2D(self.eye, refPixel, 10, refPixelWidth)
            refSplinePlotter.plotViewRay(viewRay, [0, 10])
            
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                [_, refPixelColors[i]] = splineModel.raycast(viewRay, intersections, self.viewRayDeltaRef)
            else:
                refPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
        
        numPixels = self.numPixels
        pixels = self.createPixels(numPixels)
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels
        
        viewRays = np.empty(numPixels, dtype=object)
        directPixelColors = np.empty((numPixels, 4))
        voxelizedPixelColors = np.empty((numPixels, 4))
        
        maxDirectSamplePoints = 0

        for i in range(numPixels):
            pixel = pixels[i]
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)
            viewRays[i] = viewRay
            
            directSplinePlotter.plotViewRay(viewRay, [0, 10])
            voxelPlotter.plotViewRay(viewRay, [0, 10])
        
        for i, viewRay in enumerate(viewRays):
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                [directSamplePoints, directPixelColors[i]] = splineModel.raycast(viewRay, intersections, self.viewRayDeltaDirect, directSplinePlotter)
                maxDirectSamplePoints = max(directSamplePoints, maxDirectSamplePoints)
            else:
                directPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
            
        plotter.pixelReferencePlot.plotPixelColors(refPixelColors)
        plotter.pixelDirectPlot.plotPixelColors(directPixelColors)
        
        directDiffs = colordiff.compare(refPixelColors, directPixelColors)
        plotter.pixelDirectDiffPlot.plotPixelColorDiffs(directDiffs)
        directSummary = Summary(directDiffs, maxDirectSamplePoints)
        self.printSummary("Direct", directSummary)
        
        plotter.draw()
        
        print "Voxelized color diffs"
        print "---------------------"
            
        texDimSize = 20
        
        splineModel.plotBoundingEllipses = True
        samplingScalars = splineModel.generateScalarMatrix(bb, texDimSize, texDimSize, self.voxelizationTolerance, paramPlotter, refSplinePlotter)
        scalarTexture = Texture2D(samplingScalars)
        
        voxelWidth = bb.getHeight() / float(texDimSize)
        criterion = GeometricCriterion(pixelWidth, voxelWidth)
        
        voxelModel = VoxelModel(self.transfer, scalarTexture, bb)
        
        choice = 3
        
        if choice == 0:
            model = voxelModel
        elif choice == 1:
            model = BoundaryHybridModel(self.transfer, splineModel, voxelModel)
        elif choice == 2:
            model = HybridModel(self.transfer, splineModel, voxelModel, criterion)
        elif choice == 3:
            bhModel = BoundaryHybridModel(self.transfer, splineModel, voxelModel)
            model = HybridModel(self.transfer, splineModel, bhModel, criterion)
        
        maxVoxelSamplePoints = 0

        for i, viewRay in enumerate(viewRays):
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                [voxelSamplePoints, voxelizedPixelColors[i]] = model.raycast(viewRay, intersections, self.viewRayDeltaVoxelized, plotter.voxelModelPlotter)
                maxVoxelSamplePoints = max(voxelSamplePoints, maxVoxelSamplePoints)
            else:
                voxelizedPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
    
        voxelizedDiffs = colordiff.compare(refPixelColors, voxelizedPixelColors)
        summary = Summary(voxelizedDiffs, maxVoxelSamplePoints)
        self.printSummary("Voxel ({}x{})".format(texDimSize, texDimSize), summary)

        voxelPlotter.plotScalars(samplingScalars, bb)    
        plotter.plotScalarTexture(scalarTexture)
        plotter.pixelVoxelizedPlot.plotPixelColors(voxelizedPixelColors)
        plotter.pixelVoxelizedDiffPlot.plotPixelColorDiffs(voxelizedDiffs)
        
        plotter.draw()
        
    def printSummary(self, name, summary):
        print "{} color diffs".format(name)
        print "---------------------"
        summary.printData()
        print ""
    
def run():
    main = Main()
    main.run()

if __name__ == "__main__":
    run()
