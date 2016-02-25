import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

import datasets.peakstransfer as transfer
#import transfer


fig = plt.figure(figsize=(8, 6))
gs = GridSpec(4, 1)

axes = []

for i in range(4):
    axes.append(fig.add_subplot(4, 1, i+1))

t = transfer.createTransferFunction()

n = 100
scalars = np.linspace(0.0, 1.0, n)
colors = np.zeros((n, 4))

for i, scalar in enumerate(scalars):
    colors[i] = t(scalar)

    # Hack to make top and bottom visible
    for c in range(4):
        if colors[i][c] < 0.01:
            colors[i][c] = 0.01
        elif colors[i][c] > 0.97:
            colors[i][c] = 0.97

for i in range(4):
    axes[i].plot(scalars, colors[:, i], color='w', linewidth=2.0)
    axes[i].set_xlim([0.0, 1.0])
    axes[i].set_ylim([0.0, 1.0])

    axes[i].set_yticks((0.0, 1.0))
    axes[i].set_yticklabels(['0.0', '1.0']) # Workaround for the ticks being converted to integers

plotlim = plt.xlim() + plt.ylim()

top = [[1.0, 0.0, 0.0, 1.0], [0.0, 1.0, 0.0, 1.0], [0.0, 0.0, 1.0, 1.0], [0.0, 0.0, 0.0, 1.0]]
bottom = [[0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 0.0]]
#black = [0.0, 0.0, 0.0, 1.0]

m = 60
n = 8
light = [0.6] * 3
dark = [0.25] * 3

qq = []

for j in range(n/2):
    qr = []
    qs = []

    for i in range(m/2):
        qr.append(light)
        qr.append(dark)
        qs.append(dark)
        qs.append(light)

    qq.append(qr)
    qq.append(qs)

chessboard = np.asarray(qq)

axes[3].imshow(chessboard, interpolation='nearest', extent=plotlim)

for i in range(4):
    axes[i].imshow([[top[i]],[bottom[i]]], interpolation='bicubic', extent=plotlim)
    axes[i].set_aspect('auto')

fig.tight_layout()
plt.savefig("output/vg/transfer.pdf", format="pdf", transparent=True)
