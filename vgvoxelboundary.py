from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

from model.splinemodel import SplineModel
from plotting.splineplotter import SplinePlotter
from plotting.voxelplotter import VoxelPlotter
from dataset import Dataset
from splineplane import SplinePlane


fig = plt.figure(figsize=[6, 6])
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

ax.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
ax.yaxis.set_major_locator(plt.NullLocator())

texDimSize = 32
newtonTolerance = 1e-5
dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])

phi = dataset.phi
rho = dataset.rho
phiPlane = SplinePlane(phi, splineInterval, newtonTolerance)
boundingBox = phiPlane.createBoundingBox()
splineModel = SplineModel(None, phiPlane, rho)
samplingScalars = splineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize, newtonTolerance)

s = SplinePlotter(ax, splineInterval)
s.plotOutline(phi.evaluate, color='b')

v = VoxelPlotter(ax)
v.plotScalars(samplingScalars, boundingBox, facecolor=None, edgecolor='g')

ax.set_xlim([-0.12, 0.19])
ax.set_ylim([-0.04, 0.27])

plt.savefig("output/vg/voxelboundary.pdf", format="pdf")
