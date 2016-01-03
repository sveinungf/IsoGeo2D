import matplotlib.pyplot as plt

from graphplotter import GraphPlotter

class GraphFigure:
    def __init__(self):
        fig = plt.figure()
        self.fig = fig

        mainGrid = plt.GridSpec(2, 2)

        ax = fig.add_subplot(mainGrid[0, 0])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Max')
        self.maxGraph = GraphPlotter(ax)

        ax = fig.add_subplot(mainGrid[0, 1])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Mean')
        self.meanGraph = GraphPlotter(ax)

        ax = fig.add_subplot(mainGrid[1, 0])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Var')
        self.varGraph = GraphPlotter(ax)

    def graphVoxelSummaries(self, texDimSizes, summaries):
        maxes = []
        means = []
        vars = []

        for summary in summaries:
            maxes.append(summary.max)
            means.append(summary.mean)
            vars.append(summary.var)

        self.maxGraph.plotGraph(texDimSizes, maxes)
        self.meanGraph.plotGraph(texDimSizes, means)
        self.varGraph.plotGraph(texDimSizes, vars)

    def show(self):
        self.fig.show()
