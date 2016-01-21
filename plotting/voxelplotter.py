import numpy as np
from matplotlib.patches import Rectangle

from modelplotter import ModelPlotter

class VoxelPlotter(ModelPlotter):
    def __init__(self, plot):
        super(VoxelPlotter, self).__init__(plot)
        
    def plotColors(self, colors, boundingBox):
        deltaX = boundingBox.getWidth() / float(len(colors[0]))
        deltaY = boundingBox.getHeight() / float(len(colors))
        
        for i in range(len(colors)):
            for j in range(len(colors[0])):
                color = colors[i][j]
                
                if color[3] != 0:
                    lowerLeft = (boundingBox.left+j*deltaX, boundingBox.bottom+i*deltaY)
                    r = Rectangle(lowerLeft, deltaX, deltaY, facecolor=tuple(color))
                    self.plot.add_patch(r)

    def plotScalars(self, scalars, boundingBox, facecolor=None, edgecolor=None):
        deltaX = boundingBox.getWidth() / float(len(scalars[0]))
        deltaY = boundingBox.getHeight() / float(len(scalars))
        
        for (i, j), scalar in np.ndenumerate(scalars):
            if scalar != -1:
                lowerLeft = (boundingBox.left+j*deltaX, boundingBox.bottom+i*deltaY)
                fColor = facecolor if facecolor is not None else tuple([scalar]*3)
                r = Rectangle(lowerLeft, deltaX, deltaY, facecolor=fColor, edgecolor=edgecolor)
                self.plot.add_patch(r)
