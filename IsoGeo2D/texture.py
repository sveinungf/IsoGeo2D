import numpy as np
from scipy import interpolate

class Texture2D:
    def __init__(self, textureData):
        cols = len(textureData[0])
        rows = len(textureData)
        
        x = np.linspace(0, 1, cols)
        y = np.linspace(0, 1, rows)
        
        self.f = interpolate.interp2d(x, y, textureData, kind='linear')
        
    def fetch(self, u, v):
        return self.f(u, v)
