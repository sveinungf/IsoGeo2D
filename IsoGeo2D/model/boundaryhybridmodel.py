import numpy as np

from model.basemodel import BaseModel, Sample
from samplingtype import SamplingType

class BoundaryHybridModel(BaseModel):
    samplingDefault = -1
    
    def __init__(self, transfer, scalarTexture, splineModel, boundingBox):
        super(BoundaryHybridModel, self).__init__(transfer)
        
        self.boundingBox = boundingBox
        self.scalarTexture = scalarTexture
        self.splineModel = splineModel

    def sample(self, samplePoint, prevSample, viewRay, delta):
        bb = self.boundingBox
        texture = self.scalarTexture

        u = (samplePoint[0]-bb.left)/bb.getWidth()
        v = (samplePoint[1]-bb.bottom)/bb.getHeight()
        
        if not bb.enclosesPoint(samplePoint):
            return None
        
        if texture.closest([u, v]) == self.samplingDefault:
            return None
        
        scalar = texture.fetch([u, v])
        geomPoint = np.array(samplePoint)

        return Sample(geomPoint, scalar, SamplingType.VOXEL_MODEL)
        
    def inSample(self, intersection):
        return self.splineModel.inSample(intersection)
    
    def outSample(self, intersection):
        return self.splineModel.outSample(intersection)
