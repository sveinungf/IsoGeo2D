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
        splinePoints = []
        voxelPoints = []
        outsidePoints = []
        
        for point, sampleType in itertools.izip(points, types):
            if sampleType == SamplingType.SPLINE_MODEL:
                splinePoints.append(point)
            elif sampleType == SamplingType.VOXEL_MODEL:
                voxelPoints.append(point)
            else:
                outsidePoints.append(point)

        splinePoints = np.array(splinePoints)
        voxelPoints = np.array(voxelPoints)
        outsidePoints = np.array(outsidePoints)
        
        if len(splinePoints) > 0:
            self.plot.plot(splinePoints[:,0], splinePoints[:,1], marker='o', color='b')
        
        if len(voxelPoints) > 0:
            self.plot.plot(voxelPoints[:,0], voxelPoints[:,1], marker='o', color='g')
        
        if len(outsidePoints) > 0:
            self.plot.plot(outsidePoints[:,0], outsidePoints[:,1], marker='o', color='r')
        
    def plotViewRay(self, ray, interval):
        params = np.linspace(interval[0], interval[1], 100)
        points = self.__generatePoints1var(ray.evalFromEye, params)
        
        self.plot.plot(points[:,0], points[:,1], color='r')
