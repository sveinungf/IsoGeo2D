import matplotlib.pyplot as plt

from graphplotter import GraphPlotter

class GraphFigure:
    def __init__(self):
        fig = plt.figure()
        self.fig = fig

        mainGrid = plt.GridSpec(1, 1)

        ax = fig.add_subplot(mainGrid[0, 0])
        ax.set_xlabel('Texture size (n x n)')
        ax.set_ylabel('Mean')
        self.meanGraph = GraphPlotter(ax)

    def graphVoxelSummaries(self, texDimSizes, summaries):
        means = []

        for summary in summaries:
            means.append(summary.mean)

        self.meanGraph.plotGraph(texDimSizes, means)

    def show(self):
        self.fig.show()
