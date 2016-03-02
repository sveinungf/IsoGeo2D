from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import sys

import summary
from fileio.filehandler import FileHandler
from plotting.graphplotter import GraphPlotter
from dataset import Dataset
from modeltype import ModelType


datasetRho = int(sys.argv[1])
datasetPhi = int(sys.argv[2])

figs = []
gss = []
axs = []
plotters = []
graphNames = ['max', 'mean', 'var']

for i in range(3):
    fig = plt.figure(figsize=[6, 6])
    gs = GridSpec(1, 1)
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xscale('log', basex=2)
    ax.set_yscale('log', basey=2)

    figs.append(fig)
    gss.append(gs)
    axs.append(ax)
    plotters.append(GraphPlotter(ax))

dataset = Dataset(datasetRho, datasetPhi)

fileHandler = FileHandler()
fileHandler.setFiledir('output/results/{},{}'.format(datasetRho, datasetPhi))

summaries = summary.createSummaries(fileHandler, dataset)

colors = ['b', 'g', 'r', 'c', 'm']
markers = ['x', '+', 'o', 's', 'v']

texDimSizes = []

for voxelSummary in summaries[ModelType.VOXEL]:
    texDimSizes.append(voxelSummary.renderData.texSize)

for i in range(1, len(summaries)):
    modelSummaries = summaries[i]

    color = colors[i-1]
    marker = markers[i-1]
    maxes = []
    means = []
    vars = []

    for modelSummary in modelSummaries:
        maxes.append(modelSummary.max)
        means.append(modelSummary.mean)
        vars.append(modelSummary.var)

    stats = []
    stats.append(maxes)
    stats.append(means)
    stats.append(vars)

    for i in range(3):
        plotters[i].plotGraph(texDimSizes, stats[i], 'label', color, marker)

for i in range(3):
    figs[i].tight_layout()

    plt.figure(figs[i].number)
    filename = 'output/vg/graph_{},{}_{}.pdf'.format(datasetRho, datasetPhi, graphNames[i])
    plt.savefig(filename, format='pdf', transparent=True)
