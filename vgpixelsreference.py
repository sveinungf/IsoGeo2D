import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

import datasets.peakstransfer as trans
from fileio.filehandler import FileHandler
from model.splinemodel import SplineModel
from plotting.pixelplotter import PixelPlotter
from dataset import Dataset
from modeltype import ModelType
from renderdata import RenderData
from renderer import Renderer
from screen import Screen
from splineplane import SplinePlane


numPixels = 100

figsize = [8, 0.5]
aspectRatio = numPixels / 50.0

figref = plt.figure(figsize=figsize)
gsref = GridSpec(1, 1)
axref = figref.add_subplot(gsref[0, 0])

dataset = Dataset(1, 2)
splineInterval = np.array([0.0, 1.0])

eye = np.array([-1.2, 0.65])
pixelX = -0.5
screenTop = 0.9
screenBottom = 0.2
screen = Screen(pixelX, screenTop, screenBottom, numPixels)

refIntersectTolerance = 1e-5
refTolerance = 1e-5
viewRayDeltaRef = 1e-5

phi = dataset.phi
rho = dataset.rho
refPhiPlane = SplinePlane(phi, splineInterval, refIntersectTolerance)
tf = trans.createTransferFunction()

refSplineModel = SplineModel(tf, refPhiPlane, rho, refTolerance)

renderer = Renderer(eye, screen)
renderData = RenderData(ModelType.REFERENCE, viewRayDeltaRef)
renderData.renderResult = renderer.render(refSplineModel, viewRayDeltaRef)

fileHandler = FileHandler()
fileHandler.setFiledir('output/vgresults')
fileHandler.save(renderData, 'reference')

pref = PixelPlotter(axref)
pref.plotPixelColors(renderData.renderResult.colors)
axref.set_aspect(aspectRatio)

figref.tight_layout()

plt.figure(figref.number)
plt.savefig("output/vg/pixelsReference.pdf", format="pdf", transparent=True)
