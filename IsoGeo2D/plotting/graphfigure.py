import matplotlib.pyplot as plt
import numpy as np

from graphplotter import GraphPlotter

class GraphFigure:
    def __init__(self, texDimSizes):
        self.texDimSizes = texDimSizes

        fig = plt.figure()
        self.fig = fig

        mainGrid = plt.GridSpec(2, 2)

        ax = fig.add_subplot(mainGrid[0, 0])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Max')
        ax.set_xticks(texDimSizes)
        self.maxGraph = GraphPlotter(ax)

        ax = fig.add_subplot(mainGrid[0, 1])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Mean')
        ax.set_xticks(texDimSizes)
        self.meanGraph = GraphPlotter(ax)

        ax = fig.add_subplot(mainGrid[1, 0])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Var')
        ax.set_xticks(texDimSizes)
        self.varGraph = GraphPlotter(ax)

    def __graphSummaries(self, maxes, means, vars, label):
        self.maxGraph.plotGraph(self.texDimSizes, maxes, label)
        self.meanGraph.plotGraph(self.texDimSizes, means, label)
        self.varGraph.plotGraph(self.texDimSizes, vars, label)

    def graphDirectSummary(self, summary):
        numPoints = len(self.texDimSizes)
        maxes = np.ones(numPoints) * summary.max
        means = np.ones(numPoints) * summary.mean
        vars = np.ones(numPoints) * summary.var

        self.__graphSummaries(maxes, means, vars, 'Direct')

    def graphVoxelSummaries(self, summaries):
        maxes = []
        means = []
        vars = []

        for summary in summaries:
            maxes.append(summary.max)
            means.append(summary.mean)
            vars.append(summary.var)

        self.__graphSummaries(maxes, means, vars, 'Voxel')

    def show(self):
        handles, labels = self.meanGraph.plot.get_legend_handles_labels()
        self.fig.legend(handles, labels, loc=4)
        self.fig.show()
