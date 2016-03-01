import matplotlib.pyplot as plt
import numpy as np
import sys
from matplotlib.gridspec import GridSpec

import colordiff
import datasets.peakstransfer as trans
from fileio.filehandler import FileHandler
from model.boundaryaccuratemodel import BoundaryAccurateModel
from model.hybridmodel import HybridModel
from model.splinemodel import SplineModel
from model.voxelmodel import VoxelModel
from plotting.pixelplotter import PixelPlotter
from voxelcriterion.geometriccriterion import GeometricCriterion
from dataset import Dataset
from hybridrenderer import HybridRenderer
from renderer import Renderer
from screen import Screen
from splineplane import SplinePlane
from texture import Texture2D


modelChoice = int(sys.argv[1])
texDimSize = int(sys.argv[2])

numPixels = 100

figsize = [8, 0.5]
aspectRatio = numPixels / 50.0

fig = plt.figure(figsize=figsize)
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

figdiff = plt.figure(figsize=figsize)
gsdiff = GridSpec(1, 1)
axdiff = figdiff.add_subplot(gsdiff[0, 0])

figratio = plt.figure(figsize=figsize)
gsratio = GridSpec(1, 1)
axratio = figratio.add_subplot(gsratio[0, 0])

dataset = Dataset(1, 2)
splineInterval = np.array([0.0, 1.0])

eye = np.array([-1.2, 0.65])
pixelX = -0.5
screenTop = 0.9
screenBottom = 0.2
screen = Screen(pixelX, screenTop, screenBottom, numPixels)

refIntersectTolerance = 1e-5
refTolerance = 1e-5
voxTolerance = 1e-5
viewRayDelta = 1e-3

phi = dataset.phi
rho = dataset.rho
refPhiPlane = SplinePlane(phi, splineInterval, refIntersectTolerance)
boundingBox = refPhiPlane.createBoundingBox()
tf = trans.createTransferFunction()

refSplineModel = SplineModel(tf, refPhiPlane, rho, refTolerance)
directSplineModel = SplineModel(tf, refPhiPlane, rho)
voxelModel = None

voxelWidth = boundingBox.getHeight() / float(texDimSize)
criterion = GeometricCriterion(screen.pixelWidth, voxelWidth)

if modelChoice != 0:
    samplingScalars = refSplineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize, voxTolerance)
    texture = Texture2D(samplingScalars)
    voxelModel = VoxelModel(tf, texture, boundingBox)

model = None
name = ''

if modelChoice == 0:
    # Direct
    model = directSplineModel
    name = 'Direct'
elif modelChoice == 1:
    # Voxel
    model = voxelModel
    name = 'Voxel{}'.format(texDimSize)
elif modelChoice == 2:
    # Boundary accurate
    model = BoundaryAccurateModel(tf, directSplineModel, voxelModel)
    name = 'Ba{}'.format(texDimSize)
elif modelChoice == 3:
    # Hybrid (Direct/Voxelized)
    model = HybridModel(tf, directSplineModel, voxelModel, criterion)
    name = 'Hybrid{}'.format(texDimSize)
elif modelChoice == 4:
    # Hybrid (Direct/Boundary accurate)
    baModel = BoundaryAccurateModel(tf, directSplineModel, voxelModel)
    model = HybridModel(tf, directSplineModel, baModel, criterion)
    name = 'BaHybrid{}'.format(texDimSize)

ratios = None

if modelChoice == 3 or modelChoice == 4:
    renderer = HybridRenderer(eye, screen)
    renderResult = renderer.render(model, viewRayDelta)
    ratios = renderResult.ratios
else:
    renderer = Renderer(eye, screen)
    renderResult = renderer.render(model, viewRayDelta)

colors = renderResult.colors

fileHandler = FileHandler()
fileHandler.setFiledir('output/vgresults')
refObj = fileHandler.load('reference.pkl')

refColors = refObj.renderResult.colors
colorDiffs = colordiff.compare(refColors, colors)

p = PixelPlotter(ax)
p.plotPixelColors(colors)
ax.set_aspect(aspectRatio)

pdiff = PixelPlotter(axdiff)
pdiff.plotPixelColorDiffs(colorDiffs)
axdiff.set_aspect(aspectRatio)

fig.tight_layout()
figdiff.tight_layout()

plt.figure(fig.number)
plt.savefig("output/vg/pixels{}.pdf".format(name), format="pdf", transparent=True)

plt.figure(figdiff.number)
plt.savefig("output/vg/pixels{}Diff.pdf".format(name), format="pdf", transparent=True)

if modelChoice == 3 or modelChoice == 4:
    pratio = PixelPlotter(axratio)
    pratio.plotRatios(ratios)
    axratio.set_aspect(aspectRatio)

    figratio.tight_layout()

    plt.figure(figratio.number)
    plt.savefig("output/vg/pixels{}Ratio.pdf".format(name), format="pdf", transparent=True)
