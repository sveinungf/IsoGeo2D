import math
import numpy as np

import fileio.splinereader
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
        
        self.rho = fileio.splinereader.read('datasets/0/rho.json')
    
    def sample(self, samplePoint):
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
        
        inParamPoint = intersections[0].paramPoint
        inGeomPoint = intersections[0].geomPoint
        outParamPoint = intersections[1].paramPoint
        outGeomPoint = intersections[1].geomPoint
        
        scalar = self.rho.evaluate(inParamPoint[0], inParamPoint[1])
        color = self.transfer(scalar)
        sampleColors.append(color)
        
        samplePoints.append(inGeomPoint)
        sampleTypes.append(SamplingType.SPLINE_MODEL)
        
        prevGeomPoint = inGeomPoint
        
        viewDirDelta = viewRay.viewDir * delta
        samplePoint = inGeomPoint + viewDirDelta
        
        while samplePoint[0] < outGeomPoint[0]:
            sampleColor = self.sample(samplePoint)
            
            if sampleColor == None:
                sampleType = SamplingType.OUTSIDE_OBJECT
            else:
                sampleType = SamplingType.VOXEL_MODEL
                sampleColors.append(sampleColor)
                
                if prevGeomPoint != None:
                    dist = samplePoint - prevGeomPoint
                    sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
                    
                prevGeomPoint = np.array(samplePoint)
                
            samplePoints.append(samplePoint)
            sampleTypes.append(sampleType)
            
            samplePoint = samplePoint + viewDirDelta
        
        scalar = self.rho.evaluate(outParamPoint[0], outParamPoint[1])
        color = self.transfer(scalar)
        sampleColors.append(color)
        
        dist = outGeomPoint - prevGeomPoint
        sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
        
        samplePoints.append(outGeomPoint)
        sampleTypes.append(SamplingType.SPLINE_MODEL)

        if plotter != None and self.plotSamplePoints:
            plotter.plotSamplePoints(samplePoints, sampleTypes)
        
        return [len(sampleColors), compositing.frontToBack(sampleColors, sampleDeltas)]
