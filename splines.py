import numpy as np
from scipy import interpolate

from field import Field
from geometry import Geometry


class Spline2D(Geometry, Field):
    def __init__(self, degree, uKnots, vKnots, coeffs):
        super(Spline2D, self).__init__()

        self.coeffs = coeffs
        self.coeffElems = len(coeffs)
        self.uCoeffsLength = len(uKnots) - degree - 1
        self.vCoeffsLength = len(vKnots) - degree - 1
        self.tcks = []
        
        for i in range(self.coeffElems):
            self.tcks.append([uKnots, vKnots, coeffs[i], degree, degree])
    
    def __coeffsExtremum(self, axis, f):
        coeffs = self.coeffs[axis]
        extremum = coeffs[0]
        
        for i in range(1, len(coeffs)):
            extremum = f(extremum, coeffs[i])
            
        return extremum
        
    def min(self, axis):
        return self.__coeffsExtremum(axis, min)
    
    def max(self, axis):
        return self.__coeffsExtremum(axis, max)
        
    def evaluate(self, x, y):
        result = np.empty(self.coeffElems)
        
        for i in range(self.coeffElems):
            result[i] = interpolate.bisplev(x, y, self.tcks[i])
            
        return result
    
    def evaluatePartialDerivativeU(self, x, y):
        result = np.empty(self.coeffElems)
        
        for i in range(self.coeffElems):
            result[i] = interpolate.bisplev(x, y, self.tcks[i], dx=1)
            
        return result
        
    def evaluatePartialDerivativeV(self, x, y):
        result = np.empty(self.coeffElems)
        
        for i in range(self.coeffElems):
            result[i] = interpolate.bisplev(x, y, self.tcks[i], dy=1)
            
        return result

    def jacob(self, u, v):
        return np.matrix([self.evaluatePartialDerivativeU(u, v), 
                          self.evaluatePartialDerivativeV(u, v)]).transpose()
