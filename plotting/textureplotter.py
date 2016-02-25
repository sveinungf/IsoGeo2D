import numpy as np
from matplotlib.patches import Rectangle

from modelplotter import ModelPlotter


class TexturePlotter(ModelPlotter):
    def __init__(self, plot):
        super(TexturePlotter, self).__init__(plot)

    def plotScalars(self, texture, boundingBox, facecolor=None, edgecolor=None, nonresidentcolor=None):
        scalars = texture.textureData
        indicators = texture.indicators

        m = len(scalars[0])
        n = len(scalars)

        deltaX = boundingBox.getWidth() / float(m - 2)
        deltaY = boundingBox.getHeight() / float(n - 2)

        for (i, j), scalar in np.ndenumerate(scalars):
            if scalar != -1:
                lowerLeft = (boundingBox.left+(j-1)*deltaX, boundingBox.bottom+(i-1)*deltaY)
                fColor = facecolor if facecolor is not None else tuple([scalar]*3)

                markerX = [lowerLeft[0], lowerLeft[0]+deltaX]
                markerY = [lowerLeft[1], lowerLeft[1]+deltaY]

                if 0 < i < (m-1) and 0 < j < (n-1):
                    if indicators[i-1][j-1] == -1:
                        self.plot.plot(markerX, markerY, color=nonresidentcolor)
                else:
                    # Ghost cells
                    self.plot.plot(markerX, markerY, color=nonresidentcolor)

                r = Rectangle(lowerLeft, deltaX, deltaY, facecolor=fColor, edgecolor=edgecolor)
                self.plot.add_patch(r)
