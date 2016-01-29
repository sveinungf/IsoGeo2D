from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

from model.splinemodel import SplineModel
from plotting.paramplotter import ParamPlotter
from plotting.splineplotter import SplinePlotter
from color import Color
from dataset import Dataset
from splineplane import SplinePlane


fig = plt.figure(figsize=[6, 6])
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

fig2 = plt.figure(figsize=[6, 6])
gs2 = GridSpec(1, 1)
ax2 = fig2.add_subplot(gs[0, 0])

texDimSize = 8
newtonTolerance = 1e-5
dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])

phi = dataset.phi
rho = dataset.rho
phiPlane = SplinePlane(phi, splineInterval, newtonTolerance)
boundingBox = phiPlane.createBoundingBox()
splineModel = SplineModel(None, phiPlane, rho)

s = SplinePlotter(ax, splineInterval)
s.pointMarker = 'o'
s.pointColor = Color.POINT

p = ParamPlotter(ax2, splineInterval)
p.pointMarker = 'o'
p.pointColor = Color.POINT

s.plotGrid(phi.evaluate, 10, 10, color=Color.DIRECT)
p.plotGrid(10, 10)
s.plotBoundingBox(boundingBox, edgecolor=Color.BOUNDINGBOX)

samplingScalars = splineModel.generateScalarMatrix(boundingBox, texDimSize, texDimSize, newtonTolerance, paramPlotter=p, geomPlotter=s)

ax.set_xlim([-0.3, 1.1])
ax.set_ylim([-0.2, 1.2])

fig.tight_layout()
fig2.tight_layout()

plt.figure(fig.number)
plt.savefig("output/vg/voxelizinggeom.pdf", format="pdf", transparent=True)

plt.figure(fig2.number)
plt.savefig("output/vg/voxelizingparam.pdf", format="pdf", transparent=True)
