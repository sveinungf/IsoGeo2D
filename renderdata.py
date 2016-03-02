from modeltype import ModelType


class RenderData:
    def __init__(self, modelType='', delta=0.0, texSize=0):
        self.delta = delta
        self.modelType = modelType
        self.renderResult = None
        self.texSize = texSize
