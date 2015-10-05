import math
import numpy as np

def normalize2D(vector):
    magnitude = float(math.sqrt(vector[0]**2 + vector[1]**2))
    return np.array([vector[0] / magnitude, vector[1] / magnitude])
    
class Ray2D:
    def __init__(self, eye, pixel, pixelWidth=0):
        self.eye = eye
        self.pixel = pixel
        self.pixelWidth = pixelWidth
        
        self.viewDir = normalize2D(pixel - eye)
        self.frustumUpperDir = normalize2D(pixel + pixelWidth/2 - eye)
        self.frustumLowerDir = normalize2D(pixel - pixelWidth/2 - eye)

    def eval(self, t):
        return self.evalFromPixel(t)
        
    def evalFromEye(self, t):
        return self.eye + self.viewDir*t
    
    def evalFromPixel(self, t):
        return self.pixel + self.viewDir*t
    
    def deval(self, t):
        return self.viewDir
    
    def evalFrustumUpper(self, t):
        return self.eye + self.frustumUpperDir*t
    
    def evalFrustumLower(self, t):
        return self.eye + self.frustumLowerDir*t

    def generateSamplePoints(self, begin, end, delta):
        result = []
        current = begin + delta
        
        while current < end:
            result.append(self.evalFromPixel(current))
            current += delta
            
        return result
