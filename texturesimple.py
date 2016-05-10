import math
import numpy as np
from scipy import interpolate

class Texture2D:
    def __init__(self, textureData):
        cols = len(textureData[0])
        rows = len(textureData)
        self.cols = cols
        self.rows = rows

        indicators = np.empty_like(textureData)

        for i in range(rows):
            for j in range(cols):
                if textureData[i][j] == -1:
                    indicators[i][j] = 1.0
                else:
                    indicators[i][j] = 0.0

        marginX = 1.0/(2.0 * cols)
        marginY = 1.0/(2.0 * rows)

        data = textureData
        data = np.vstack((data[0], data))
        data = np.vstack((data, data[-1]))
        data = np.column_stack((data[:,0],data))
        data = np.column_stack((data, data[:,-1]))
        self.textureData = data

        idata = indicators
        irow = np.ones_like(idata[0]) * 1
        idata = np.vstack((irow, idata))
        idata = np.vstack((idata, irow))
        icolumn = np.ones_like(idata[:, 0]) * 1
        idata = np.column_stack((icolumn, idata))
        idata = np.column_stack((idata, icolumn))

        x = np.linspace(-marginX, 1.0+marginX, cols+2)
        y = np.linspace(-marginY, 1.0+marginY, rows+2)

        self.indicator = interpolate.interp2d(x, y, idata, kind='linear')

        self.f = interpolate.interp2d(x, y, data, kind='linear')

    def fetch(self, uv):
        if self.closest(uv) == -1:
            return -1

        if self.indicator(uv[0], uv[1])[0] > 0.0:
            return -1

        return self.f(uv[0], uv[1])[0]

    def closest(self, uv):
        uIndex = math.floor(uv[0] * self.cols)
        vIndex = math.floor(uv[1] * self.rows)

        return self.textureData[vIndex+1, uIndex+1]
