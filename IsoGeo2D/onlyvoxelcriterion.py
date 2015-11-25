from voxelcriterion import VoxelCriterion

class OnlyVoxelMCriterion(VoxelCriterion):
    def lodLevel(self, viewRay, viewRayParam):
        return 0
