import matplotlib.pyplot as plt
import numpy as np

from pixelplotter import PixelPlotter

class PixelFigure:
    def __init__(self, texDimSizes):
        numTextures = len(texDimSizes)
        aspectRatio = 50

        fig = plt.figure(figsize=(15,6))
        self.fig = fig

        mainGrid = plt.GridSpec(2 + numTextures * 4, 2, hspace=(0.6*numTextures))
        
        ax = fig.add_subplot(mainGrid[0, 0])
        self.refPixelsPlot = PixelPlotter(ax, "Reference", aspectRatio)
        
        ax = fig.add_subplot(mainGrid[1, 0])
        self.directPixelsPlot = PixelPlotter(ax, "Direct", aspectRatio)
        
        ax = fig.add_subplot(mainGrid[1, 1])
        self.directDiffsPlot = PixelPlotter(ax, "Direct color diff", aspectRatio)
        
        self.voxelPixelsPlots = np.empty(numTextures, dtype=object)
        self.voxelDiffsPlots = np.empty(numTextures, dtype=object)
        
        self.baPixelsPlots = np.empty(numTextures, dtype=object)
        self.baDiffsPlots = np.empty(numTextures, dtype=object)
        
        self.hybridPixelsPlots = np.empty(numTextures, dtype=object)
        self.hybridDiffsPlots = np.empty(numTextures, dtype=object)
        self.hybridVoxelRatioPlots = np.empty(numTextures, dtype=object)
        
        offset = 2

        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            
            ax = fig.add_subplot(mainGrid[i + offset, 0])
            self.voxelPixelsPlots[i] = PixelPlotter(ax, "Voxel ({}x{})".format(texDimSize, texDimSize), aspectRatio)
            
            ax = fig.add_subplot(mainGrid[i + offset, 1])
            self.voxelDiffsPlots[i] = PixelPlotter(ax, "Voxel color diffs ({}x{})".format(texDimSize, texDimSize), aspectRatio)
        
        offset += numTextures
        
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            
            ax = fig.add_subplot(mainGrid[i + offset, 0])
            self.baPixelsPlots[i] = PixelPlotter(ax, "Boundary accurate ({}x{})".format(texDimSize, texDimSize), aspectRatio)
            
            ax = fig.add_subplot(mainGrid[i + offset, 1])
            self.baDiffsPlots[i] = PixelPlotter(ax, "Boundary accurate color diffs ({}x{})".format(texDimSize, texDimSize), aspectRatio)
            
        offset += numTextures    
        
        for i in range(numTextures):
            texDimSize = texDimSizes[i]
            
            ax = fig.add_subplot(mainGrid[2*i + offset, 0])
            self.hybridPixelsPlots[i] = PixelPlotter(ax, "Hybrid ({}x{})".format(texDimSize, texDimSize), aspectRatio)
            
            ax = fig.add_subplot(mainGrid[2*i + 1 + offset, 0])
            self.hybridVoxelRatioPlots[i] = PixelPlotter(ax, "", aspectRatio)
            
            ax = fig.add_subplot(mainGrid[2*i + offset, 1])
            self.hybridDiffsPlots[i] = PixelPlotter(ax, "Hybrid color diffs ({}x{})".format(texDimSize, texDimSize), aspectRatio)

    def show(self):
        self.fig.show()