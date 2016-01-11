import numpy as np

import colordiff
import transfer as trans
from dataset import Dataset
from model.boundaryaccuratemodel import BoundaryAccurateModel
from model.hybridmodel import HybridModel
from model.splinemodel import SplineModel
from model.voxellodmodel import VoxelLodModel
from model.voxelmodel import VoxelModel
from plotting.plotter import Plotter
from ray import Ray2D
from renderers.comparerenderer import CompareSummary
from splineplane import SplinePlane
from texture import Texture2D
from voxelcriterion.geometriccriterion import GeometricCriterion


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
        
        self.eye = np.array([-0.9, 0.65])
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
        
        refSplineModel = SplineModel(self.transfer, phiPlane, rho, 0.0001)
        directSplineModel = SplineModel(self.transfer, phiPlane, rho)
        
        numPixelsRef = self.numPixelsRef
        refPixels = self.createPixels(numPixelsRef)
        refPixelWidth = (self.screenTop-self.screenBottom) / numPixelsRef
        refPixelColors = np.empty((numPixelsRef, 4))
        
        for i, refPixel in enumerate(refPixels):
            viewRay = Ray2D(self.eye, refPixel, 10, refPixelWidth)
            refSplinePlotter.plotViewRay(viewRay, [0, 10])

            viewRay.splineIntersects = refSplineModel.phiPlane.findTwoIntersections(viewRay)
            result = refSplineModel.raycast(viewRay, self.viewRayDeltaRef)

            if result.color is not None:
                refPixelColors[i] = result.color
            else:
                refPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
        
        numPixels = self.numPixels
        pixels = self.createPixels(numPixels)
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels
        
        viewRays = np.empty(numPixels, dtype=object)
        directPixelColors = np.empty((numPixels, 4))
        pixelColors = np.empty((numPixels, 4))
        
        maxDirectSamplePoints = 0

        for i in range(numPixels):
            pixel = pixels[i]
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)
            viewRays[i] = viewRay
            
            directSplinePlotter.plotViewRay(viewRay, [0, 10])
            voxelPlotter.plotViewRay(viewRay, [0, 10])
        
        for i, viewRay in enumerate(viewRays):
            viewRay.splineIntersects = directSplineModel.phiPlane.findTwoIntersections(viewRay)
            result = directSplineModel.raycast(viewRay, self.viewRayDeltaDirect, directSplinePlotter)

            if result.color is not None:
                directPixelColors[i] = result.color
                maxDirectSamplePoints = max(result.samples, maxDirectSamplePoints)
            else:
                directPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
            
        plotter.pixelReferencePlot.plotPixelColors(refPixelColors)
        plotter.pixelDirectPlot.plotPixelColors(directPixelColors)
        
        directDiffs = colordiff.compare(refPixelColors, directPixelColors)
        plotter.pixelDirectDiffPlot.plotPixelColorDiffs(directDiffs)
        directSummary = CompareSummary(directPixelColors, maxDirectSamplePoints, directDiffs)
        self.printSummary("Direct", directSummary)
        
        plotter.draw()
        
        print "Voxelized color diffs"
        print "---------------------"
            
        texDimSize = 32

        samplingScalars = refSplineModel.generateScalarMatrix(bb, texDimSize, texDimSize, self.voxelizationTolerance, paramPlotter, refSplinePlotter)
        voxelPlotter.plotScalars(samplingScalars, bb)

        scalarTexture = Texture2D(samplingScalars)
        
        voxelModel = VoxelModel(self.transfer, scalarTexture, bb)
        
        choice = 0

        if choice == 0:
            model = voxelModel
        elif choice == 1:
            model = BoundaryAccurateModel(self.transfer, directSplineModel, voxelModel)
        elif choice == 2:
            voxelWidth = bb.getHeight() / float(texDimSize)
            criterion = GeometricCriterion(pixelWidth, voxelWidth)
            model = HybridModel(self.transfer, directSplineModel, voxelModel, criterion)
        else:
            lodTextures = []
            lodTextures.append(scalarTexture)

            size = texDimSize / 2
            while size >= 2:
                scalars = refSplineModel.generateScalarMatrix(bb, size, size, self.voxelizationTolerance)
                lodTextures.append(Texture2D(scalars))
                size /= 2

            model = VoxelLodModel(self.transfer, lodTextures, bb, pixelWidth)
        
        maxSamplePoints = 0

        for i, viewRay in enumerate(viewRays):
            viewRay.boundingBoxIntersects = bb.findTwoIntersections(viewRay)
            viewRay.splineIntersects = directSplineModel.phiPlane.findTwoIntersections(viewRay)

            result = model.raycast(viewRay, self.viewRayDeltaVoxelized, plotter.voxelModelPlotter)

            if result.color is not None:
                pixelColors[i] = result.color
                maxSamplePoints = max(result.samples, maxSamplePoints)
            else:
                pixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])

    
        voxelizedDiffs = colordiff.compare(refPixelColors, pixelColors)
        summary = CompareSummary(pixelColors, maxSamplePoints, voxelizedDiffs)
        self.printSummary("Voxel ({}x{})".format(texDimSize, texDimSize), summary)

        plotter.plotScalarTexture(scalarTexture)
        plotter.pixelVoxelizedPlot.plotPixelColors(pixelColors)
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
