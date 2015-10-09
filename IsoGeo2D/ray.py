import math
import numpy as np
import numpy.linalg as la
from ellipse import Ellipse

def normalize2D(vector):
    magnitude = float(math.sqrt(vector[0]**2 + vector[1]**2))
    return np.array([vector[0] / magnitude, vector[1] / magnitude])
    
class Ray2D:
    def __init__(self, eye, pixel, pixelWidth=0):
        self.eye = eye
        self.pixel = pixel
        self.pixelWidth = pixelWidth
        
        self.viewDir = normalize2D(pixel - eye)
        
        pixelTop = np.array([pixel[0], pixel[1] + pixelWidth/2])
        pixelBottom = np.array([pixel[0], pixel[1] - pixelWidth/2])
        self.frustumUpperDir = normalize2D(pixelTop - eye)
        self.frustumLowerDir = normalize2D(pixelBottom - eye)

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

    def frustumBoundingEllipse(self, point, delta):
        upper = self.frustumUpperDir
        lower = self.frustumLowerDir
        v = self.viewDir
        
        rayAngle = math.atan(v[1])
        
        cosUpperAngle = np.dot(upper, v) / la.norm(upper) / la.norm(v)
        upperAngle = np.arccos(np.clip(cosUpperAngle, -1, 1))
        
        cosLowerAngle = np.dot(lower, v) / la.norm(lower) / la.norm(v)
        lowerAngle = np.arccos(np.clip(cosLowerAngle, -1, 1))
        
        eyeDistance = la.norm(point - self.eye)
        upperDistance = np.tan(upperAngle)*eyeDistance
        lowerDistance = np.tan(lowerAngle)*eyeDistance
        
        perpendicularViewDir = np.array([-self.viewDir[1], self.viewDir[0]])
        
        upperIntersectionPoint = point + perpendicularViewDir * upperDistance
        lowerIntersectionPoint = point - perpendicularViewDir * lowerDistance
        
        midpoint = (upperIntersectionPoint + lowerIntersectionPoint) / 2.0
        
        return Ellipse(midpoint, delta, upperDistance + lowerDistance, rayAngle)
        
    def generateSamplePoints(self, begin, end, delta):
        result = []
        current = begin + delta
        
        while current < end:
            result.append(self.evalFromPixel(current))
            current += delta
            
        return result
