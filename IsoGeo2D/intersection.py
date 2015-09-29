import math

class Intersection:
    def __init__(self, paramPoint, lineParam):
        self.paramPoint = paramPoint
        self.lineParam = lineParam

    def alreadyIn(self, intersects, tolerance):
        result = False
        thisPoint = self.paramPoint
        
        for intersect in intersects:
            point = intersect.paramPoint
            distance = math.sqrt((thisPoint[0]-point[0])**2 + (thisPoint[1]-point[1])**2) 
            result = distance < 2*tolerance
            
            if result:
                break
            
        return result
