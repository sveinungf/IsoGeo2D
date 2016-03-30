from matplotlib.gridspec import GridSpec
import matplotlib.pyplot as plt
import sys

import summary
from fileio.filehandler import FileHandler
from plotting.graphplotter import GraphPlotter
from dataset import Dataset
from modeltype import ModelType


rhoNo = int(sys.argv[1])
phiNo = int(sys.argv[2])
tfNo = int(sys.argv[3])

plotWindow = False

figNames = ['max', 'mean', 'var']
colors = ['b', 'g', 'r', 'c', 'm']
markers = ['x', '+', 'o', 's', 'v']
legendNames = {
    ModelType.DIRECT : 'Direct',
    ModelType.VOXEL : 'Voxelized',
    ModelType.BOUNDARYACCURATE : 'Boundary accurate',
    ModelType.HYBRID : 'Hybrid (direct/voxelized)',
    ModelType.BAHYBRID : 'Hybrid (direct/boundary accurate)'
}


figs = []
gss = []
axs = []
plotters = []
legendFig = plt.figure(figsize=[6, 6])

for i in range(3):
    fig = plt.figure(figsize=[6, 6])
    gs = GridSpec(1, 1)
    ax = fig.add_subplot(gs[0, 0])
    ax.set_xscale('log', basex=2)
    ax.set_yscale('log', basey=2)
    ax.set_xlabel('Texture size')
    ax.set_ylabel('Color difference ($\Delta E$)')

    figs.append(fig)
    gss.append(gs)
    axs.append(ax)
    plotters.append(GraphPlotter(ax))

dataset = Dataset(rhoNo, phiNo, tfNo)

fileHandler = FileHandler()
fileHandler.setFiledir('output/results/{},{},{}'.format(rhoNo, phiNo, tfNo))

summaries = summary.createSummaries(fileHandler, dataset)

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

    for j in range(3):
        plotters[j].plotGraph(texDimSizes, stats[j], legendNames[i], color, marker)

handles, labels = plotters[0].plot.get_legend_handles_labels()
legendFig.legend(handles, labels)

if plotWindow:
    plt.show()
else:
    filenameA = 'output/vg/graph_{},{},{}'.format(rhoNo, phiNo, tfNo)

    for i in range(3):
        figs[i].tight_layout()

        plt.figure(figs[i].number)
        filename = '{}_{}.pdf'.format(filenameA, figNames[i])
        plt.savefig(filename, format='pdf', transparent=True)

    plt.figure(legendFig.number)
    filename = '{}_legend.pdf'.format(filenameA)
    plt.savefig(filename, format='pdf', transparent=True)
