import math
import numpy as np
from scipy import interpolate

class Texture2D:
    def __init__(self, textureData):
        self.cols = len(textureData[0])
        self.rows = len(textureData)
        
        data = textureData
        data = np.vstack((data[0], data))
        data = np.vstack((data, data[-1]))
        data = np.column_stack((data[:,0],data))
        data = np.column_stack((data, data[:,-1]))

        self.textureData = data
        
        x = np.linspace(0, 1, len(textureData[0]))
        step = x[1]
        x = np.insert(x, 0, -step)
        x = np.append(x, 1+step)
        
        y = np.linspace(0, 1, len(textureData))
        step = y[1]
        y = np.insert(y, 0, -step)
        y = np.append(y, 1+step)
        
        self.f = interpolate.interp2d(x, y, data, kind='linear')
        
    def fetch(self, uv):
        return self.f(uv[0], uv[1])[0]

    def closest(self, uv):
        uIndex = math.floor(uv[0] * self.cols)
        vIndex = math.floor(uv[1] * self.rows)
        
        return self.textureData[vIndex+1, uIndex+1]
