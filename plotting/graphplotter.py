class GraphPlotter:
    def __init__(self, plot):
        self.plot = plot

    def plotGraph(self, x, y, label, color=None, marker=None):
        self.plot.plot(x, y, label=label, color=color, marker=marker, markeredgecolor=color, markerfacecolor='None')
