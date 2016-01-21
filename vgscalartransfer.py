from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

from plotting.paramplotter import ParamPlotter
from dataset import Dataset
import transfer


fig = plt.figure(figsize=[8, 6])
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])
t = transfer.createTransferFunction(1000)

p = ParamPlotter(ax, splineInterval, precision=1000)
cax = p.plotScalarField(dataset.rho, t)
ax.set_aspect('equal')
cbar = fig.colorbar(cax, ticks=[0.0, 1.0])
cbar.ax.set_yticklabels(['0.0', '1.0']) # Workaround for the ticks being converted to integers
cbar.solids.set_edgecolor('face') # Removes buggy lines in vector graphics

fig.tight_layout()
plt.savefig("output/vg/scalartransfer.pdf", format="pdf", transparent=True)
