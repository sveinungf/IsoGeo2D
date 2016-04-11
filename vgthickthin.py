from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

from model.boundaryaccuratemodel import BoundaryAccurateModel
from model.splinemodel import SplineModel
from model.voxelmodel import VoxelModel
from plotting.splineplotter import SplinePlotter
from plotting.voxelplotter import VoxelPlotter
from color import Color
from dataset import Dataset
from ray import Ray2D
from renderer import Renderer
from screen import Screen
from splineplane import SplinePlane
from textureX import Texture2D


fig = plt.figure(figsize=[6, 6])
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

fig2 = plt.figure(figsize=[6, 6])
gs2 = GridSpec(1, 1)
ax2 = fig2.add_subplot(gs2[0, 0])

ax.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
ax.yaxis.set_major_locator(plt.NullLocator())

ax2.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
ax2.yaxis.set_major_locator(plt.NullLocator())

texDimSize = 16
newtonTolerance = 1e-5
dataset = Dataset(1, 1, 0)
splineInterval = np.array([0.0, 1.0])

phi = dataset.phi
rho = dataset.rho
phiPlane = SplinePlane(phi, splineInterval, newtonTolerance)
boundingBox = phiPlane.createBoundingBox()
splineModel = SplineModel(dataset.tf, phiPlane, rho, 1e-5)
samplingScalars = splineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize, newtonTolerance)

s = SplinePlotter(ax, splineInterval)
s.plotOutline(phi.evaluate, color=Color.DIRECT, linewidth=2.0)

s2 = SplinePlotter(ax2, splineInterval)
s2.plotOutline(phi.evaluate, color=Color.DIRECT, linewidth=2.0)

v = VoxelPlotter(ax)
v.plotScalars(samplingScalars, boundingBox, facecolor=None, edgecolor='k')

v2 = VoxelPlotter(ax2)
v2.plotScalars(samplingScalars, boundingBox, facecolor=None, edgecolor='k')

scalarTexture = Texture2D(samplingScalars)
voxelModel = VoxelModel(dataset.tf, scalarTexture, boundingBox)
baModel = BoundaryAccurateModel(dataset.tf, splineModel, voxelModel)

eye = np.array([0.95, -1.4])
screenBottom = np.array([0.965, -1.0])
screenTop = np.array([0.945, -1.0])
numPixels = 2
screen = Screen(screenBottom, screenTop, numPixels)

renderer = Renderer(eye, screen)
renderer.plotViewRays = False

for pixel in screen.pixels:
    viewRay = Ray2D(eye, pixel, 10, screen.pixelWidth)
    s.plotViewRay(viewRay, [0, 10])
    s2.plotViewRay(viewRay, [0, 10])

renderer.render(baModel, 0.05, s)

renderer.render(splineModel, 0.05, s2)
renderer.render(baModel, 0.05, s2)

size = 0.52
left = 0.68
bottom = -0.13
ax.set_xlim([left, left + size])
ax.set_ylim([bottom, bottom + size])

ax2.set_xlim([left, left + size])
ax2.set_ylim([bottom, bottom + size])

fig.tight_layout()
fig2.tight_layout()

plt.figure(fig.number)
plt.savefig("output/vg/bathin.pdf", format="pdf", transparent=True)

plt.figure(fig2.number)
plt.savefig("output/vg/bathick.pdf", format="pdf", transparent=True)
