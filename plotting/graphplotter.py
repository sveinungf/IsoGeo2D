class GraphPlotter:
    def __init__(self, plot):
        self.plot = plot

    def plotGraph(self, x, y, label, color=None, marker=None):
        self.plot.plot(x, y, label=label, color=color, marker=marker, markeredgecolor=color, markerfacecolor='None')

    def plotThresholdX(self, x, color='k', linestyle='solid'):
        self.plot.axvline(x, color=color, linestyle=linestyle)

    def plotThresholdY(self, y, color='k', linestyle='solid'):
        self.plot.axhline(y, color=color, linestyle=linestyle)
