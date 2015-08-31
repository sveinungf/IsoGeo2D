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
        denum1 = t[j+p-1] - t[j-1]
        denum2 = t[j+p] - t[j]
        
        frac1 = 0 if denum1 == 0 else float(x - t[j-1])/denum1
        frac2 = 0 if denum2 == 0 else float(t[j+p] - x)/denum2
        
        b1 = bSpline(p-1, t, x, j)
        b2 = bSpline(p-1, t, x, j+1)
        
        return frac1 * b1 + frac2 * b2


class Spline1D:
    def __init__(self, degree, knots, coeffs):
        self.degree = degree
        self.knots = knots
        self.coeffs = coeffs
    
    def evaluate(self, x):
        p = self.degree
        
        mu = findMu(self.knots, x)
        bSplines = []
        
        for j in range(mu-p, mu+1):
            b = bSpline(p, self.knots, x, j)
            bSplines.append(b)
            
        c = self.coeffs[mu-p-1 : mu]
        n = len(c[0])
        result = [0] * n
        
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
        p = self.degree
        
        uMu = findMu(self.uKnots, x)
        vMu = findMu(self.vKnots, y)
        
        uBSplines = []
        vBSplines = []
        
        for i in range(uMu-p, uMu+1):
            b = bSpline(p, self.uKnots, x, i)
            uBSplines.append(b)
            
        for j in range(vMu-p, vMu+1):
            b = bSpline(p, self.vKnots, y, j)
            vBSplines.append(b)
        
        c = self.coeffs[uMu-p-1 : uMu, vMu-p-1 : vMu]
        n = 2
        result = [0] * n
        
        for u in range(len(uBSplines)):
            uB = uBSplines[u]
            
            for v in range(len(vBSplines)):
                vB = vBSplines[v]
                
                for k in range(n):
                    result[k] += uB * vB * c[u][v][k]
        
        return result
