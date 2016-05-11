import math
import numpy as np

import vecutil
from voxelcriterion import VoxelCriterion

class GeometricCriterion(VoxelCriterion):
    def __init__(self, pixelWidth, voxelWidth, voxelHeight):
        self.pixelWidth = pixelWidth
        self.voxelDiagonal = math.sqrt(voxelWidth**2 + voxelHeight**2)
    
    def lodLevel(self, viewRay, samplePoint):
        farZ = samplePoint[0] - viewRay.eye[0]

        upperFrustumDir = vecutil.normalize(viewRay.pixelTop - viewRay.eye)
        t = farZ / upperFrustumDir[0]
        upperEpsilonPoint = np.array([samplePoint[0], viewRay.eye[1] + t*upperFrustumDir[1]])

        lowerFrustumDir = vecutil.normalize(viewRay.pixelBottom - viewRay.eye)
        t = farZ / lowerFrustumDir[0]
        lowerEpsilonPoint = np.array([samplePoint[0], viewRay.eye[1] + t*lowerFrustumDir[1]])

        epsilon = upperEpsilonPoint[1] - lowerEpsilonPoint[1]

        if 0.5 * epsilon > self.voxelDiagonal:
            return 0
        else:
            return -1
