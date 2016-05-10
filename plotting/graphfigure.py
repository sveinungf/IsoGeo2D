import matplotlib.pyplot as plt
import numpy as np

from graphplotter import GraphPlotter

class GraphFigure:
    def __init__(self, texDimSizes, invertXAxis=False):
        self.texDimSizes = texDimSizes

        fig = plt.figure()
        self.fig = fig

        mainGrid = plt.GridSpec(2, 2)

        ax = fig.add_subplot(mainGrid[0, 0])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Max')
        ax.set_xscale('log', basex=2)
        ax.set_yscale('log', basey=2)
        if invertXAxis:
            ax.invert_xaxis()
        self.maxGraph = GraphPlotter(ax)

        ax = fig.add_subplot(mainGrid[0, 1])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Mean')
        ax.set_xscale('log', basex=2)
        ax.set_yscale('log', basey=2)
        if invertXAxis:
            ax.invert_xaxis()
        self.meanGraph = GraphPlotter(ax)

        ax = fig.add_subplot(mainGrid[1, 0])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Var')
        ax.set_xscale('log', basex=2)
        ax.set_yscale('log', basey=2)
        if invertXAxis:
            ax.invert_xaxis()
        self.varGraph = GraphPlotter(ax)

        self.colors = ['b', 'g', 'r', 'c', 'm']
        self.markers = ['x', '+', 'o', 's', 'v']
        self.currentIndex = 0

    def __graphMaxMeanVars(self, maxes, means, vars, label, color, marker):
        self.maxGraph.plotGraph(self.texDimSizes, maxes, label, color, marker)
        self.meanGraph.plotGraph(self.texDimSizes, means, label, color, marker)
        self.varGraph.plotGraph(self.texDimSizes, vars, label, color, marker)

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

        color = self.colors[self.currentIndex]
        marker = self.markers[self.currentIndex]
        self.__graphMaxMeanVars(maxes, means, vars, label, color, marker)

        self.currentIndex += 1
        if self.currentIndex == len(self.colors):
            self.currentIndex = 0

    def show(self):
        handles, labels = self.meanGraph.plot.get_legend_handles_labels()
        self.fig.legend(handles, labels, loc=4)
        self.fig.show()
