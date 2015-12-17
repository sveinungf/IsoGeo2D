from model.basemodel import BaseModel

class BoundaryHybridModel(BaseModel):
    def __init__(self, transfer, splineModel, voxelModel):
        super(BoundaryHybridModel, self).__init__(transfer)

        self.splineModel = splineModel
        self.voxelModel = voxelModel

    def sample(self, samplePoint, prevSample, viewRay, delta):
        return self.voxelModel.sample(samplePoint, prevSample, viewRay, delta)
        
    def inSample(self, intersection, viewRay):
        return self.splineModel.inSample(intersection, viewRay)
    
    def outSample(self, intersection, viewRay):
        return self.splineModel.outSample(intersection, viewRay)
