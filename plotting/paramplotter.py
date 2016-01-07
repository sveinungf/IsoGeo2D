class ParamPlotter():
    def __init__(self, plot):
        self.plot = plot
        
    def plotPoints(self, points):
        for point in points:
            self.plot.plot(point[0], point[1], marker='x', color='k')
