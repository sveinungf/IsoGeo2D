class BoundingBox:
    def __init__(self, bottom, top, left, right):
        self.bottom = bottom
        self.top = top
        self.left = left
        self.right = right

    def getWidth(self):
        return self.right - self.left
    
    def getHeight(self):
        return self.top - self.bottom
