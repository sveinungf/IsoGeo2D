from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import numpy as np

import datasets.peakstransfer as transfer


fig = plt.figure(figsize=[8, 6])
gs = GridSpec(1, 1)
ax = fig.add_subplot(gs[0, 0])

t = transfer.createTransferFunction()

n = 100
scalars = np.linspace(0.0, 1.0, n)
colors = np.zeros((n, 4))

for i, scalar in enumerate(scalars):
    colors[i] = t(scalar)

plt.plot(scalars, colors[:, 0], color='r')
plt.plot(scalars, colors[:, 1], color='g')
plt.plot(scalars, colors[:, 2], color='b')
plt.plot(scalars, colors[:, 3], color='k')

fig.tight_layout()
plt.show()
