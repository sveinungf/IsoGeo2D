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


def bSplineDerivative(p, t, x, j):
    if p == 0:
        return 0
    
    denom1 = t[j+p-1] - t[j-1]
    denom2 = t[j+p] - t[j]
    
    frac1 = 0 if denom1 == 0 else float(bSpline(p-1, t, x, j))/denom1
    frac2 = 0 if denom2 == 0 else float(bSpline(p-1, t, x, j+1))/denom2
    
    return p * (frac1 - frac2)

    
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
        
    def evaluate(self, x, y):
        return self.__evaluate(x, y, bSpline, bSpline)
    
    def evaluatePartialDerivativeX(self, x, y):
        return self.__evaluate(x, y, bSplineDerivative, bSpline)
        
    def evaluatePartialDerivativeY(self, x, y):
        return self.__evaluate(x, y, bSpline, bSplineDerivative)
        
    def __evaluate(self, x, y, uBSplineFunc, vBSplineFunc):
        n = len(self.coeffs[0][0])
        result = [0] * n
        
        if not (self.uKnots[0] <= x < self.uKnots[-1] and 
                self.vKnots[0] <= y < self.vKnots[-1]):
            return result
        
        p = self.degree
        uMu = findMu(self.uKnots, x)
        vMu = findMu(self.vKnots, y)
        
        uBSplines = []
        vBSplines = []

        for j in range(p+1):
            uB = uBSplineFunc(p, self.uKnots, x, uMu-p+j)
            vB = vBSplineFunc(p, self.vKnots, y, vMu-p+j)
            uBSplines.append(uB)
            vBSplines.append(vB)
        
        c = self.coeffs[uMu-p-1 : uMu, vMu-p-1 : vMu]
        
        for u, uB in enumerate(uBSplines):
            for v, vB in enumerate(vBSplines):
                for k in range(n):
                    result[k] += uB * vB * c[u][v][k]
        
        return result
