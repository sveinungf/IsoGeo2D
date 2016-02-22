import numpy as np
import pylab as plt
from matplotlib.patches import Rectangle

class PixelPlotter():
    def __init__(self, plot, title=None):
        self.plot = plot

        if title is not None:
            plot.set_title(title)

        plot.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
        plot.yaxis.set_major_locator(plt.NullLocator())
        
    def __getPixelPlotAxis(self, numPixels):
        return (-0.5, numPixels-0.5, 0, 1)
        
    def plotPixelColors(self, pixelColors):
        #pixelColors = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])

        numPixels = len(pixelColors)
        #self.plot.axis(self.__getPixelPlotAxis(numPixels))


        
        #for i, pixelColor in enumerate(pixelColors):
        #    r = Rectangle((i-0.5, 0), 1, 1, facecolor=tuple(pixelColor), linewidth=0)
        #    self.plot.add_patch(r)
        self.plot.imshow([pixelColors], interpolation='nearest', extent=(-0.5, numPixels+0.5, -0.5, 0.5), aspect=(2))
        #print pixelColors
    
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

    def plotRatios(self, ratios):
        colors = np.empty((len(ratios), 3))
        
        for i, ratio in enumerate(ratios):
            colors[i] = np.array([ratio, ratio, ratio])
        
        self.plotPixelColors(colors)
