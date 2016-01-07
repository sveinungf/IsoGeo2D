import numpy as np

import fileio.voxelio as voxelio
import transfer as trans
from dataset import Dataset
from model.boundaryaccuratemodel import BoundaryAccurateModel
from model.hybridmodel import HybridModel
from model.splinemodel import SplineModel
from model.voxelmodel import VoxelModel
from plotting.graphfigure import GraphFigure
from plotting.pixelfigure import PixelFigure
from ray import Ray2D
from renderers.comparerenderer import CompareRenderer
from renderers.hybridrenderer import HybridRenderer
from renderers.renderer import Renderer
from splineplane import SplinePlane
from texture import Texture2D
from voxelcriterion.geometriccriterion import GeometricCriterion


class Main2:
    def __init__(self, eyeX=-2.0):
        self.dataset = Dataset(1, 1)
        
        self.splineInterval = [0, 0.99999]
        self.transfer = trans.createTransferFunction(100)

        self.numPixels = 100
        self.pixelX = -0.5
        self.screenTop = 0.9
        self.screenBottom = 0.2
        
        self.eye = np.array([eyeX, 0.65])
        self.viewRayDelta = 0.01
        self.viewRayDeltaRef = 0.001
        self.refTolerance = 0.001
        
        self.voxelizationTolerance = 1e-5

        self.autoDelta = False
        
    def createPixels(self, numPixels):
        pixels = np.empty((numPixels, 2))
        pixelXs = np.ones(numPixels) * self.pixelX
        
        deltaY = (self.screenTop - self.screenBottom) / numPixels
        firstPixelY = self.screenBottom + (deltaY/2.0)
        lastPixelY = self.screenTop - (deltaY/2.0)
        
        pixels[:, 0] = pixelXs
        pixels[:, 1] = np.linspace(firstPixelY, lastPixelY, numPixels)
        
        return pixels
        
    def run(self):
        numPixels = self.numPixels
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels

        texDimSizes = np.array([64, 128, 192, 256, 320, 384])
        
        numTextures = len(texDimSizes)
        
        rho = self.dataset.rho
        phi = self.dataset.phi
        phiPlane = SplinePlane(phi, self.splineInterval, 0.00001)
        
        boundingBox = phiPlane.createBoundingBox()
        
        refSplineModel = SplineModel(self.transfer, phiPlane, rho, self.refTolerance)
        directSplineModel = SplineModel(self.transfer, phiPlane, rho)
        voxelModels = np.empty(numTextures, dtype=object)
        baModels = np.empty(numTextures, dtype=object)
        hybridModels = np.empty(numTextures, dtype=object)
        
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            
            if voxelio.exist(self.dataset, texDimSize, texDimSize):
                samplingScalars = voxelio.read(self.dataset, texDimSize, texDimSize)
                print "Read {}x{} texture data from file".format(texDimSize, texDimSize)
            else:
                samplingScalars = refSplineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize, self.voxelizationTolerance)
                voxelio.write(self.dataset, samplingScalars)
                print "Wrote {}x{} texture data to file".format(texDimSize, texDimSize)
            
            scalarTexture = Texture2D(samplingScalars)
            
            voxelWidth = boundingBox.getHeight() / float(texDimSize)
            criterion = GeometricCriterion(pixelWidth, voxelWidth)
            
            voxelModels[i] = VoxelModel(self.transfer, scalarTexture, boundingBox)
            baModels[i] = BoundaryAccurateModel(self.transfer, directSplineModel, voxelModels[i])
            hybridModels[i] = HybridModel(self.transfer, directSplineModel, baModels[i], criterion)

        pixels = self.createPixels(numPixels)
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels

        viewRays = []
        
        for i, pixel in enumerate(pixels):
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)
            
            viewRay.splineIntersects = directSplineModel.phiPlane.findTwoIntersections(viewRay)
            viewRay.boundingBoxIntersects = boundingBox.findTwoIntersections(viewRay)

            viewRays.append(viewRay)

        figure = PixelFigure(texDimSizes)

        refRenderer = Renderer(self.viewRayDeltaRef, figure.refPixelsPlot)
        refSummary = refRenderer.render(refSplineModel, viewRays)
        self.printSummary("Reference (delta={})".format(self.viewRayDeltaRef), refSummary)

        refPixelColors = refSummary.colors

        directSummaries = []
        voxelSummaries = []
        baSummaries = []
        hybridSummaries = []

        if not self.autoDelta:
            renderer = CompareRenderer(self.viewRayDelta, figure.directPixelsPlot, figure.directDiffsPlot, refPixelColors)
            summary = renderer.render(directSplineModel, viewRays)
            self.printSummary("Direct (delta={})".format(self.viewRayDelta), summary)

            for i in range(numTextures):
                directSummaries.append(summary)

        for i, texSize in enumerate(texDimSizes):
            if self.autoDelta:
                voxelWidth = boundingBox.getWidth() / float(texSize)
                delta = voxelWidth/2.0

                renderer = CompareRenderer(delta, None, None, refPixelColors)
                summary = renderer.render(directSplineModel, viewRays)
                directSummaries.append(summary)
                self.printSummary("Direct (delta={})".format(delta), summary)
            else:
                delta = self.viewRayDelta

            renderer = CompareRenderer(delta, figure.voxelPixelsPlots[i], figure.voxelDiffsPlots[i], refPixelColors)
            summary = renderer.render(voxelModels[i], viewRays)
            voxelSummaries.append(summary)
            self.printSummary("Voxel ({}x{})".format(texSize, texSize), summary)

            renderer = CompareRenderer(delta, figure.baPixelsPlots[i], figure.baDiffsPlots[i], refPixelColors)
            summary = renderer.render(baModels[i], viewRays)
            baSummaries.append(summary)
            self.printSummary("Boundary accurate ({}x{})".format(texSize, texSize), summary)

            renderer = HybridRenderer(delta, figure.hybridPixelsPlots[i], figure.hybridDiffsPlots[i], refPixelColors, figure.hybridVoxelRatioPlots[i])
            summary = renderer.render(hybridModels[i], viewRays)
            hybridSummaries.append(summary)
            self.printSummary("Hybrid ({}x{})".format(texSize, texSize), summary)

        figure.show()

        graphFigure = GraphFigure(texDimSizes)
        graphFigure.graphSummaries(directSummaries, 'Direct')
        graphFigure.graphSummaries(voxelSummaries, 'Voxel')
        graphFigure.graphSummaries(baSummaries, 'Boundary accurate')
        graphFigure.graphSummaries(hybridSummaries, 'Hybrid')
        graphFigure.show()
        
    def printSummary(self, name, summary):
        print "{}".format(name)
        print "---------------------"
        summary.printData()
        print ""
