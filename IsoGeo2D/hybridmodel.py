import math

import compositing
from samplingtype import SamplingType


class HybridModel:
    def __init__(self, splineModel, voxelModel, criterion, plotter=None):
        self.criterion = criterion
        self.plotSamplePoints = False
        self.plotter = plotter
        self.splineModel = splineModel
        self.voxelModel = voxelModel

    def raycast(self, viewRay, intersections, delta):
        criterion = self.criterion
        plotter = self.plotter
        splineModel = self.splineModel
        voxelModel = self.voxelModel
        
        sampleColors = []
        sampleDeltas = []
        samplePoints = []
        sampleTypes = []
        
        viewRayParam = 0

        pGuess = intersections[0].paramPoint
        inGeomPoint = intersections[0].geomPoint
        outGeomPoint = intersections[1].geomPoint
        
        prevGeomPoint = None
        
        while viewRay.inRange(viewRayParam):
            samplePoint = viewRay.evalFromPixel(viewRayParam)
            
            if samplePoint[0] > outGeomPoint[0]:
                break
            
            if inGeomPoint[0] <= samplePoint[0]:
                if criterion.lodLevel(viewRay, viewRayParam) >= 0:
                    sampleColor = voxelModel.sample(samplePoint)
                    sampleType = SamplingType.VOXEL_MODEL
                else:
                    frustum = viewRay.frustumBoundingEllipse(samplePoint, delta)
                    
                    [sampleColor, pApprox, gApprox] = splineModel.sampleInFrustum(samplePoint, pGuess, frustum)
                    pGuess = pApprox
                    samplePoint = gApprox
                    sampleType = SamplingType.SPLINE_MODEL
                    
                if sampleColor == None:
                    sampleType = SamplingType.OUTSIDE_OBJECT
                else:
                    sampleColors.append(sampleColor)
                    
                    if not prevGeomPoint == None:
                        dist = samplePoint - prevGeomPoint
                        sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
                    
                    prevGeomPoint = samplePoint
            else:
                sampleType = SamplingType.OUTSIDE_OBJECT
                
            samplePoints.append(samplePoint)
            sampleTypes.append(sampleType)
            
            viewRayParam += delta

        if plotter != None and self.plotSamplePoints:
            plotter.plotSamplePoints(samplePoints, sampleTypes)
            
        return compositing.frontToBack(sampleColors, sampleDeltas)
