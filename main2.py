import numpy as np

import fileio.general as io
import fileio.voxelio as voxelio
import transfer as trans
import colordiff
from dataset import Dataset
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


class Main2:
    def __init__(self):
        self.dataset = Dataset(1, 1)
        
        self.splineInterval = [0.0, 1.0]
        self.transfer = trans.createTransferFunction(100)

        pixelX = -0.5
        screenTop = 0.9
        screenBottom = 0.2
        numPixels = 10
        self.screen = Screen(pixelX, screenTop, screenBottom, numPixels)
        self.eye = np.array([-2.0, 0.65])

        self.viewRayDelta = 0.01
        self.viewRayDeltaRef = 1e-5
        self.refTolerance = 1e-5
        
        self.voxelizationTolerance = 1e-5

        self.autoDelta = False

        self.texDimSizes = np.array([8,16,32,64,128,192,256])#,320,384,448,512])#,576,640,704,768,896,1024,1152,1280,1408,1536,1664,1792,1920,2048])
        self.numTextures = len(self.texDimSizes)

        self.numFiles = 0

    def save(self, obj):
        filename = '{0:03d}'.format(self.numFiles)
        io.save(obj, filename)
        self.numFiles += 1

    def run(self):
        renderer = Renderer(self.eye, self.screen)
        hybridRenderer = HybridRenderer(self.eye, self.screen)

        numTextures = self.numTextures
        
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
            texDimSize = self.texDimSizes[i]
            
            if voxelio.exist(self.dataset, texDimSize, texDimSize):
                samplingScalars = voxelio.read(self.dataset, texDimSize, texDimSize)
                print "Read {}x{} texture data from file".format(texDimSize, texDimSize)
            else:
                samplingScalars = refSplineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize, self.voxelizationTolerance)
                voxelio.write(self.dataset, samplingScalars)
                print "Wrote {}x{} texture data to file".format(texDimSize, texDimSize)
            
            scalarTexture = Texture2D(samplingScalars)
            
            voxelWidth = boundingBox.getHeight() / float(texDimSize)
            criterion = GeometricCriterion(self.screen.pixelWidth, voxelWidth)
            
            voxelModels[i] = VoxelModel(self.transfer, scalarTexture, boundingBox)
            baModels[i] = BoundaryAccurateModel(self.transfer, directSplineModel, voxelModels[i])
            hybridModels[i] = HybridModel(self.transfer, directSplineModel, baModels[i], criterion)

        renderData = RenderData(ModelType.REFERENCE, self.viewRayDeltaRef)
        renderData.renderResult = renderer.render(refSplineModel, self.viewRayDeltaRef)
        self.save(renderData)

        if not self.autoDelta:
            renderData = RenderData(ModelType.DIRECT, self.viewRayDelta)
            renderData.renderResult = renderer.render(directSplineModel, self.viewRayDelta)
            self.save(renderData)

        for i, texSize in enumerate(self.texDimSizes):
            if self.autoDelta:
                voxelWidth = boundingBox.getWidth() / float(texSize)
                delta = voxelWidth/2.0

                renderData = RenderData(ModelType.DIRECT, delta)
                renderData.renderResult = renderer.render(directSplineModel, delta)
                self.save(renderData)
            else:
                delta = self.viewRayDelta

            renderData = RenderData(ModelType.VOXEL, delta=delta, texSize=texSize)
            renderData.renderResult = renderer.render(voxelModels[i], delta)
            self.save(renderData)

            renderData = RenderData(ModelType.BOUNDARYACCURATE, delta=delta, texSize=texSize)
            renderData.renderResult = renderer.render(baModels[i], delta)
            self.save(renderData)

            renderData = RenderData(ModelType.HYBRID, delta=delta, texSize=texSize)
            renderData.renderResult = hybridRenderer.render(hybridModels[i], delta)
            self.save(renderData)

    def createSummaries(self):
        result = []

        for i in range(ModelType._COUNT):
            result.append([])

        files = io.findAll()
        refObj = io.load(files[0])

        for i in range(1, len(files)):
            obj = io.load(files[i])

            colorDiffs = colordiff.compare(refObj.renderResult.colors, obj.renderResult.colors)
            summary = Summary(obj, colorDiffs)
            result[obj.modelType].append(summary)

        return result

    def duplicateDirectSummary(self, summaries):
        summary = summaries[ModelType.DIRECT][0]

        for i in range(self.numTextures - 1):
            summaries[ModelType.DIRECT].append(summary)

    def plotGraphs(self):
        graphFigure = GraphFigure(self.texDimSizes)

        summaries = self.createSummaries()

        if len(summaries[ModelType.DIRECT]) == 1:
            self.duplicateDirectSummary(summaries)

        graphFigure.graphSummaries(summaries[ModelType.DIRECT], 'Direct')
        graphFigure.graphSummaries(summaries[ModelType.VOXEL], 'Voxel')
        graphFigure.graphSummaries(summaries[ModelType.BOUNDARYACCURATE], 'Boundary accurate')
        graphFigure.graphSummaries(summaries[ModelType.HYBRID], 'Hybrid')
        graphFigure.show()

    def plotPixels(self):
        pixelFigure = PixelFigure(self.texDimSizes)

        directPixels = []
        voxelPixels = []
        baPixels = []
        hybridPixels = []
        hybridVoxelRatios = []

        files = io.findAll()
        refObj = io.load(files[0])
        refPixels = refObj.renderResult.colors
        pixelFigure.refPixelsPlot.plotPixelColors(refPixels)

        for i in range(1, len(files)):
            obj = io.load(files[i])
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

    def printSummary(self):
        summaries = self.createSummaries()

        for modelSummaries in summaries:
            for modelSummary in modelSummaries:
                modelSummary.printData()
                print ""
