import numpy as np
from matplotlib.patches import Rectangle

from modelplotter import ModelPlotter

class VoxelPlotter(ModelPlotter):
    def __init__(self, plot):
        super(VoxelPlotter, self).__init__(plot)

    def plotScalars(self, scalars, boundingBox):
        deltaX = boundingBox.getWidth() / float(len(scalars[0]))
        deltaY = boundingBox.getHeight() / float(len(scalars))
        
        for (i, j), scalar in np.ndenumerate(scalars):
            if scalar != -1:
                lowerLeft = (boundingBox.left+j*deltaX, boundingBox.bottom+i*deltaY)
                r = Rectangle(lowerLeft, deltaX, deltaY, facecolor=tuple([scalar]*3))
                self.plot.add_patch(r)
