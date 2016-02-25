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


numPixels = 200

figsize = [8, 0.5]
aspectRatio = numPixels / 50.0

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
screen = Screen(pixelX, screenTop, screenBottom, numPixels)

refIntersectTolerance = 1e-5
refTolerance = 1e-5
viewRayDeltaRef = 1e-5
directIntersectTolerance = 1e-3
viewRayDeltaDirect = 1e-2

phi = dataset.phi
rho = dataset.rho
refPhiPlane = SplinePlane(phi, splineInterval, refIntersectTolerance)
directPhiPlane = SplinePlane(phi, splineInterval, directIntersectTolerance)
tf = trans.createTransferFunction()

refSplineModel = SplineModel(tf, refPhiPlane, rho, refTolerance)
directSplineModel = SplineModel(tf, directPhiPlane, rho)

renderer = Renderer(eye, screen)

refColors = renderer.render(refSplineModel, viewRayDeltaRef).colors
directColors = renderer.render(directSplineModel, viewRayDeltaDirect).colors
colorDiffs = colordiff.compare(refColors, directColors)

pref = PixelPlotter(axref)
pref.plotPixelColors(refColors)
axref.set_aspect(aspectRatio)

pdir = PixelPlotter(axdir)
pdir.plotPixelColors(directColors)
axdir.set_aspect(aspectRatio)

pdiff = PixelPlotter(axdiff)
pdiff.plotPixelColorDiffs(colorDiffs)
axdiff.set_aspect(aspectRatio)

figref.tight_layout()
figdir.tight_layout()
figdiff.tight_layout()

plt.figure(figref.number)
plt.savefig("output/vg/pixelsreference.pdf", format="pdf", transparent=True)

plt.figure(figdir.number)
plt.savefig("output/vg/pixelsdirect.pdf", format="pdf", transparent=True)

plt.figure(figdiff.number)
plt.savefig("output/vg/pixelsdirectdiff.pdf", format="pdf", transparent=True)
