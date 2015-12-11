from voxelcriterion import VoxelCriterion

class OnlySplineCriterion(VoxelCriterion):
    def lodLevel(self, viewRay, samplePoint):
        return -1
