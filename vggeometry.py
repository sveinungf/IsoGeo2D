import matplotlib.pyplot as plt
import numpy as np

from plotting.splineplotter import SplinePlotter
from color import Color
from dataset import Dataset


fig = plt.figure(figsize=[6, 6])
dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])
s = SplinePlotter(plt, splineInterval)
s.plotGrid(dataset.phi.evaluate, 10, 10, color=Color.DIRECT)

fig.tight_layout()
plt.savefig("output/vg/geometry.pdf", format="pdf", transparent=True)
