import itertools
import numpy as np
from matplotlib.patches import Rectangle

from samplingtype import SamplingType

class ModelPlotter(object):
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
        
    def plotSamplePoints(self, points, types):
        for point, sampleType in itertools.izip(points, types):
            if sampleType == SamplingType.SPLINE_MODEL:
                pointColor = 'b'
            elif sampleType == SamplingType.VOXEL_MODEL:
                pointColor = 'g'
            else:
                pointColor = 'r'
                
            self.plot.plot(point[0], point[1], marker='o', color=pointColor)
        
    def plotViewRay(self, ray, interval):
        params = np.linspace(interval[0], interval[1], 100)
        points = self.__generatePoints1var(ray.evalFromEye, params)
        
        self.plot.plot(points[:,0], points[:,1], color='r')
