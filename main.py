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
from renderer import Renderer
from renderers.comparerenderer import CompareSummary
from screen import Screen
from splineplane import SplinePlane
from texture import Texture2D
from voxelcriterion.geometriccriterion import GeometricCriterion


class Main:
    def __init__(self):
        self.dataset = Dataset(1, 1)
        
        self.splineInterval = [0.0, 1.0]
        self.transfer = trans.createTransferFunction(100)

        pixelX = -0.5
        screenTop = 0.90
        screenBottom = 0.2
        numPixels = 10
        self.screen = Screen(pixelX, screenTop, screenBottom, numPixels)
        self.eye = np.array([-0.9, 0.65])
        
        self.plotter = Plotter(self.splineInterval)

        self.viewRayDeltaRef = 0.01
        self.viewRayDeltaDirect = 0.01
        self.viewRayDeltaVoxelized = 0.01
        
        self.voxelizationTolerance = 1e-5
        
    def run(self):
        renderer = Renderer(self.eye, self.screen)

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

        paramPlotter.plotGrid(10, 10)
        paramPlotter.plotScalarField(rho, self.transfer)
        
        bb = phiPlane.createBoundingBox()
        refSplinePlotter.plotBoundingBox(bb)
        directSplinePlotter.plotBoundingBox(bb)
        voxelPlotter.plotBoundingBox(bb)
        
        refSplineModel = SplineModel(self.transfer, phiPlane, rho, 0.0001)
        directSplineModel = SplineModel(self.transfer, phiPlane, rho)

        refPixelColors = renderer.render(refSplineModel, self.viewRayDeltaRef, refSplinePlotter)

        directPixelColors = renderer.render(directSplineModel, self.viewRayDeltaDirect, directSplinePlotter)
        maxDirectSamplePoints = renderer.maxSamplePoints
            
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

        samplingScalars = refSplineModel.generateScalarMatrix(bb, texDimSize, texDimSize, self.voxelizationTolerance,
                                                              paramPlotter, refSplinePlotter)
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
            criterion = GeometricCriterion(self.screen.pixelWidth, voxelWidth)
            model = HybridModel(self.transfer, directSplineModel, voxelModel, criterion)
        else:
            lodTextures = [scalarTexture]

            size = texDimSize / 2
            while size >= 2:
                scalars = refSplineModel.generateScalarMatrix(bb, size, size, self.voxelizationTolerance)
                lodTextures.append(Texture2D(scalars))
                size /= 2

            model = VoxelLodModel(self.transfer, lodTextures, bb, self.screen.pixelWidth)

        pixelColors = renderer.render(model, self.viewRayDeltaVoxelized, voxelPlotter)
        maxSamplePoints = renderer.maxSamplePoints

        voxelizedDiffs = colordiff.compare(refPixelColors, pixelColors)
        summary = CompareSummary(pixelColors, maxSamplePoints, voxelizedDiffs)
        self.printSummary("Voxel ({}x{})".format(texDimSize, texDimSize), summary)

        plotter.plotScalarTexture(scalarTexture)
        plotter.pixelVoxelizedPlot.plotPixelColors(pixelColors)
        plotter.pixelVoxelizedDiffPlot.plotPixelColorDiffs(voxelizedDiffs)
        
        plotter.draw()

    @staticmethod
    def printSummary(name, summary):
        print "{} color diffs".format(name)
        print "---------------------"
        summary.printData()
        print ""


def run():
    main = Main()
    main.run()

if __name__ == "__main__":
    run()
