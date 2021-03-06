from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

from model.splinemodel import SplineModel
from plotting.splineplotter import SplinePlotter
from plotting.voxelplotter import VoxelPlotter
from color import Color
from dataset import Dataset
from splineplane import SplinePlane


fig = plt.figure(figsize=[6, 6])
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

ax.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
ax.yaxis.set_major_locator(plt.NullLocator())

texDimSize = 32
newtonTolerance = 1e-5
dataset = Dataset(1, 1, 1)
splineInterval = np.array([0.0, 1.0])

phi = dataset.phi
rho = dataset.rho
phiPlane = SplinePlane(phi, splineInterval, newtonTolerance)
boundingBox = phiPlane.createBoundingBox()
splineModel = SplineModel(None, phiPlane, rho)
samplingScalars = splineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize, newtonTolerance)

s = SplinePlotter(ax, splineInterval)
s.plotOutline(phi.evaluate, color=Color.DIRECT, linewidth=2.0)

v = VoxelPlotter(ax)
v.plotScalars(samplingScalars, boundingBox, facecolor=None, edgecolor='k')

size = 0.96
left = -0.56
bottom = 0.01
ax.set_xlim([left, left + size])
ax.set_ylim([bottom, bottom + size])

fig.tight_layout()
plt.savefig("output/vg/voxelboundary.pdf", format="pdf", transparent=True)
