import numpy as np

def findMu(t, x):
    for j in range(len(t)):
        if x >= t[j] and x < t[j+1]:
            return j+1

def bSpline(p, t, x, j):
    '''
    p - degree
    t - knots
    '''
    
    if p == 0:
        if x >= t[j-1] and x < t[j]:
            return 1
        else:
            return 0
    else:
        denom1 = t[j+p-1] - t[j-1]
        denom2 = t[j+p] - t[j]
        
        frac1 = 0 if denom1 == 0 else float(x - t[j-1])/denom1
        frac2 = 0 if denom2 == 0 else float(t[j+p] - x)/denom2
        
        b1 = bSpline(p-1, t, x, j)
        b2 = bSpline(p-1, t, x, j+1)
        
        return frac1 * b1 + frac2 * b2
    
def bSplines(p, t, mu, x):
    b = np.zeros(p + 1, dtype=float)
    b[p] = 1.0
    
    for r in range(1 , p+1):
        k = mu - r + 1
        
        denom = t[k+r-1] - t[k-1]
        w2 = (t[k+r-1] - x) / denom
        b[p-r] = w2 * b[p-r+1]
        
        for j in range(p-r+1, p):
            k += 1
            w1 = w2
            w2 = (t[k+r-1] - x) / (t[k+r-1] - t[k-1])
            b[j] = (1 - w1) * b[j] + w2 * b[j+1]
        
        b[p] *= (1 - w2)
        
    return b


def bSplineDerivative(p, t, x, j):
    if p == 0:
        return 0
    
    denom1 = t[j+p-1] - t[j-1]
    denom2 = t[j+p] - t[j]
    
    frac1 = 0 if denom1 == 0 else float(bSpline(p-1, t, x, j))/denom1
    frac2 = 0 if denom2 == 0 else float(bSpline(p-1, t, x, j+1))/denom2
    
    return p * (frac1 - frac2)

def bSplineDerivatives(p, t, mu, x):
    bSplines = []
    
    for j in range(p+1):
        b = bSplineDerivative(p, t, x, mu-p+j)
        bSplines.append(b)

    return bSplines
    
class Spline1D:
    def __init__(self, degree, knots, coeffs):
        self.degree = degree
        self.knots = knots
        self.coeffs = coeffs
    
    def evaluate(self, x):
        n = len(self.coeffs[0])
        result = [0] * n
        t = self.knots
        
        if x < t[0] or x >= t[-1]:
            return result
        
        p = self.degree
        bSplines = []
        mu = findMu(self.knots, x)
        
        for j in range(mu-p, mu+1):
            b = bSpline(p, self.knots, x, j)
            bSplines.append(b)
            
        c = self.coeffs[mu-p-1 : mu]
        
        for j in range(len(c)):
            b = bSplines[j]
            
            for k in range(n):
                result[k] += b * c[j][k] 
        
        return result

class Spline2D:
    '''
    coeffs - numpy array
    '''
    def __init__(self, degree, uKnots, vKnots, coeffs):
        self.degree = degree
        self.uKnots = uKnots
        self.vKnots = vKnots
        self.coeffs = coeffs
        self.n = len(coeffs[0][0])
        
    def evaluate(self, x, y):
        return self.__evaluate(x, y, bSplines, bSplines)
    
    def evaluatePartialDerivativeU(self, x, y):
        return self.__evaluate(x, y, bSplineDerivatives, bSplines)
        
    def evaluatePartialDerivativeV(self, x, y):
        return self.__evaluate(x, y, bSplines, bSplineDerivatives)

    def jacob(self, u, v):
        return np.matrix([self.evaluatePartialDerivativeU(u, v), 
                          self.evaluatePartialDerivativeV(u, v)]).transpose()
        
    def __evaluate(self, x, y, uBSplinesFunc, vBSplinesFunc):
        n = self.n
        result = np.zeros(n)
        
        if not (self.uKnots[0] <= x < self.uKnots[-1] and 
                self.vKnots[0] <= y < self.vKnots[-1]):
            return result
        
        p = self.degree
        uMu = findMu(self.uKnots, x)
        vMu = findMu(self.vKnots, y)
        
        uBSplines = uBSplinesFunc(p, self.uKnots, uMu, x)
        vBSplines = vBSplinesFunc(p, self.vKnots, vMu, y)

        c = self.coeffs

        for u, uB in enumerate(uBSplines):
            cu = c[uMu-p-1+u]
            
            for v, vB in enumerate(vBSplines):
                cuv = cu[vMu-p-1+v]
                
                for k in range(n):
                    result[k] += uB * vB * cuv[k]
        
        return result
