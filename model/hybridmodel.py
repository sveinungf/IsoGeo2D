from model.basemodel import BaseModel


class HybridModel(BaseModel):
    def __init__(self, transfer, splineModel, voxelModel, criterion):
        super(HybridModel, self).__init__(transfer)
        
        self.criterion = criterion
        self.splineModel = splineModel
        self.voxelModel = voxelModel
        
        self.splineSamples = 0
        self.voxelSamples = 0
        
    def __chooseModel(self, viewRay, samplePoint):
        lodLevel = self.criterion.lodLevel(viewRay, samplePoint)
        useVoxelized = lodLevel >= 0
        
        if useVoxelized:
            self.voxelSamples += 1
            return self.voxelModel
        else:
            self.splineSamples += 1
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

    def findIntersections(self, viewRay):
        return self.splineModel.findIntersections(viewRay)

    def voxelRatio(self):
        x = self.voxelSamples
        s = self.splineSamples
        ratio = float(x) / (x + s)
        
        self.splineSamples = 0
        self.voxelSamples = 0
        
        return ratio
