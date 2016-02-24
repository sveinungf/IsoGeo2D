import numpy as np
import pylab as plt
from matplotlib.patches import Rectangle

class PixelPlotter():
    def __init__(self, plot, title=None, aspectRatio=None):
        self.plot = plot
        self.aspectRatio = aspectRatio

        # Default
        if aspectRatio is not None:
            plot.imshow([[[1.0, 1.0, 1.0]]], interpolation='nearest', extent=(-0.5, 0.5, -0.5, 0.5))
            plot.set_aspect(1.0 / aspectRatio)

        if title is not None:
            plot.set_title(title)

        plot.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
        plot.yaxis.set_major_locator(plt.NullLocator())
        
    def __getPixelPlotAxis(self, numPixels):
        return (-0.5, numPixels-0.5, 0, 1)
        
    def plotPixelColors(self, pixelColors):
        numPixels = len(pixelColors)
        self.plot.imshow([pixelColors], interpolation='nearest', extent=(-0.5, numPixels-0.5, -0.5, 0.5))

        if self.aspectRatio is not None:
            self.plot.set_aspect(numPixels / float(self.aspectRatio))
    
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
