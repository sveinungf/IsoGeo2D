import math
import numpy as np

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
        rho = self.splineModel.rho
        splineModel = self.splineModel
        transfer = self.splineModel.transfer
        voxelModel = self.voxelModel
        
        geomPoints = []
        sampleColors = []
        sampleDeltas = []
        sampleTypes = []
        
        inParamPoint = intersections[0].paramPoint
        inGeomPoint = intersections[0].geomPoint
        outParamPoint = intersections[1].paramPoint
        outGeomPoint = intersections[1].geomPoint
        
        scalar = rho.evaluate(inParamPoint[0], inParamPoint[1])
        color = transfer(scalar)
        sampleColors.append(color)
        
        geomPoints.append(inGeomPoint)
        sampleTypes.append(SamplingType.SPLINE_MODEL)
        
        pGuess = inParamPoint
        prevGeomPoint = inGeomPoint
        
        viewDirDelta = viewRay.viewDir * delta
        samplePoint = inGeomPoint + viewDirDelta
        
        while samplePoint[0] < outGeomPoint[0]:
            lodLevel = criterion.lodLevel(viewRay, samplePoint)
            useVoxelized = lodLevel >= 0
            
            if useVoxelized:
                sampleColor = voxelModel.sample(samplePoint)
                sampleType = SamplingType.VOXEL_MODEL
                geomPoint = samplePoint
            else:
                frustum = viewRay.frustumBoundingEllipse(samplePoint, delta)
                [sampleColor, pApprox, gApprox] = splineModel.sampleInFrustum(samplePoint, pGuess, frustum)
                
                pGuess = pApprox
                sampleType = SamplingType.SPLINE_MODEL
                geomPoint = gApprox
                
            if sampleColor == None:
                sampleType = SamplingType.OUTSIDE_OBJECT
            else:
                sampleColors.append(sampleColor)
                
                dist = geomPoint - prevGeomPoint
                sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
                
                prevGeomPoint = np.array(geomPoint)
                
            geomPoints.append(np.array(geomPoint))
            sampleTypes.append(sampleType)
            
            samplePoint += viewDirDelta
            
        scalar = rho.evaluate(outParamPoint[0], outParamPoint[1])
        color = transfer(scalar)
        sampleColors.append(color)
        
        dist = outGeomPoint - prevGeomPoint
        sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
        
        geomPoints.append(outGeomPoint)
        sampleTypes.append(SamplingType.SPLINE_MODEL)

        if plotter != None and self.plotSamplePoints:
            plotter.plotSamplePoints(geomPoints, sampleTypes)
            
        return [len(sampleColors), compositing.frontToBack(sampleColors, sampleDeltas)]
