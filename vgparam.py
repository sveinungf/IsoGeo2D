import matplotlib.pyplot as plt
import numpy as np

from plotting.paramplotter import ParamPlotter
from dataset import Dataset


def transfer(x):
    return np.array([x, x, x, 1.0])

plt.figure(figsize=[6, 6])
dataset = Dataset(1, 1)
splineInterval = np.array([0.0, 1.0])
p = ParamPlotter(plt, splineInterval)
p.plotScalarField(dataset.rho, transfer)
plt.savefig("output/vg/param.pdf", format="pdf")
