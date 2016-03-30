class GraphPlotter:
    def __init__(self, plot):
        self.plot = plot

    def plotGraph(self, x, y, label, color=None, marker=None):
        self.plot.plot(x, y, label=label, color=color, marker=marker, markeredgecolor=color, markerfacecolor='None')

    def plotThresholdY(self, fromX, toX, y, color='k', linestyle='solid'):
        self.plot.plot([fromX, toX], [y, y], color=color, linestyle=linestyle)
