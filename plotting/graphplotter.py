class GraphPlotter:
    def __init__(self, plot):
        self.plot = plot

    def plotGraph(self, x, y, label):
        self.plot.plot(x, y, label=label)
