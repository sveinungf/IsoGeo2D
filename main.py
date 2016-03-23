import numpy as np

import colordiff
from model.boundaryaccuratemodel import BoundaryAccurateModel
from model.hybridmodel import HybridModel
from model.splinemodel import SplineModel
from model.voxellodmodel import VoxelLodModel
from model.voxelmodel import VoxelModel
from plotting.plotter import Plotter
from dataset import Dataset
from modeltype import ModelType
from renderdata import RenderData
from renderer import Renderer
from screen import Screen
from splineplane import SplinePlane
from summary import Summary
from textureY import Texture2D
import textureY
from voxelcriterion.geometriccriterion import GeometricCriterion


class Main:
    def __init__(self):
        self.splineInterval = [0.0, 1.0]

        screenBottom = np.array([-0.5, 0.2])
        screenTop = np.array([-0.5, 0.9])
        numPixels = 10
        self.screen = Screen(screenBottom, screenTop, numPixels)
        self.eye = np.array([-0.9, 0.65])

        self.viewRayDelta = 0.3
        self.viewRayDeltaRef = 0.1
        self.refTolerance = 1e-3
        self.intersectTolerance = 1e-5

        self.voxelizationTolerance = 1e-3

    def run(self, rhoNo=1, phiNo=1, tfNo=1):
        dataset = Dataset(rhoNo, phiNo, tfNo)
        texDimSize = 8

        renderer = Renderer(self.eye, self.screen)

        rho = dataset.rho
        phi = dataset.phi
        tf = dataset.tf
        phiPlane = SplinePlane(phi, self.splineInterval, self.intersectTolerance)

        boundingBox = phiPlane.createBoundingBox()

        plotter = Plotter(self.splineInterval)
        refSplinePlotter = plotter.refSplineModelPlotter
        directSplinePlotter = plotter.directSplineModelPlotter
        voxelPlotter = plotter.voxelModelPlotter
        paramPlotter = plotter.paramPlotter

        refSplinePlotter.plotGrid(phi.evaluate, 10, 10)
        directSplinePlotter.plotGrid(phi.evaluate, 10, 10)

        paramPlotter.plotGrid(10, 10)
        paramPlotter.plotScalarField(rho, tf)

        refSplinePlotter.plotBoundingBox(boundingBox)
        directSplinePlotter.plotBoundingBox(boundingBox)
        voxelPlotter.plotBoundingBox(boundingBox)

        # Creating models
        refSplineModel = SplineModel(tf, phiPlane, rho, self.refTolerance)
        directSplineModel = SplineModel(tf, phiPlane, rho)

        #samplingScalars = refSplineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize,
        #                                                      self.voxelizationTolerance, paramPlotter,
        #                                                      refSplinePlotter)

        samplingScalars, indicators = textureY.create(refSplineModel, texDimSize, texDimSize, self.voxelizationTolerance, paramPlotter, refSplinePlotter)

        voxelPlotter.plotScalars(samplingScalars, boundingBox)

        scalarTexture = Texture2D(samplingScalars, indicators)
        plotter.plotScalarTexture(scalarTexture)

        voxelModel = VoxelModel(tf, scalarTexture, boundingBox)

        choice = 0

        if choice == 0:
            model = voxelModel
            modelType = ModelType.VOXEL
        elif choice == 1:
            model = BoundaryAccurateModel(tf, directSplineModel, voxelModel)
            modelType = ModelType.BOUNDARYACCURATE
        elif choice == 2:
            voxelWidth = boundingBox.getHeight() / float(texDimSize)
            criterion = GeometricCriterion(self.screen.pixelWidth, voxelWidth)
            model = HybridModel(tf, directSplineModel, voxelModel, criterion)
            modelType = ModelType.HYBRID
        else:
            lodTextures = [scalarTexture]

            size = texDimSize / 2
            while size >= 2:
                scalars = refSplineModel.generateScalarMatrix(boundingBox, size, size, self.voxelizationTolerance)
                lodTextures.append(Texture2D(scalars))
                size /= 2

            model = VoxelLodModel(tf, lodTextures, boundingBox, self.screen.pixelWidth)
            modelType = ModelType.VOXEL

        # Rendering
        refRenderData = RenderData(ModelType.REFERENCE, self.viewRayDeltaRef)
        refRenderData.renderResult = renderer.render(refSplineModel, self.viewRayDeltaRef, refSplinePlotter)

        directRenderData = RenderData(ModelType.DIRECT, self.viewRayDelta)
        directRenderData.renderResult = renderer.render(directSplineModel, self.viewRayDelta, directSplinePlotter)

        renderData = RenderData(modelType, self.viewRayDelta, texSize=texDimSize)
        renderData.renderResult = renderer.render(model, self.viewRayDelta, voxelPlotter)

        # Plotting
        refPixelColors = refRenderData.renderResult.colors
        directPixelColors = directRenderData.renderResult.colors
        pixelColors = renderData.renderResult.colors

        plotter.pixelReferencePlot.plotPixelColors(refPixelColors)
        plotter.pixelDirectPlot.plotPixelColors(directPixelColors)
        plotter.pixelVoxelizedPlot.plotPixelColors(pixelColors)

        directDiffs = colordiff.compare(refPixelColors, directPixelColors)
        diffs = colordiff.compare(refPixelColors, pixelColors)

        plotter.pixelDirectDiffPlot.plotPixelColorDiffs(directDiffs)
        plotter.pixelVoxelizedDiffPlot.plotPixelColorDiffs(diffs)

        plotter.draw()

        # Printing
        directSummary = Summary(directRenderData, directDiffs)
        directSummary.printData()

        print ""

        summary = Summary(renderData, diffs)
        summary.printData()


def run():
    main = Main()
    main.run()


if __name__ == "__main__":
    run()
