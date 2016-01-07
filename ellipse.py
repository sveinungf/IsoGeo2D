from math import cos, sin

class Ellipse:
    def __init__(self, point, width, height, angle):
        self.point = point
        self.width = width
        self.height = height
        self.angle = angle
        
    def enclosesXY(self, xp, yp):
        a = self.angle
        w = self.width
        h = self.height
        x0 = self.point[0]
        y0 = self.point[1]
        
        frac1 = ((cos(a)*(xp-x0) + sin(a)*(yp-y0))**2)/(w/2.)**2
        frac2 = ((sin(a)*(xp-x0) - cos(a)*(yp-y0))**2)/(h/2.)**2
        
        return (frac1 + frac2) <= 1.0

    def enclosesPoint(self, point):
        return self.enclosesXY(point[0], point[1])
