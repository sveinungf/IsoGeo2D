import math

from voxelcriterion import VoxelCriterion

class GeometricCriterion(VoxelCriterion):
    def __init__(self, pixelWidth, voxelWidth):
        self.pixelWidth = pixelWidth
        self.voxelDiagonal = math.sqrt(2) * voxelWidth 
    
    def lodLevel(self, viewRay, samplePoint):
        z = samplePoint[0] - viewRay.eye[0]
        
        pixelFrustumWidth = self.pixelWidth * z / viewRay.near
        
        if pixelFrustumWidth >= (1.5 * self.voxelDiagonal):
            return 0
        else:
            return -1
