import newton
import numpy as np
from intersection import Intersection
from side import Side
from boundingbox import BoundingBox

def intersection2D(f, g, df, dg, uGuess, uInterval, tolerance):
    vGuess = 0
    
    def h(u, v):
        return f(u) - g(v)
    
    def hJacob(u, v):
        return np.matrix([df(u), -dg(v)]).transpose()
    
    return newton.newtonsMethod2DTolerance(h, hJacob, [uGuess, vGuess], uInterval, tolerance)

class SplinePlane:
    def __init__(self, phiPlane, interval, tolerance):
        self.phi = phiPlane
        self.interval = interval
        self.tolerance = tolerance

    def evaluate(self, u, v):
        return self.phi.evaluate(u, v)
        
    def bottom(self, u):
        return self.phi.evaluate(u, self.interval[0])
    def dbottom(self, u):
        return self.phi.evaluatePartialDerivativeU(u, self.interval[0])
        
    def top(self, u):
        return self.phi.evaluate(u, self.interval[1])
    def dtop(self, u):
        return self.phi.evaluatePartialDerivativeU(u, self.interval[1])
    
    def left(self, v):
        return self.phi.evaluate(self.interval[0], v)
    def dleft(self, v):
        return self.phi.evaluatePartialDerivativeV(self.interval[0], v)
    
    def right(self, v):
        return self.phi.evaluate(self.interval[1], v)
    def dright(self, v):
        return self.phi.evaluatePartialDerivativeV(self.interval[1], v)

    def __findIntersection(self, side, ray, uGuess):
        if side == Side.BOTTOM:
            f = self.bottom
            df = self.dbottom
        elif side == Side.TOP:
            f = self.top
            df = self.dtop
        elif side == Side.LEFT:
            f = self.left
            df = self.dleft
        else:
            f = self.right
            df = self.dright
        
        uv = intersection2D(f, ray.eval, df, ray.deval, uGuess, self.interval, self.tolerance)
        
        if uv != None:
            interval = self.interval
            
            if side == Side.BOTTOM:
                point = np.array([uv[0], interval[0]])
            elif side == Side.TOP:
                point = np.array([uv[0], interval[1]])
            elif side == Side.LEFT:
                point = np.array([interval[0], uv[0]])
            else:
                point = np.array([interval[1], uv[0]])
                
            return Intersection(point, ray.eval(uv[1]), uv[1])
        
        return None
    
    def findTwoIntersections(self, ray):
        result = []

        for side in Side.sides:
            intersection = self.__findIntersection(side, ray, 0)
            
            if intersection != None:
                result.append(intersection)
                
        if len(result) < 2:
            for side in Side.sides:
                intersection = self.__findIntersection(side, ray, 1)
                
                if intersection != None:
                    if not intersection.alreadyIn(result, self.tolerance):
                        result.append(intersection)
        
        if len(result) < 2:
            return None
        
        if result[0].lineParam < result[1].lineParam:
            return np.asarray(result)
        else:
            return np.asarray([result[1], result[0]])

    def createBoundingBox(self):
        coeffs = self.phi.coeffs
        
        left = coeffs[0][0][0]
        right = coeffs[-1][0][0]
        bottom = coeffs[:, 0][0][1]
        top = coeffs[:, -1][0][1]
        
        for coeff in coeffs[0]:
            if coeff[0] < left:
                left = coeff[0]
                
        for coeff in coeffs[-1]:
            if coeff[0] > right:
                right = coeff[0]
                
        for coeff in coeffs[:, 0]:
            if coeff[1] < bottom:
                bottom = coeff[1]
                
        for coeff in coeffs[:, -1]:
            if coeff[1] > top:
                top = coeff[1]
                
        return BoundingBox(left, right, bottom, top)

    def inverseInFrustum(self, geomPoint, uvGuess, frustum):
        interval = self.interval
        phi = self.phi
        
        def f(u,v):
            return phi.evaluate(u,v) - geomPoint
                              
        return newton.newtonsMethod2DFrustum(f, phi.jacob, uvGuess, interval, phi, frustum)

    def inverseWithinTolerance(self, geomPoint, uvGuess, tolerance):
        interval = self.interval
        phi = self.phi
        
        def f(u,v):
            return phi.evaluate(u,v) - geomPoint
                   
        return newton.newtonsMethod2DTolerance(f, phi.jacob, uvGuess, interval, tolerance)           
