import numpy as np
import pylab as plt
from matplotlib.patches import Rectangle

class PixelPlotter():
    def __init__(self, plot, title):
        self.plot = plot
        plot.set_title(title)
        plot.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
        plot.yaxis.set_major_locator(plt.NullLocator())
        
    def __getPixelPlotAxis(self, numPixels):
        return (-0.5, numPixels-0.5, 0, 1)
        
    def plotPixelColors(self, pixelColors):
        numPixels = len(pixelColors)
        self.plot.axis(self.__getPixelPlotAxis(numPixels))
        
        for i, pixelColor in enumerate(pixelColors):
            r = Rectangle((i-0.5, 0), 1, 1, facecolor=tuple(pixelColor), linewidth=0)
            self.plot.add_patch(r)
    
    def plotPixelColorDiffs(self, colorDiffs):
        colors = np.empty((len(colorDiffs), 3))
        
        for i, colorDiff in enumerate(colorDiffs):
            if colorDiff <= 1.0:
                colors[i] = np.array([0.75, 0.75, 0.75])
            elif colorDiff <= 5.0:
                colors[i] = np.array([0.0, 0.0, 1.0])
            elif colorDiff <= 10.0:
                colors[i] = np.array([0.0, 1.0, 0.0])
            else:
                colors[i] = np.array([1.0, 0.0, 0.0])
                
        self.plotPixelColors(colors)
