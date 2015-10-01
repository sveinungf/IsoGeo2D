import numpy as np
from scipy import interpolate

class Texture2D:
    def __init__(self, textureData):
        self.textureData = textureData
        
        self.cols = len(textureData[0])
        self.rows = len(textureData)
        
        x = np.linspace(0, 1, self.cols)
        y = np.linspace(0, 1, self.rows)
        
        self.f = interpolate.interp2d(x, y, textureData, kind='linear')
        
    def fetch(self, uv):
        return self.f(uv[0], uv[1])

    def closest(self, uv):
        uIndex = round(uv[0] * (self.cols-1))
        vIndex = round(uv[1] * (self.rows-1))
        
        return self.textureData[vIndex, uIndex]
