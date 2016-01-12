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
        ax.set_xscale('log')
        ax.set_yscale('log')
        self.maxGraph = GraphPlotter(ax)

        ax = fig.add_subplot(mainGrid[0, 1])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Mean')
        ax.set_xscale('log')
        ax.set_yscale('log')
        self.meanGraph = GraphPlotter(ax)

        ax = fig.add_subplot(mainGrid[1, 0])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Var')
        ax.set_xscale('log')
        ax.set_yscale('log')
        self.varGraph = GraphPlotter(ax)

    def __graphMaxMeanVars(self, maxes, means, vars, label):
        self.maxGraph.plotGraph(self.texDimSizes, maxes, label)
        self.meanGraph.plotGraph(self.texDimSizes, means, label)
        self.varGraph.plotGraph(self.texDimSizes, vars, label)

    def graphDirectSummary(self, summary):
        numPoints = len(self.texDimSizes)
        maxes = np.ones(numPoints) * summary.max
        means = np.ones(numPoints) * summary.mean
        vars = np.ones(numPoints) * summary.var

        self.__graphMaxMeanVars(maxes, means, vars, 'Direct')

    def graphSummaries(self, summaries, label):
        maxes = []
        means = []
        vars = []

        for summary in summaries:
            maxes.append(summary.max)
            means.append(summary.mean)
            vars.append(summary.var)

        self.__graphMaxMeanVars(maxes, means, vars, label)

    def show(self):
        handles, labels = self.meanGraph.plot.get_legend_handles_labels()
        self.fig.legend(handles, labels, loc=4)
        self.fig.show()
