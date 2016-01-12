import abc
import math
import numpy as np

import compositing


class Sample(object):
    def __init__(self, geomPoint, scalar, thetype):
        self.geomPoint = geomPoint
        self.scalar = scalar
        self.type = thetype


class RaycastResult(object):
    def __init__(self, color, samples):
        self.color = color
        self.samples = samples


class BaseModel(object):
    __metaclass__ = abc.ABCMeta
    
    def __init__(self, transfer):
        self.transfer = transfer
    
    @abc.abstractmethod
    def sample(self, samplePoint, prevSample, viewRay, delta):
        return
    
    @abc.abstractmethod
    def inSample(self, intersection, viewRay):
        return
    
    @abc.abstractmethod
    def outSample(self, intersection, viewRay):
        return

    @abc.abstractmethod
    def getIntersections(self, viewRay):
        return
    
    def raycast(self, viewRay, delta, plotter=None):
        geomPoints = []
        sampleTypes = []

        intersections = self.getIntersections(viewRay)

        if intersections is None:
            return RaycastResult(None, 0)
        
        inGeomPoint = intersections[0].geomPoint
        outGeomPoint = intersections[1].geomPoint
        
        resultColor = np.zeros(4)
        prevColor = None
        
        sample = self.inSample(intersections[0], viewRay)
        
        if sample is not None:
            geomPoints.append(sample.geomPoint)
            sampleTypes.append(sample.type)
            
            prevColor = self.transfer(sample.scalar)
            
        viewDirDelta = viewRay.viewDir * delta
        samplePoint = inGeomPoint + viewDirDelta
        
        prevSample = sample

        saturated = False
        
        while samplePoint[0] < outGeomPoint[0]:
            sample = self.sample(samplePoint, prevSample, viewRay, delta)
            
            if sample is not None:
                geomPoints.append(sample.geomPoint)
                sampleTypes.append(sample.type)
                
                if prevSample is not None:
                    dist = sample.geomPoint - prevSample.geomPoint
                    actualDelta = math.sqrt(dist[0]**2 + dist[1]**2)
                    resultColor = compositing.accumulate(resultColor, prevColor, actualDelta)

                prevColor = self.transfer(sample.scalar)
                prevSample = sample
                
                if resultColor[3] >= 1.0:
                    saturated = True
                    break
            
            samplePoint += viewDirDelta

        if not saturated:
            sample = self.outSample(intersections[1], viewRay)

            if sample is not None:
                geomPoints.append(sample.geomPoint)
                sampleTypes.append(sample.type)
                
                dist = sample.geomPoint - prevSample.geomPoint
                actualDelta = math.sqrt(dist[0]**2 + dist[1]**2)
                resultColor = compositing.accumulate(resultColor, prevColor, actualDelta)

        if plotter is not None:
            plotter.plotSamplePoints(geomPoints, sampleTypes)

        return RaycastResult(resultColor, len(geomPoints))
