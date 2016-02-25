from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

from model.splinemodel import SplineModel
from plotting.textureplotter import TexturePlotter
from dataset import Dataset
from splineplane import SplinePlane
from texture import Texture2D


fig = plt.figure(figsize=[6, 6])
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

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

voxelWidth = boundingBox.getWidth() / float(texDimSize)
voxelHeight = boundingBox.getHeight() / float(texDimSize)

tex = Texture2D(samplingScalars)

t = TexturePlotter(ax)
t.plotScalars(tex, boundingBox, facecolor=None, edgecolor='k', nonresidentcolor='#ff3333')
t.plotBoundingBox(boundingBox, linewidth=2.0, edgecolor='b')

ax.set_xlim([boundingBox.left - voxelWidth, boundingBox.right + voxelWidth])
ax.set_ylim([boundingBox.bottom - voxelHeight, boundingBox.top + voxelHeight])

ax.set_xticks((boundingBox.left, boundingBox.right))
ax.set_yticks((boundingBox.bottom, boundingBox.top))
ax.set_xticklabels(['0.0', '1.0'])
ax.set_yticklabels(['0.0', '1.0'])

fig.tight_layout()
plt.savefig("output/vg/texture.pdf", format="pdf", transparent=True)
