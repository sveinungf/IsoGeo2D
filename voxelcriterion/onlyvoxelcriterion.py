from voxelcriterion import VoxelCriterion

class OnlyVoxelCriterion(VoxelCriterion):
    def lodLevel(self, viewRay, samplePoint):
        return 0
