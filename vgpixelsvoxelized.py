import matplotlib.pyplot as plt
import numpy as np
import sys
from matplotlib.gridspec import GridSpec

import colordiff
import transfer as trans
from model.splinemodel import SplineModel
from model.voxelmodel import VoxelModel
from plotting.pixelplotter import PixelPlotter
from dataset import Dataset
from renderer import Renderer
from screen import Screen
from splineplane import SplinePlane
from texture import Texture2D


texDimSize = int(sys.argv[1])

numPixels = 200

figsize = [8, 0.5]
aspectRatio = numPixels / 50.0

figvox = plt.figure(figsize=figsize)
gsvox = GridSpec(1, 1)
axvox = figvox.add_subplot(gsvox[0, 0])

figdiff = plt.figure(figsize=figsize)
gsdiff = GridSpec(1, 1)
axdiff = figdiff.add_subplot(gsdiff[0, 0])

dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])

eye = np.array([-2.0, 0.65])
pixelX = -0.5
screenTop = 0.9
screenBottom = 0.2
screen = Screen(pixelX, screenTop, screenBottom, numPixels)

refIntersectTolerance = 1e-5
refTolerance = 1e-5
voxTolerance = 1e-5
viewRayDeltaRef = 1e-5
viewRayDeltaVoxel = 1e-2

phi = dataset.phi
rho = dataset.rho
refPhiPlane = SplinePlane(phi, splineInterval, refIntersectTolerance)
boundingBox = refPhiPlane.createBoundingBox()
tf = trans.createTransferFunction()

refSplineModel = SplineModel(tf, refPhiPlane, rho, refTolerance)
samplingScalars = refSplineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize, voxTolerance)
texture = Texture2D(samplingScalars)
voxelModel = VoxelModel(tf, texture, boundingBox)

renderer = Renderer(eye, screen)

refColors = renderer.render(refSplineModel, viewRayDeltaRef).colors
voxelColors = renderer.render(voxelModel, viewRayDeltaVoxel).colors
colorDiffs = colordiff.compare(refColors, voxelColors)

pvox = PixelPlotter(axvox)
pvox.plotPixelColors(voxelColors)
axvox.set_aspect(aspectRatio)

pdiff = PixelPlotter(axdiff)
pdiff.plotPixelColorDiffs(colorDiffs)
axdiff.set_aspect(aspectRatio)

figvox.tight_layout()
figdiff.tight_layout()

plt.figure(figvox.number)
plt.savefig("output/vg/pixelsvoxel{}.pdf".format(texDimSize), format="pdf", transparent=True)

plt.figure(figdiff.number)
plt.savefig("output/vg/pixelsvoxel{}diff.pdf".format(texDimSize), format="pdf", transparent=True)
