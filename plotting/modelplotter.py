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

    def plotBoundingBox(self, boundingBox, edgecolor=None, linestyle='dashed', linewidth=None):
        lowerLeft = (boundingBox.left, boundingBox.bottom)
        width = boundingBox.getWidth()
        height = boundingBox.getHeight()
        
        r = Rectangle(lowerLeft, width, height, fill=False, linestyle=linestyle, linewidth=linewidth, edgecolor=edgecolor)
        self.plot.add_patch(r)

    def __getSampleTypeColor(self, type):
        return {
            SamplingType.OUTSIDE_OBJECT: 'r',
            SamplingType.SPLINE_MODEL: 'b',
            SamplingType.VOXEL_MODEL_LOD[0]: 'g',
            SamplingType.VOXEL_MODEL_LOD[1]: 'c',
            SamplingType.VOXEL_MODEL_LOD[2]: 'y',
            SamplingType.VOXEL_MODEL_LOD[3]: 'm',
            SamplingType.VOXEL_MODEL_LOD[4]: 'w',
        }.get(type, 'k')
        
    def plotSamplePoints(self, points, types):
        for point, sampleType in itertools.izip(points, types):
            color = self.__getSampleTypeColor(sampleType)
            self.plot.plot(point[0], point[1], marker='o', color=color)
        
    def plotViewRay(self, ray, interval):
        params = np.linspace(interval[0], interval[1], 100)
        points = self.__generatePoints1var(ray.evalFromEye, params)
        
        self.plot.plot(points[:,0], points[:,1], color='r')
