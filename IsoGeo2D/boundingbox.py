class BoundingBox:
    def __init__(self, top, bottom, left, right):
        self.top = top
        self.bottom = bottom
        self.left = left
        self.right = right

    def getWidth(self):
        return self.right - self.left
    
    def getHeight(self):
        return self.top - self.bottom
