import math
import numpy as np
from matplotlib.patches import Ellipse

from modelplotter import ModelPlotter

class SplinePlotter(ModelPlotter):
    def __init__(self, plot, interval):
        super(SplinePlotter, self).__init__(plot)
        
        self.interval = interval
        
    def __generatePoints2var(self, f, xInputs, yInputs):
        xOutput = []
        yOutput = []
        
        for i in range(len(xInputs)):
            fResult = f(xInputs[i], yInputs[i])
            xOutput.append(fResult[0])
            yOutput.append(fResult[1])
        
        return [xOutput, yOutput]

    def plotGrid(self, f, m, n):
        interval = self.interval
        precision = 100
        
        vLines = np.linspace(interval[0], interval[1], m)
        hLines = np.linspace(interval[0], interval[1], n)
        lineColor = '0.5'
        
        for vLine in vLines:
            paramsX = [vLine] * precision
            paramsY = np.linspace(interval[0], interval[1], precision)
            
            [geomX, geomY] = self.__generatePoints2var(f, paramsX, paramsY)
            
            self.plot.plot(geomX, geomY, color=lineColor)
        for hLine in hLines:
            paramsX = np.linspace(interval[0], interval[1], precision)
            paramsY = [hLine] * precision
            
            [geomX, geomY] = self.__generatePoints2var(f, paramsX, paramsY)
            
            self.plot.plot(geomX, geomY, color=lineColor)

    def plotPoints(self, points):
        for point in points:
            self.plot.plot(point[0], point[1], marker='x', color='k')

    def plotEllipse(self, ellipse):
        point = tuple(ellipse.point)
        degrees = math.degrees(ellipse.angle)
        e = Ellipse(point, ellipse.width, ellipse.height, degrees, fill=False)

        self.plot.add_artist(e)
