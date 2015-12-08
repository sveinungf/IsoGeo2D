import math

import compositing
from samplingtype import SamplingType

class VoxelModel:
    samplingDefault = -1
    
    def __init__(self, scalarTexture, transfer, boundingBox, plotter=None):
        self.boundingBox = boundingBox
        self.plotSamplePoints = False
        self.plotter = plotter
        self.scalarTexture = scalarTexture
        self.transfer = transfer
    
    def sampleInFrustum(self, samplePoint):
        bb = self.boundingBox
        scalarTexture = self.scalarTexture
        
        u = (samplePoint[0]-bb.left)/bb.getWidth()
        v = (samplePoint[1]-bb.bottom)/bb.getHeight()
        
        if not bb.enclosesPoint(samplePoint):
            return None
        
        if scalarTexture.closest([u, v]) == self.samplingDefault:
            return None
        
        scalar = scalarTexture.fetch([u, v])
        color = self.transfer(scalar)
        
        return color
    
    def raycast(self, viewRay, intersections, delta):
        plotter = self.plotter
        
        sampleColors = []
        sampleDeltas = []
        samplePoints = []
        sampleTypes = []

        viewRayParam = 0
        
        inGeomPoint = intersections[0].geomPoint
        outGeomPoint = intersections[1].geomPoint
        
        prevGeomPoint = None
        
        while viewRay.inRange(viewRayParam):
            samplePoint = viewRay.evalFromPixel(viewRayParam)
            
            if inGeomPoint[0] <= samplePoint[0] <= outGeomPoint[0]:
                sampleColor = self.sampleInFrustum(samplePoint)
                    
                if sampleColor == None:
                    sampleType = SamplingType.OUTSIDE_OBJECT
                else:
                    sampleColors.append(sampleColor)
                    
                    if prevGeomPoint != None:
                        dist = samplePoint - prevGeomPoint
                        sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
                    
                    sampleType = SamplingType.VOXEL_MODEL
                    
                    prevGeomPoint = samplePoint
            else:
                sampleType = SamplingType.OUTSIDE_OBJECT
                
            samplePoints.append(samplePoint)
            sampleTypes.append(sampleType)
            
            viewRayParam += delta
        
        if plotter != None and self.plotSamplePoints:
            plotter.plotSamplePoints(samplePoints, sampleTypes)
        
        return compositing.frontToBack(sampleColors, sampleDeltas)
