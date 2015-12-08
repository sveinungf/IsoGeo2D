import numpy as np

import colordiff
import splineexample
import transfer as trans
from plotter.pixelfigure import PixelFigure
from voxelcriterion.geometriccriterion import GeometricCriterion
from hybridmodel import HybridModel
from ray import Ray2D
from splinemodel import SplineModel
from splineplane import SplinePlane
from texture import Texture2D
from voxelmodel import VoxelModel

class Main2:
    def __init__(self):
        self.splineInterval = [0, 0.99999]
        self.rho = splineexample.createRho()
        self.phi = splineexample.createPhi()
        self.phiPlane = SplinePlane(self.phi, self.splineInterval, 0.00001)
        self.transfer = trans.createTransferFunction(100)

        self.numPixels = 10
        self.pixelX = -0.5
        self.screenTop = 0.90
        self.screenBottom = 0.2
        
        self.eye = np.array([-2.0, 0.65])
        self.viewRayDelta = 0.1
        self.viewRayDeltaRef = 0.001
        self.refTolerance = 0.000000001
        
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

        texDimSizes = np.array([8, 16, 32])
        numTextures = len(texDimSizes)
                
        figure = PixelFigure(texDimSizes)
        
        boundingBox = self.phiPlane.createBoundingBox()
        
        splineModel = SplineModel(self.phiPlane, self.rho, self.transfer)
        voxelModels = np.empty(numTextures, dtype=object)
        hybridModels = np.empty(numTextures, dtype=object)
        
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            samplingScalars = splineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize)
            scalarTexture = Texture2D(samplingScalars)
            
            voxelWidth = boundingBox.getHeight() / float(texDimSize)
            criterion = GeometricCriterion(pixelWidth, voxelWidth)
            
            voxelModels[i] = VoxelModel(scalarTexture, self.transfer, boundingBox)
            hybridModels[i] = HybridModel(splineModel, voxelModels[i], criterion)

        pixels = self.createPixels(numPixels)
        pixelWidth = (self.screenTop-self.screenBottom) / numPixels
        
        refPixelColors = np.empty((numPixels, 4))
        directPixelColors = np.empty((numPixels, 4))
        voxelPixelColors = np.empty((numTextures, numPixels, 4))
        hybridPixelColors = np.empty((numTextures, numPixels, 4))
        
        backgroundColor = np.array([0.0, 0.0, 0.0, 0.0])
        
        for i, pixel in enumerate(pixels):
            viewRay = Ray2D(self.eye, pixel, 10, pixelWidth)
            
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                refPixelColors[i] = splineModel.raycast(viewRay, intersections, self.viewRayDeltaRef, tolerance=self.refTolerance)
                directPixelColors[i] = splineModel.raycast(viewRay, intersections, self.viewRayDelta)
                
                for j in range(numTextures):
                    voxelPixelColors[j][i] = voxelModels[j].raycast(viewRay, intersections, self.viewRayDelta)
                    hybridPixelColors[j][i] = hybridModels[j].raycast(viewRay, intersections, self.viewRayDelta)
            else:
                refPixelColors[i] = backgroundColor
                directPixelColors[i] = backgroundColor
                
                for j in range(numTextures):
                    voxelPixelColors[j][i] = backgroundColor
                    hybridPixelColors[j][i] = backgroundColor
        
        figure.refPixelsPlot.plotPixelColors(refPixelColors)
        figure.directPixelsPlot.plotPixelColors(directPixelColors)
        
        directDiff = colordiff.compare(refPixelColors, directPixelColors)
        figure.directDiffsPlot.plotPixelColorDiffs(directDiff.colordiffs)
        
        for i in range(numTextures):
            figure.voxelPixelsPlots[i].plotPixelColors(voxelPixelColors[i])
            figure.hybridPixelsPlots[i].plotPixelColors(hybridPixelColors[i])
            
            voxelDiff = colordiff.compare(refPixelColors, voxelPixelColors[i])
            hybridDiff = colordiff.compare(refPixelColors, hybridPixelColors[i])
            
            figure.voxelDiffsPlots[i].plotPixelColorDiffs(voxelDiff.colordiffs)
            figure.hybridDiffsPlots[i].plotPixelColorDiffs(hybridDiff.colordiffs)
        
        figure.draw()
    
def run():
    main = Main2()
    main.run()

if __name__ == "__main__":
    run()
