import matplotlib.gridspec as gridspec
import numpy as np
import pylab as plt

from pixelplotter import PixelPlotter

class PixelFigure:
    def __init__(self, texDimSizes):
        numTextures = len(texDimSizes)
        
        plt.figure(figsize=(15, 6))
        mainGrid = gridspec.GridSpec(2 + numTextures * 3, 2, hspace=(0.6*numTextures))
        
        ax = plt.subplot(mainGrid[0, 0])
        self.refPixelsPlot = PixelPlotter(ax, "Reference")
        
        ax = plt.subplot(mainGrid[1, 0])
        self.directPixelsPlot = PixelPlotter(ax, "Direct")
        
        ax = plt.subplot(mainGrid[1, 1])
        self.directDiffsPlot = PixelPlotter(ax, "Direct color diff")
        
        self.voxelPixelsPlots = np.empty(numTextures, dtype=object)
        self.voxelDiffsPlots = np.empty(numTextures, dtype=object)
        
        self.hybridPixelsPlots = np.empty(numTextures, dtype=object)
        self.hybridDiffsPlots = np.empty(numTextures, dtype=object)
        self.hybridVoxelRatioPlots = np.empty(numTextures, dtype=object)
        
        offset = 2

        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            
            ax = plt.subplot(mainGrid[i + offset, 0])
            self.voxelPixelsPlots[i] = PixelPlotter(ax, "Voxel ({}x{})".format(texDimSize, texDimSize))
            
            ax = plt.subplot(mainGrid[i + offset, 1])
            self.voxelDiffsPlots[i] = PixelPlotter(ax, "Voxel color diffs ({}x{})".format(texDimSize, texDimSize))
        
        offset += numTextures
        
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            
            ax = plt.subplot(mainGrid[2*i + offset, 0])
            self.hybridPixelsPlots[i] = PixelPlotter(ax, "Hybrid ({}x{})".format(texDimSize, texDimSize))
            
            ax = plt.subplot(mainGrid[2*i + 1 + offset, 0])
            self.hybridVoxelRatioPlots[i] = PixelPlotter(ax, "")
            
            ax = plt.subplot(mainGrid[2*i + offset, 1])
            self.hybridDiffsPlots[i] = PixelPlotter(ax, "Hybrid color diffs ({}x{})".format(texDimSize, texDimSize))
        
        plt.ion()
        plt.show()
        
        #mainGrid.tight_layout(fig)
        
    def draw(self):
        plt.draw()
