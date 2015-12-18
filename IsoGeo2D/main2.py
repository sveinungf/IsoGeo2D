import numpy as np

import fileio.voxelio as voxelio
import colordiff
import transfer as trans
from model.boundaryhybridmodel import BoundaryHybridModel
from model.hybridmodel import HybridModel
from model.splinemodel import SplineModel
from model.voxelmodel import VoxelModel
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
        self.viewRayDelta = 0.1
        self.viewRayDeltaRef = 0.001
        self.refTolerance = 0.001
        
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
        numPixels = self.numPixels
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels

        texDimSizes = np.array([32, 64, 128, 256, 512])
        
        numTextures = len(texDimSizes)
                
        figure = PixelFigure(texDimSizes)
        
        rho = self.dataset.rho
        phi = self.dataset.phi
        phiPlane = SplinePlane(phi, self.splineInterval, 0.00001)
        
        boundingBox = phiPlane.createBoundingBox()
        
        refSplineModel = SplineModel(self.transfer, phiPlane, rho, self.refTolerance)
        directSplineModel = SplineModel(self.transfer, phiPlane, rho)
        voxelModels = np.empty(numTextures, dtype=object)
        bhModels = np.empty(numTextures, dtype=object)
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
            bhModels[i] = BoundaryHybridModel(self.transfer, directSplineModel, voxelModels[i])
            hybridModels[i] = HybridModel(self.transfer, directSplineModel, voxelModels[i], criterion)

        pixels = self.createPixels(numPixels)
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels
        
        refPixelColors = np.empty((numPixels, 4))
        directPixelColors = np.empty((numPixels, 4))
        voxelPixelColors = np.empty((numTextures, numPixels, 4))
        bhPixelColors = np.empty((numTextures, numPixels, 4))
        hybridPixelColors = np.empty((numTextures, numPixels, 4))
        
        hybridVoxelRatios = np.empty((numTextures, numPixels))
        
        maxRefSamplePoints = 0
        maxDirectSamplePoints = 0
        maxVoxelSamplePoints = np.zeros(numTextures)
        maxBhSamplePoints = np.zeros(numTextures)
        maxHybridSamplePoints = np.zeros(numTextures)
        
        backgroundColor = np.array([0.0, 0.0, 0.0, 0.0])
        
        for i, pixel in enumerate(pixels):
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)
            
            intersections = directSplineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                [refSamplePoints, refPixelColors[i]] = refSplineModel.raycast(viewRay, intersections, self.viewRayDeltaRef)
                [directSamplePoints, directPixelColors[i]] = directSplineModel.raycast(viewRay, intersections, self.viewRayDelta)
                
                maxRefSamplePoints = max(refSamplePoints, maxRefSamplePoints)
                maxDirectSamplePoints = max(directSamplePoints, maxDirectSamplePoints)
                
                for j in range(numTextures):
                    [voxelSamplePoints, voxelPixelColors[j][i]] = voxelModels[j].raycast(viewRay, intersections, self.viewRayDelta)
                    [bhSamplePoints, bhPixelColors[j][i]] = bhModels[j].raycast(viewRay, intersections, self.viewRayDelta)
                    [hybridSamplePoints, hybridPixelColors[j][i]] = hybridModels[j].raycast(viewRay, intersections, self.viewRayDelta)
                    
                    hybridVoxelRatios[j][i] = hybridModels[j].voxelRatio()
                    
                    maxVoxelSamplePoints[j] = max(voxelSamplePoints, maxVoxelSamplePoints[j])
                    maxBhSamplePoints[j] = max(bhSamplePoints, maxBhSamplePoints[j])
                    maxHybridSamplePoints[j] = max(hybridSamplePoints, maxHybridSamplePoints[j])
            else:
                refPixelColors[i] = backgroundColor
                directPixelColors[i] = backgroundColor
                
                for j in range(numTextures):
                    voxelPixelColors[j][i] = backgroundColor
                    bhPixelColors[j][i] = backgroundColor
                    hybridPixelColors[j][i] = backgroundColor
        
        figure.refPixelsPlot.plotPixelColors(refPixelColors)
        figure.directPixelsPlot.plotPixelColors(directPixelColors)
        
        self.printRefSummary(maxRefSamplePoints)
        
        directDiffs = colordiff.compare(refPixelColors, directPixelColors)
        figure.directDiffsPlot.plotPixelColorDiffs(directDiffs)
        directSummary = Summary(directDiffs, maxDirectSamplePoints)
        self.printSummary("Direct", directSummary)
        
        voxelDiffs = np.empty((numTextures, numPixels))
        bhDiffs = np.empty((numTextures, numPixels))
        hybridDiffs = np.empty((numTextures, numPixels))
        
        for i in range(numTextures):
            figure.voxelPixelsPlots[i].plotPixelColors(voxelPixelColors[i])
            figure.bhPixelsPlots[i].plotPixelColors(bhPixelColors[i])
            figure.hybridPixelsPlots[i].plotPixelColors(hybridPixelColors[i])
            
            voxelDiffs[i] = colordiff.compare(refPixelColors, voxelPixelColors[i])
            bhDiffs[i] = colordiff.compare(refPixelColors, bhPixelColors[i])
            hybridDiffs[i] = colordiff.compare(refPixelColors, hybridPixelColors[i])
            
            figure.voxelDiffsPlots[i].plotPixelColorDiffs(voxelDiffs[i])
            figure.bhDiffsPlots[i].plotPixelColorDiffs(bhDiffs[i])
            figure.hybridDiffsPlots[i].plotPixelColorDiffs(hybridDiffs[i])
            
            figure.hybridVoxelRatioPlots[i].plotRatios(hybridVoxelRatios[i])
        
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            summary = Summary(voxelDiffs[i], maxVoxelSamplePoints[i])
            self.printSummary("Voxel ({}x{})".format(texDimSize, texDimSize), summary)
            
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            summary = Summary(bhDiffs[i], maxBhSamplePoints[i])
            self.printSummary("Boundary hybrid ({}x{})".format(texDimSize, texDimSize), summary)
            
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            summary = Summary(hybridDiffs[i], maxHybridSamplePoints[i])
            self.printSummary("Hybrid ({}x{})".format(texDimSize, texDimSize), summary)
            
        figure.draw()
        
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
