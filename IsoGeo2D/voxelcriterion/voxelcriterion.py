import abc

class VoxelCriterion:
    __metaclass__ = abc.ABCMeta
    
    @abc.abstractmethod
    def lodLevel(self, viewRay, samplePoint):
        return
