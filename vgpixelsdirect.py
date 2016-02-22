import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

import colordiff
import transfer as trans
from model.splinemodel import SplineModel
from plotting.pixelplotter import PixelPlotter
from dataset import Dataset
from renderer import Renderer
from screen import Screen
from splineplane import SplinePlane


figsize = [8, 0.5]

figref = plt.figure(figsize=figsize)
gsref = GridSpec(1, 1)
axref = figref.add_subplot(gsref[0, 0])

figdir = plt.figure(figsize=figsize)
gsdir = GridSpec(1, 1)
axdir = figdir.add_subplot(gsdir[0, 0])

figdiff = plt.figure(figsize=figsize)
gsdiff = GridSpec(1, 1)
axdiff = figdiff.add_subplot(gsdiff[0, 0])

dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])

eye = np.array([-2.0, 0.65])
pixelX = -0.5
screenTop = 0.9
screenBottom = 0.2
numPixels = 200
screen = Screen(pixelX, screenTop, screenBottom, numPixels)

intersectTolerance = 1e-1
refTolerance = 1e-1
viewRayDeltaRef = 1e-1
viewRayDeltaDirect = 1e-1

phi = dataset.phi
rho = dataset.rho
phiPlane = SplinePlane(phi, splineInterval, intersectTolerance)
tf = trans.createTransferFunction()

refSplineModel = SplineModel(tf, phiPlane, rho, refTolerance)
directSplineModel = SplineModel(tf, phiPlane, rho)

renderer = Renderer(eye, screen)

refRenderResult = renderer.render(refSplineModel, viewRayDeltaRef)
directRenderResult = renderer.render(directSplineModel, viewRayDeltaDirect)
colorDiffs = colordiff.compare(refRenderResult.colors, directRenderResult.colors)

pref = PixelPlotter(axref)
pref.plotPixelColors(refRenderResult.colors)
axref.set_aspect('equal')

pdir = PixelPlotter(axdir)
pdir.plotPixelColors(directRenderResult.colors)

pdiff = PixelPlotter(axdiff)
pdiff.plotPixelColorDiffs(colorDiffs)

figref.tight_layout()
figdir.tight_layout()
figdiff.tight_layout()

plt.figure(figref.number)
plt.savefig("output/vg/pixelsreference.pdf", format="pdf", transparent=True)

plt.figure(figdir.number)
plt.savefig("output/vg/pixelsdirect.pdf", format="pdf", transparent=True)

plt.figure(figdiff.number)
plt.savefig("output/vg/pixelsdirectdiff.pdf", format="pdf", transparent=True)
