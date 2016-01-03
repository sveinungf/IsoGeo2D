class GraphPlotter:
    def __init__(self, plot):
        self.plot = plot

    def plotGraph(self, x, y):
        self.plot.set_xticks(x)
        self.plot.plot(x, y)
