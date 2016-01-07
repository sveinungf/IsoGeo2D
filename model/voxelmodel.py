import numpy as np

from model.basemodel import BaseModel, Sample
from samplingtype import SamplingType

class VoxelModel(BaseModel):
    samplingDefault = -1
    
    def __init__(self, transfer, scalarTexture, boundingBox):
        super(VoxelModel, self).__init__(transfer)
        
        self.boundingBox = boundingBox
        self.scalarTexture = scalarTexture
    
    def sample(self, samplePoint, prevSample, viewRay, delta):
        bb = self.boundingBox
        texture = self.scalarTexture

        u = (samplePoint[0]-bb.left)/bb.getWidth()
        v = (samplePoint[1]-bb.bottom)/bb.getHeight()
        
        scalar = texture.fetch([u, v])

        if scalar == -1:
            return None
            
        geomPoint = np.array(samplePoint)

        return Sample(geomPoint, scalar, SamplingType.VOXEL_MODEL_LOD[0])
    
    def inSample(self, intersection, viewRay):
        return self.sample(intersection.geomPoint, None, viewRay, None)
    
    def outSample(self, intersection, viewRay):
        return self.inSample(intersection, viewRay)

    def getIntersections(self, viewRay):
        return viewRay.boundingBoxIntersects
