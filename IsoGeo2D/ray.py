import numpy as np

class Ray2D:
    def __init__(self, eye, pixel):
        self.eye = eye
        
        viewDir = pixel - eye
        self.a = viewDir[1]/viewDir[0]
        
    def eval(self, t):
        return np.array([t+self.eye[0], self.a*t+self.eye[1]])
    
    def deval(self, t):
        return np.array([1, self.a])
