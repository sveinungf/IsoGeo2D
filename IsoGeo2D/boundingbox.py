import numpy as np

from intersection import Intersection
from side import Side


class BoundingBox:
    def __init__(self, left, right, bottom, top):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top

    def getWidth(self):
        return self.right - self.left
    
    def getHeight(self):
        return self.top - self.bottom

    def enclosesXY(self, x, y):
        return self.left <= x <= self.right and self.bottom <= y <= self.top

    def enclosesPoint(self, point):
        return self.enclosesXY(point[0], point[1])

    def __findIntersection(self, side, ray):
        point = None

        if side == Side.BOTTOM or side == Side.TOP:
            y = self.top if side == Side.TOP else self.bottom

            t = (y - ray.eye[1]) / ray.viewDir[1]
            x = ray.eye[0] + t * ray.viewDir[0]

            if self.left <= x <= self.right:
                point = np.array([x, y])
        else:
            x = self.left if side == Side.LEFT else self.right

            t = (x - ray.eye[0]) / ray.viewDir[0]
            y = ray.eye[1] + t * ray.viewDir[1]

            if self.bottom <= y <= self.top:
                point = np.array([x, y])

        if point is None:
            return None
        else:
            return Intersection(None, point, None)


    def findTwoIntersections(self, ray):
        result = []

        for side in Side.sides:
            intersection = self.__findIntersection(side, ray)

            if intersection is not None:
                result.append(intersection)

        if len(result) < 2:
            return None

        return np.asarray(result)
