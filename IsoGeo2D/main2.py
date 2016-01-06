import numpy as np

import fileio.voxelio as voxelio
import colordiff
import transfer as trans
from model.boundaryaccuratemodel import BoundaryAccurateModel
from model.hybridmodel import HybridModel
from model.splinemodel import SplineModel
from model.voxelmodel import VoxelModel
from plotting.graphfigure import GraphFigure
from plotting.pixelfigure import PixelFigure
from voxelcriterion.geometriccriterion import GeometricCriterion
from dataset import Dataset
from ray import Ray2D
from splineplane import SplinePlane
from summary import Summary
from texture import Texture2D


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
        self.viewRayDelta = 0.005
        self.viewRayDeltaRef = 0.001
        self.refTolerance = 0.001
        
        self.voxelizationTolerance = 1e-5
        
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

        texDimSizes = np.array([64, 128, 192, 256, 320, 384, 448, 512])
        
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
            hybridModels[i] = HybridModel(self.transfer, directSplineModel, voxelModels[i], criterion)

        pixels = self.createPixels(numPixels)
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels
        
        refPixelColors = np.zeros((numPixels, 4))
        directPixelColors = np.zeros((numPixels, 4))
        voxelPixelColors = np.zeros((numTextures, numPixels, 4))
        baPixelColors = np.zeros((numTextures, numPixels, 4))
        hybridPixelColors = np.zeros((numTextures, numPixels, 4))
        
        hybridVoxelRatios = np.empty((numTextures, numPixels))
        
        maxRefSamplePoints = 0
        maxDirectSamplePoints = 0
        maxVoxelSamplePoints = np.zeros(numTextures)
        maxBaSamplePoints = np.zeros(numTextures)
        maxHybridSamplePoints = np.zeros(numTextures)
        
        for i, pixel in enumerate(pixels):
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)
            
            viewRay.splineIntersects = directSplineModel.phiPlane.findTwoIntersections(viewRay)
            viewRay.boundingBoxIntersects = boundingBox.findTwoIntersections(viewRay)

            result = refSplineModel.raycast(viewRay, self.viewRayDeltaRef)
            if result.color is not None:
                refPixelColors[i] = result.color
                maxRefSamplePoints = max(result.samples, maxRefSamplePoints)

            result = directSplineModel.raycast(viewRay, self.viewRayDelta)
            if result.color is not None:
                directPixelColors[i] = result.color
                maxDirectSamplePoints = max(result.samples, maxDirectSamplePoints)

            for j in range(numTextures):
                result = voxelModels[j].raycast(viewRay, self.viewRayDelta)
                if result.color is not None:
                    voxelPixelColors[j][i] = result.color
                    maxVoxelSamplePoints[j] = max(result.samples, maxVoxelSamplePoints[j])

                result = baModels[j].raycast(viewRay, self.viewRayDelta)
                if result.color is not None:
                    baPixelColors[j][i] = result.color
                    maxBaSamplePoints[j] = max(result.samples, maxBaSamplePoints[j])

                result = hybridModels[j].raycast(viewRay, self.viewRayDelta)
                if result.color is not None:
                    hybridPixelColors[j][i] = result.color
                    maxHybridSamplePoints[j] = max(result.samples, maxHybridSamplePoints[j])

                    hybridVoxelRatios[j][i] = hybridModels[j].voxelRatio()

        figure = PixelFigure(texDimSizes)

        figure.refPixelsPlot.plotPixelColors(refPixelColors)
        figure.directPixelsPlot.plotPixelColors(directPixelColors)
        
        self.printRefSummary(maxRefSamplePoints)
        
        directDiffs = colordiff.compare(refPixelColors, directPixelColors)
        figure.directDiffsPlot.plotPixelColorDiffs(directDiffs)
        directSummary = Summary(directDiffs, maxDirectSamplePoints)
        self.printSummary("Direct", directSummary)
        
        voxelDiffs = np.empty((numTextures, numPixels))
        baDiffs = np.empty((numTextures, numPixels))
        hybridDiffs = np.empty((numTextures, numPixels))
        
        for i in range(numTextures):
            figure.voxelPixelsPlots[i].plotPixelColors(voxelPixelColors[i])
            figure.baPixelsPlots[i].plotPixelColors(baPixelColors[i])
            figure.hybridPixelsPlots[i].plotPixelColors(hybridPixelColors[i])
            
            voxelDiffs[i] = colordiff.compare(refPixelColors, voxelPixelColors[i])
            baDiffs[i] = colordiff.compare(refPixelColors, baPixelColors[i])
            hybridDiffs[i] = colordiff.compare(refPixelColors, hybridPixelColors[i])
            
            figure.voxelDiffsPlots[i].plotPixelColorDiffs(voxelDiffs[i])
            figure.baDiffsPlots[i].plotPixelColorDiffs(baDiffs[i])
            figure.hybridDiffsPlots[i].plotPixelColorDiffs(hybridDiffs[i])
            
            figure.hybridVoxelRatioPlots[i].plotRatios(hybridVoxelRatios[i])

        voxelSummaries = []
        baSummaries = []
        hybridSummaries = []
        
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            summary = Summary(voxelDiffs[i], maxVoxelSamplePoints[i])
            voxelSummaries.append(summary)
            self.printSummary("Voxel ({}x{})".format(texDimSize, texDimSize), summary)
            
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            summary = Summary(baDiffs[i], maxBaSamplePoints[i])
            baSummaries.append(summary)
            self.printSummary("Boundary accurate ({}x{})".format(texDimSize, texDimSize), summary)
            
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            summary = Summary(hybridDiffs[i], maxHybridSamplePoints[i])
            hybridSummaries.append(summary)
            self.printSummary("Hybrid ({}x{})".format(texDimSize, texDimSize), summary)

        figure.show()

        graphFigure = GraphFigure(texDimSizes)
        graphFigure.graphDirectSummary(directSummary)
        graphFigure.graphSummaries(voxelSummaries, 'Voxel')
        graphFigure.graphSummaries(baSummaries, 'Boundary accurate')
        graphFigure.graphSummaries(hybridSummaries, 'Hybrid')
        graphFigure.show()
        
    def printRefSummary(self, maxSamplePoints):
        print "Reference"
        print "---------------------"
        print "max #S = {}".format(maxSamplePoints)
        print ""
        
    def printSummary(self, name, summary):
        print "{} color diffs".format(name)
        print "---------------------"
        summary.printData()
        print ""
    
def run(eyeX=None):
    if eyeX != None:
        main = Main2(eyeX)
    else:
        main = Main2()
        
    main.run()

if __name__ == "__main__":
    run()
