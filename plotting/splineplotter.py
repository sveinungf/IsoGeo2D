import math
import numpy as np
from matplotlib.patches import Ellipse

from modelplotter import ModelPlotter

class SplinePlotter(ModelPlotter):
    def __init__(self, plot, interval):
        super(SplinePlotter, self).__init__(plot)
        
        self.interval = interval

        self.pointMarker = 'x'
        self.pointColor = 'k'
        
    def __generatePoints2var(self, f, xInputs, yInputs):
        xOutput = []
        yOutput = []
        
        for i in range(len(xInputs)):
            fResult = f(xInputs[i], yInputs[i])
            xOutput.append(fResult[0])
            yOutput.append(fResult[1])
        
        return [xOutput, yOutput]

    def plotOutline(self, f, color='0.5', linewidth=1.0):
        interval = self.interval
        precision = 100

        lows = np.ones(precision) * interval[0]
        highs = np.ones(precision) * interval[1]
        params = np.linspace(interval[0], interval[1], precision)

        [geomX, geomY] = self.__generatePoints2var(f, lows, params)
        self.plot.plot(geomX, geomY, color=color, linewidth=linewidth)

        [geomX, geomY] = self.__generatePoints2var(f, highs, params)
        self.plot.plot(geomX, geomY, color=color, linewidth=linewidth)

        [geomX, geomY] = self.__generatePoints2var(f, params, lows)
        self.plot.plot(geomX, geomY, color=color, linewidth=linewidth)

        [geomX, geomY] = self.__generatePoints2var(f, params, highs)
        self.plot.plot(geomX, geomY, color=color, linewidth=linewidth)

    def plotGrid(self, f, m, n, color='0.5'):
        interval = self.interval
        precision = 100
        
        vLines = np.linspace(interval[0], interval[1], m)
        hLines = np.linspace(interval[0], interval[1], n)
        
        for vLine in vLines:
            paramsX = [vLine] * precision
            paramsY = np.linspace(interval[0], interval[1], precision)
            
            [geomX, geomY] = self.__generatePoints2var(f, paramsX, paramsY)
            
            self.plot.plot(geomX, geomY, color=color)
        for hLine in hLines:
            paramsX = np.linspace(interval[0], interval[1], precision)
            paramsY = [hLine] * precision
            
            [geomX, geomY] = self.__generatePoints2var(f, paramsX, paramsY)
            
            self.plot.plot(geomX, geomY, color=color)

    def plotPoints(self, points):
        for point in points:
            self.plot.plot(point[0], point[1], marker=self.pointMarker, color=self.pointColor)

    def plotEllipse(self, ellipse):
        point = tuple(ellipse.point)
        degrees = math.degrees(ellipse.angle)
        e = Ellipse(point, ellipse.width, ellipse.height, degrees, fill=False)

        self.plot.add_artist(e)
