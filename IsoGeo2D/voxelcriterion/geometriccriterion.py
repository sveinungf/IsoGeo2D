from voxelcriterion import VoxelCriterion

class GeometricCriterion(VoxelCriterion):
    def __init__(self, pixelWidth, voxelWidth):
        self.pixelWidth = pixelWidth
        self.voxelWidth = voxelWidth
    
    def lodLevel(self, viewRay, viewRayParam):
        samplePoint = viewRay.evalFromPixel(viewRayParam)
        z = samplePoint[0] - viewRay.eye[0]
        
        pixelFrustumWidth = self.pixelWidth * z / viewRay.near
        
        if pixelFrustumWidth >= (1.5 * self.voxelWidth):
            return 0
        else:
            return -1

