import numpy as np
from matplotlib.patches import Rectangle

class ModelPlotter:
    def __init__(self, plot):
        self.plot = plot
        
    def __generatePoints1var(self, f, params):
        output = np.empty((len(params), 2))
        
        for i, param in enumerate(params):
            output[i] = f(param)
        
        return output

    def plotBoundingBox(self, boundingBox):
        lowerLeft = (boundingBox.left, boundingBox.bottom)
        width = boundingBox.getWidth()
        height = boundingBox.getHeight()
        
        r = Rectangle(lowerLeft, width, height, fill=False, linestyle='dashed')
        self.plot.add_patch(r)
        
    def plotViewRay(self, ray, interval):
        params = np.linspace(interval[0], interval[1], 100)
        points = self.__generatePoints1var(ray.evalFromEye, params)
        
        self.plot.plot(points[:,0], points[:,1], color='r')
