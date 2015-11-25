from voxelcriterion import VoxelCriterion

class OnlyVoxelCriterion(VoxelCriterion):
    def lodLevel(self, viewRay, viewRayParam):
        return 0
