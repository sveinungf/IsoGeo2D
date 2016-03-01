from modeltype import ModelType


class RenderData:
    def __init__(self, modelType='', delta=0.0, texSize=0):
        self.delta = delta
        self.modelType = modelType
        self.renderResult = None
        self.texSize = texSize

        name = None

        if modelType == ModelType.REFERENCE:
            name = 'Reference'
        elif modelType == ModelType.DIRECT:
            name = 'Direct'
        elif modelType == ModelType.VOXEL:
            name = 'Voxel ({}x{})'.format(texSize, texSize)
        elif modelType == ModelType.BOUNDARYACCURATE:
            name = 'Boundary accurate ({}x{})'.format(texSize, texSize)
        elif modelType == ModelType.HYBRID:
            name = 'Hybrid ({}x{})'.format(texSize, texSize)

        self.name = name
