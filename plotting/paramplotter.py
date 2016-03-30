import numpy as np


class ParamPlotter():
    def __init__(self, plot, interval, precision=100):
        self.interval = interval
        self.plot = plot
        self.precision = precision

        self.connectPoints = False
        self.pointMarker = 'x'
        self.pointColor = 'k'
        self.gridColor = '0.5'

    def plotGrid(self, m, n):
        interval = self.interval
        precision = self.precision

        vLines = np.linspace(interval[0], interval[1], m)
        hLines = np.linspace(interval[0], interval[1], n)
        ax = self.plot

        for vLine in vLines:
            paramsX = [vLine] * precision
            paramsY = np.linspace(interval[0], interval[1], precision)

            ax.plot(paramsX, paramsY, color=self.gridColor)
        for hLine in hLines:
            paramsX = np.linspace(interval[0], interval[1], precision)
            paramsY = [hLine] * precision

            ax.plot(paramsX, paramsY, color=self.gridColor)

    def plotPoints(self, points):
        if self.connectPoints:
            actualPoints = []

            for point in points:
                if point is not None:
                    actualPoints.append(point)

            actualPoints = np.asarray(actualPoints)

            self.plot.plot(actualPoints[:, 0], actualPoints[:, 1], marker=self.pointMarker, color=self.pointColor)
        else:
            for point in points:
                if point is not None:
                    self.plot.plot(point[0], point[1], marker=self.pointMarker, color=self.pointColor)

    def plotScalarField(self, rho, transfer):
        interval = self.interval
        precision = self.precision

        uRange = np.linspace(interval[0], interval[1], precision)
        vRange = np.linspace(interval[1], interval[0], precision)

        img = []

        for v in vRange:
            row = []

            for u in uRange:
                x = rho.evaluate(u,v)[0]

                if x > 1.0:
                    x = 1.0

                row.append(transfer(x))

            img.append(row)

        ax = self.plot
        return ax.imshow(img, aspect='auto', extent=(interval[0], interval[1], interval[0], interval[1]))
