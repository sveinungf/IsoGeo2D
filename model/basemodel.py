import abc

from compositing import FrontToBack


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
    def findIntersections(self, viewRay):
        return
    
    def raycast(self, viewRay, delta, plotter=None):
        geomPoints = []
        sampleTypes = []

        intersections = self.findIntersections(viewRay)

        if intersections is None:
            return RaycastResult(None, 0)
        
        inGeomPoint = intersections[0].geomPoint
        outGeomPoint = intersections[1].geomPoint

        compositing = FrontToBack(self.transfer)
        
        sample = self.inSample(intersections[0], viewRay)
        
        if sample is not None:
            geomPoints.append(sample.geomPoint)
            sampleTypes.append(sample.type)

            compositing.addSample(sample)
            
        viewDirDelta = viewRay.viewDir * delta
        samplePoint = inGeomPoint + viewDirDelta

        saturated = False
        
        while samplePoint[0] < outGeomPoint[0]:
            sample = self.sample(samplePoint, sample, viewRay, delta)
            
            if sample is not None:
                geomPoints.append(sample.geomPoint)
                sampleTypes.append(sample.type)

                compositing.addSample(sample)
                saturated = compositing.saturated()

                if saturated:
                    break
            
            samplePoint += viewDirDelta

        if not saturated:
            sample = self.outSample(intersections[1], viewRay)

            if sample is not None:
                geomPoints.append(sample.geomPoint)
                sampleTypes.append(sample.type)

                compositing.addSample(sample)

        if plotter is not None:
            plotter.plotSamplePoints(geomPoints, sampleTypes)

        return RaycastResult(compositing.dst, len(geomPoints))
