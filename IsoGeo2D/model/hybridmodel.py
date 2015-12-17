from model.basemodel import BaseModel

class HybridModel(BaseModel):
    def __init__(self, transfer, splineModel, voxelModel, criterion):
        super(HybridModel, self).__init__(transfer)
        
        self.criterion = criterion
        self.splineModel = splineModel
        self.voxelModel = voxelModel
        
    def __chooseModel(self, viewRay, samplePoint):
        lodLevel = self.criterion.lodLevel(viewRay, samplePoint)
        useVoxelized = lodLevel >= 0
        
        if useVoxelized:
            return self.voxelModel
        else:
            return self.splineModel
        
    def sample(self, samplePoint, prevSample, viewRay, delta):
        model = self.__chooseModel(viewRay, samplePoint)
        return model.sample(samplePoint, prevSample, viewRay, delta)
    
    def inSample(self, intersection, viewRay):
        model = self.__chooseModel(viewRay, intersection.geomPoint)
        return model.inSample(intersection, viewRay)
    
    def outSample(self, intersection, viewRay):
        model = self.__chooseModel(viewRay, intersection.geomPoint)
        return model.outSample(intersection, viewRay)
