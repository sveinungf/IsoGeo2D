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
