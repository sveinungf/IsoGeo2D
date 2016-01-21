import numpy as np


class ParamPlotter():
    def __init__(self, plot, interval, precision=100):
        self.interval = interval
        self.plot = plot
        self.precision = precision

    def plotGrid(self, m, n):
        interval = self.interval
        precision = self.precision

        vLines = np.linspace(interval[0], interval[1], m)
        hLines = np.linspace(interval[0], interval[1], n)
        lineColor = '0.5'
        ax = self.plot

        for vLine in vLines:
            paramsX = [vLine] * precision
            paramsY = np.linspace(interval[0], interval[1], precision)

            ax.plot(paramsX, paramsY, color=lineColor)
        for hLine in hLines:
            paramsX = np.linspace(interval[0], interval[1], precision)
            paramsY = [hLine] * precision

            ax.plot(paramsX, paramsY, color=lineColor)

    def plotPoints(self, points):
        for point in points:
            self.plot.plot(point[0], point[1], marker='x', color='k')

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
