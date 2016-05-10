import numpy as np
import sys

import fileio.voxelio as voxelio
import colordiff
from dataset import Dataset
from fileio.filehandler import FileHandler
from model.boundaryaccuratemodel import BoundaryAccurateModel
from model.hybridmodel import HybridModel
from model.splinemodel import SplineModel
from model.voxelmodel import VoxelModel
from plotting.graphfigure import GraphFigure
from plotting.pixelfigure import PixelFigure
from hybridrenderer import HybridRenderer
from modeltype import ModelType
from renderdata import RenderData
from renderer import Renderer
from screen import Screen
from splineplane import SplinePlane
from summary import Summary
from texture import Texture2D
from voxelcriterion.geometriccriterion import GeometricCriterion


def printflush(string):
    sys.stdout.write(string)
    sys.stdout.flush()


class Main2:
    def __init__(self):
        self.splineInterval = [0.0, 1.0]

        screenBottom = np.array([-0.5, 0.2])
        screenTop = np.array([-0.5, 0.9])
        numPixels = 100
        self.screen = Screen(screenBottom, screenTop, numPixels)
        self.eye = np.array([-1.2, 0.65])

        self.viewRayDelta = 1e-5
        self.refTolerance = 1e-5

        self.voxelizationTolerance = 1e-5

        self.texDimSizes = np.array([8, 16, 32, 64, 128, 256, 512, 1024])
        self.numTextures = len(self.texDimSizes)

        self.numFiles = 0
        self.fileHandler = FileHandler()

    @staticmethod
    def filedir(dataset):
        return 'output/results/{},{},{}'.format(dataset.rhoNumber, dataset.phiNumber, dataset.tfNumber)

    def save(self, dataset, obj):
        filedir = self.filedir(dataset)
        filename = '{0:03d}'.format(self.numFiles)

        self.fileHandler.setFiledir(filedir)
        self.fileHandler.save(obj, filename)

        self.numFiles += 1

    def run(self, rhoNo=1, phiNo=1, tfNo=1):
        dataset = Dataset(rhoNo, phiNo, tfNo)
        self.numFiles = 0

        renderer = Renderer(self.eye, self.screen)

        numTextures = self.numTextures

        rho = dataset.rho
        phi = dataset.phi
        tf = dataset.tf
        phiPlane = SplinePlane(phi, self.splineInterval, 1e-5)

        boundingBox = phiPlane.createBoundingBox()

        refSplineModel = SplineModel(tf, phiPlane, rho, self.refTolerance)
        voxelModels = np.empty(numTextures, dtype=object)

        for i in range(numTextures):
            texDimSize = self.texDimSizes[i]

            if voxelio.exist(dataset, texDimSize, texDimSize):
                samplingScalars = voxelio.read(dataset, texDimSize, texDimSize)
                print "Read {}x{} texture data from file".format(texDimSize, texDimSize)
            else:
                samplingScalars = refSplineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize,
                                                                      self.voxelizationTolerance)
                voxelio.write(dataset, samplingScalars)
                print "Wrote {}x{} texture data to file".format(texDimSize, texDimSize)

            scalarTexture = Texture2D(samplingScalars)

            voxelModels[i] = VoxelModel(tf, scalarTexture, boundingBox)

        printflush("Rendering reference... ")
        renderData = RenderData(ModelType.REFERENCE, self.viewRayDelta)
        renderData.renderResult = renderer.render(refSplineModel, self.viewRayDelta)
        self.save(dataset, renderData)
        print "Done!"

        for i, texSize in enumerate(self.texDimSizes):
            delta = self.viewRayDelta

            printflush("Rendering voxelized ({0}x{0})...".format(texSize))
            renderData = RenderData(ModelType.VOXEL, delta=delta, texSize=texSize)
            renderData.renderResult = renderer.render(voxelModels[i], delta)
            self.save(dataset, renderData)
            print "Done!"

    def createSummaries(self, dataset):
        result = []

        for i in range(ModelType._COUNT):
            result.append([])

        filedir = self.filedir(dataset)
        self.fileHandler.setFiledir(filedir)

        files = self.fileHandler.findAll()
        refObj = self.fileHandler.load(files[0])

        for i in range(1, len(files)):
            obj = self.fileHandler.load(files[i])

            colorDiffs = colordiff.compare(refObj.renderResult.colors, obj.renderResult.colors)
            summary = Summary(obj, colorDiffs)
            result[obj.modelType].append(summary)

        return result

    def duplicateDirectSummary(self, summaries):
        summary = summaries[ModelType.DIRECT][0]

        for i in range(self.numTextures - 1):
            summaries[ModelType.DIRECT].append(summary)

    def plotGraphs(self, rhoNo=1, phiNo=1, tfNo=1):
        dataset = Dataset(rhoNo, phiNo, tfNo)
        graphFigure = GraphFigure(self.texDimSizes)

        summaries = self.createSummaries(dataset)

        if len(summaries[ModelType.DIRECT]) == 1:
            self.duplicateDirectSummary(summaries)

        graphFigure.graphSummaries(summaries[ModelType.VOXEL], 'Voxel')
        graphFigure.show()

    def plotPixels(self, rhoNo=1, phiNo=1, tfNo=1):
        dataset = Dataset(rhoNo, phiNo, tfNo)
        pixelFigure = PixelFigure(self.texDimSizes)

        directPixels = []
        voxelPixels = []
        baPixels = []
        hybridPixels = []
        hybridVoxelRatios = []
        baHybridPixels = []
        baHybridVoxelRatios = []

        filedir = self.filedir(dataset)
        self.fileHandler.setFiledir(filedir)

        files = self.fileHandler.findAll()
        refObj = self.fileHandler.load(files[0])
        refPixels = refObj.renderResult.colors
        pixelFigure.refPixelsPlot.plotPixelColors(refPixels)

        for i in range(1, len(files)):
            obj = self.fileHandler.load(files[i])
            objPixels = obj.renderResult.colors

            if obj.modelType == ModelType.DIRECT:
                directPixels.append(objPixels)
            elif obj.modelType == ModelType.VOXEL:
                voxelPixels.append(objPixels)
            elif obj.modelType == ModelType.BOUNDARYACCURATE:
                baPixels.append(objPixels)
            elif obj.modelType == ModelType.HYBRID:
                hybridPixels.append(objPixels)
                hybridVoxelRatios.append(obj.renderResult.ratios)
            elif obj.modelType == ModelType.BAHYBRID:
                baHybridPixels.append(objPixels)
                baHybridVoxelRatios.append(obj.renderResult.ratios)

        if len(directPixels) == 1:
            pixels = directPixels[0]
            colorDiffs = colordiff.compare(refPixels, pixels)

            pixelFigure.directPixelsPlot.plotPixelColors(pixels)
            pixelFigure.directDiffsPlot.plotPixelColorDiffs(colorDiffs)

        for i in range(len(voxelPixels)):
            pixels = voxelPixels[i]
            colorDiffs = colordiff.compare(refPixels, pixels)
            pixelFigure.voxelPixelsPlots[i].plotPixelColors(pixels)
            pixelFigure.voxelDiffsPlots[i].plotPixelColorDiffs(colorDiffs)

            pixels = baPixels[i]
            colorDiffs = colordiff.compare(refPixels, pixels)
            pixelFigure.baPixelsPlots[i].plotPixelColors(pixels)
            pixelFigure.baDiffsPlots[i].plotPixelColorDiffs(colorDiffs)

            pixels = hybridPixels[i]
            colorDiffs = colordiff.compare(refPixels, pixels)
            pixelFigure.hybridPixelsPlots[i].plotPixelColors(pixels)
            pixelFigure.hybridDiffsPlots[i].plotPixelColorDiffs(colorDiffs)
            pixelFigure.hybridVoxelRatioPlots[i].plotRatios(hybridVoxelRatios[i])

        pixelFigure.show()

    def printSummary(self, rhoNo=1, phiNo=1, tfNo=1):
        dataset = Dataset(rhoNo, phiNo, tfNo)
        summaries = self.createSummaries(dataset)

        for modelSummaries in summaries:
            for modelSummary in modelSummaries:
                modelSummary.printData()
                print ""
