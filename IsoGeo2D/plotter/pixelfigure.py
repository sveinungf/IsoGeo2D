import matplotlib.gridspec as gridspec
import pylab as plt

from pixelplotter import PixelPlotter

class PixelFigure:
    def __init__(self):
        plt.figure(figsize=(15, 6))
        mainGrid = gridspec.GridSpec(4, 2)
        
        ax = plt.subplot(mainGrid[0, 0])
        self.refPixelsPlot = PixelPlotter(ax, "Reference")
        
        ax = plt.subplot(mainGrid[1, 0])
        self.directPixelsPlot = PixelPlotter(ax, "Direct")
        
        ax = plt.subplot(mainGrid[1, 1])
        self.directDiffsPlot = PixelPlotter(ax, "Direct color diff")
        
        ax = plt.subplot(mainGrid[2, 0])
        self.voxelPixelsPlot = PixelPlotter(ax, "Voxel")
        
        ax = plt.subplot(mainGrid[2, 1])
        self.voxelDiffsPlot = PixelPlotter(ax, "Voxel color diffs")
        
        ax = plt.subplot(mainGrid[3, 0])
        self.hybridPixelsPlot = PixelPlotter(ax, "Hybrid")
        
        ax = plt.subplot(mainGrid[3, 1])
        self.hybridDiffsPlot = PixelPlotter(ax, "Hybrid color diffs")
        
        plt.ion()
        plt.show()
        
    def draw(self):
        plt.draw()
