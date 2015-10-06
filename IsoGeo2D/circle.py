class Circle:
    def __init__(self, point, radius):
        self.point = point
        self.radius = radius

    def enclosesXY(self, x, y):
        xmid = self.point[0]
        ymid = self.point[1]
        
        return (x-xmid)**2 + (y-ymid)**2 < self.radius**2

    def enclosesPoint(self, point):
        return self.enclosesXY(point[0], point[1])
