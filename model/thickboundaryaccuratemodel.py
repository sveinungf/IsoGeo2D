from model.boundaryaccuratemodel import BoundaryAccurateModel


class ThickBoundaryAccurateModel(BoundaryAccurateModel):
    def __init__(self, transfer, splineModel, voxelModel):
        super(ThickBoundaryAccurateModel, self).__init__(transfer, splineModel, voxelModel)

    def sample(self, samplePoint, prevSample, viewRay, delta):
        voxelSample = self.voxelModel.sample(samplePoint, prevSample, viewRay, delta)

        if voxelSample is not None:
            return voxelSample
        else:
            return self.splineModel.sample(samplePoint, prevSample, viewRay, delta)
