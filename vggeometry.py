from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

from plotting.splineplotter import SplinePlotter
from color import Color
from dataset import Dataset


fig = plt.figure(figsize=[6, 6])
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])
s = SplinePlotter(ax, splineInterval)
s.plotGrid(dataset.phi.evaluate, 10, 10, color=Color.DIRECT)

xlim = ax.get_xlim()
ylim = ax.get_ylim()
xextent = xlim[1] - xlim[0]
yextent = ylim[1] - ylim[0]
xmid = xlim[0] + xextent/2.0
ymid = ylim[0] + yextent/2.0

newextent = max(xextent, yextent) * 1.1

ticks = np.linspace(-1.0, 2.0, 13)
ax.set_xticks(ticks)
ax.set_yticks(ticks)

ax.set_xlim(xmid - newextent/2, xmid + newextent/2)
ax.set_ylim(ymid - newextent/2, ymid + newextent/2)

fig.tight_layout()
plt.savefig("output/vg/geometry.pdf", format="pdf", transparent=True)
