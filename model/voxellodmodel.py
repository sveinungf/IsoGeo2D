import math

from model.basemodel import BaseModel, Sample
from model.voxelmodel import VoxelModel


class LodSample(Sample):
    def __init__(self, sample, lodLevel):
        super(LodSample, self).__init__(sample.geomPoint, sample.scalar, sample.type)
        self.lodLevel = lodLevel


class VoxelLodModel(BaseModel):
    def __init__(self, transfer, lodTextures, boundingBox, pixelWidth):
        super(VoxelLodModel, self).__init__(transfer)

        self.pixelWidth = pixelWidth

        self.lodModels = []
        self.voxelDiagonals = []

        bbWidth = boundingBox.getWidth()
        sqrt2 = math.sqrt(2)

        for texture in lodTextures:
            voxelWidth = bbWidth / float(texture.cols)
            self.voxelDiagonals.append(sqrt2 * voxelWidth)
            self.lodModels.append(VoxelModel(transfer, texture, boundingBox))

    def __chooseLodLevel(self, samplePoint, viewRay):
        z = samplePoint[0] - viewRay.eye[0]
        pixelFrustumWidth = self.pixelWidth * z / viewRay.near
        maxVoxelSize = pixelFrustumWidth / 1.5

        index = 0

        for i, voxelDiagonal in reversed(list(enumerate(self.voxelDiagonals))):
            if voxelDiagonal >= maxVoxelSize:
                index = i
                break

        return index

    def sample(self, samplePoint, prevSample, viewRay, delta):
        lodLevel = self.__chooseLodLevel(samplePoint, viewRay)
        model = self.lodModels[lodLevel]
        sample = model.sample(samplePoint, prevSample, viewRay, delta)

        if sample is None:
            return None
        else:
            return LodSample(sample, lodLevel)

    def inSample(self, intersection, viewRay):
        lodLevel = self.__chooseLodLevel(intersection.geomPoint, viewRay)
        model = self.lodModels[lodLevel]
        sample = model.inSample(intersection, viewRay)

        if sample is None:
            return None
        else:
            return LodSample(sample, lodLevel)

    def outSample(self, intersection, viewRay):
        lodLevel = self.__chooseLodLevel(intersection.geomPoint, viewRay)
        model = self.lodModels[lodLevel]
        sample = model.outSample(intersection, viewRay)

        if sample is None:
            return None
        else:
            return LodSample(sample, lodLevel)

    def getIntersections(self, viewRay):
        return viewRay.boundingBoxIntersects
