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

        self.refTolerance = 1e-5

        self.voxelizationTolerance = 1e-5

        self.viewRayDeltaRef = 0.0005
        self.viewRayDeltas = np.array([0.128, 0.064, 0.032, 0.016, 0.008, 0.004, 0.002, 0.001])

        self.allMethods = False
        self.texDimSize = 128
        self.numTextures = 1

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
        hybridRenderer = HybridRenderer(self.eye, self.screen)

        numTextures = self.numTextures

        rho = dataset.rho
        phi = dataset.phi
        tf = dataset.tf
        phiPlane = SplinePlane(phi, self.splineInterval, 1e-5)

        boundingBox = phiPlane.createBoundingBox()

        refSplineModel = SplineModel(tf, phiPlane, rho, self.refTolerance)
        directSplineModel = SplineModel(tf, phiPlane, rho)
        voxelModels = np.empty(numTextures, dtype=object)
        baModels = np.empty(numTextures, dtype=object)
        hybridModels = np.empty(numTextures, dtype=object)
        baHybridModels = np.empty(numTextures, dtype=object)

        for i in range(numTextures):
            texDimSize = self.texDimSize

            if voxelio.exist(dataset, texDimSize, texDimSize):
                samplingScalars = voxelio.read(dataset, texDimSize, texDimSize)
                print "Read {}x{} texture data from file".format(texDimSize, texDimSize)
            else:
                samplingScalars = refSplineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize,
                                                                      self.voxelizationTolerance)
                voxelio.write(dataset, samplingScalars)
                print "Wrote {}x{} texture data to file".format(texDimSize, texDimSize)

            scalarTexture = Texture2D(samplingScalars)

            voxelWidth = boundingBox.getHeight() / float(texDimSize)
            criterion = GeometricCriterion(self.screen.pixelWidth, voxelWidth)

            voxelModels[i] = VoxelModel(tf, scalarTexture, boundingBox)
            baModels[i] = BoundaryAccurateModel(tf, directSplineModel, voxelModels[i])
            hybridModels[i] = HybridModel(tf, directSplineModel, voxelModels[i], criterion)
            baHybridModels[i] = HybridModel(tf, directSplineModel, baModels[i], criterion)

        printflush("Rendering reference... ")
        renderData = RenderData(ModelType.REFERENCE, self.viewRayDeltaRef)
        renderData.renderResult = renderer.render(refSplineModel, self.viewRayDeltaRef)
        self.save(dataset, renderData)
        print "Done!"

        for delta in self.viewRayDeltas:
            texSize = self.texDimSize

            printflush("Rendering direct (delta = {})...".format(delta))
            renderData = RenderData(ModelType.DIRECT, delta)
            renderData.renderResult = renderer.render(directSplineModel, delta)
            self.save(dataset, renderData)
            print "Done!"

            printflush("Rendering voxelized (delta = {})...".format(delta))
            renderData = RenderData(ModelType.VOXEL, delta=delta, texSize=texSize)
            renderData.renderResult = renderer.render(voxelModels[i], delta)
            self.save(dataset, renderData)
            print "Done!"

            if self.allMethods:
                printflush("Rendering boundary accurate (delta = {})...".format(delta))
                renderData = RenderData(ModelType.BOUNDARYACCURATE, delta=delta, texSize=texSize)
                renderData.renderResult = renderer.render(baModels[i], delta)
                self.save(dataset, renderData)
                print "Done!"

                printflush("Rendering hybrid (delta = {})...".format(delta))
                renderData = RenderData(ModelType.HYBRID, delta=delta, texSize=texSize)
                renderData.renderResult = hybridRenderer.render(hybridModels[i], delta)
                self.save(dataset, renderData)
                print "Done!"

                printflush("Rendering hybrid (delta = {})...".format(delta))
                renderData = RenderData(ModelType.BAHYBRID, delta=delta, texSize=texSize)
                renderData.renderResult = hybridRenderer.render(baHybridModels[i], delta)
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
        graphFigure = GraphFigure(self.viewRayDeltas, True)

        summaries = self.createSummaries(dataset)

        if len(summaries[ModelType.DIRECT]) == 1:
            self.duplicateDirectSummary(summaries)

        graphFigure.graphSummaries(summaries[ModelType.DIRECT], 'Direct')
        graphFigure.graphSummaries(summaries[ModelType.VOXEL], 'Voxel')

        if self.allMethods:
            graphFigure.graphSummaries(summaries[ModelType.BOUNDARYACCURATE], 'Boundary accurate')
            graphFigure.graphSummaries(summaries[ModelType.HYBRID], 'Hybrid')
            graphFigure.graphSummaries(summaries[ModelType.BAHYBRID], 'Hybrid (BA)')

        graphFigure.show()

    def printSummary(self, rhoNo=1, phiNo=1, tfNo=1):
        dataset = Dataset(rhoNo, phiNo, tfNo)
        summaries = self.createSummaries(dataset)

        for modelSummaries in summaries:
            for modelSummary in modelSummaries:
                modelSummary.printData()
                print ""
