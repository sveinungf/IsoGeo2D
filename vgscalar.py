import matplotlib.pyplot as plt
import numpy as np

from plotting.paramplotter import ParamPlotter
from dataset import Dataset


def transfer(x):
    return np.array([x, x, x, 1.0])

fig = plt.figure(figsize=[6, 6])
dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])
p = ParamPlotter(plt, splineInterval)
p.plotScalarField(dataset.rho, transfer)

fig.tight_layout()
plt.savefig("output/vg/scalar.pdf", format="pdf", transparent=True)
