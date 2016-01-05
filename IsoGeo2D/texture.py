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

        x = np.linspace(marginX, 1.0-marginX, cols)
        y = np.linspace(marginY, 1.0-marginY, rows)

        self.indicator = interpolate.interp2d(x, y, indicators, kind='linear')
        
        data = textureData
        data = np.vstack((data[0], data))
        data = np.vstack((data, data[-1]))
        data = np.column_stack((data[:,0],data))
        data = np.column_stack((data, data[:,-1]))
        self.textureData = data

        x = np.linspace(0, 1, cols)
        step = x[1]
        x = np.insert(x, 0, -step)
        x = np.append(x, 1+step)

        y = np.linspace(0, 1, rows)
        step = y[1]
        y = np.insert(y, 0, -step)
        y = np.append(y, 1+step)
        
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
