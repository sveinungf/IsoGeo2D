import math
import numpy as np

import compositing
from ray import Ray2D
from samplingtype import SamplingType


class SplineModel:
    samplingDefault = -1
    
    def __init__(self, phiPlane, rho, transfer):
        self.phiPlane = phiPlane
        self.rho = rho
        self.transfer = transfer
        
    def generateScalarMatrix(self, boundingBox, width, height):
        phiPlane = self.phiPlane
        bb = boundingBox
        
        rayCount = height
        samplingsPerRay = width
        
        xDelta = float(bb.getWidth())/samplingsPerRay
        yDelta = float(bb.getHeight())/rayCount
        
        xValues = np.linspace(bb.left+xDelta/2, bb.right-xDelta/2, samplingsPerRay)
        yValues = np.linspace(bb.bottom+yDelta/2, bb.top-yDelta/2, rayCount)
        
        samplingScalars = np.ones((rayCount, samplingsPerRay)) * SplineModel.samplingDefault    
        
        for i, y in enumerate(yValues):
            samplingRay = Ray2D(np.array([bb.left-xDelta/2, y]), np.array([0, y]), 10, yDelta)
            
            intersections = phiPlane.findTwoIntersections(samplingRay)
            
            if intersections == None:
                continue

            inGeomPoint = intersections[0].geomPoint
            outGeomPoint = intersections[1].geomPoint
            
            geomPoints = []
            paramPoints = []
            
            prevUV = intersections[0].paramPoint
            
            for j, x in enumerate(xValues):
                if x < inGeomPoint[0] or x > outGeomPoint[0]:
                    continue
                
                samplePoint = np.array([x, y])
                
                pixelFrustum = samplingRay.frustumBoundingEllipseParallel(samplePoint, xDelta)
                
                pApprox = phiPlane.inverseInFrustum(samplePoint, prevUV, pixelFrustum)
                gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])
                geomPoints.append(gApprox)

                paramPoints.append(pApprox)
                
                scalar = self.rho.evaluate(pApprox[0], pApprox[1])
                samplingScalars[i][j] = scalar
                
                prevUV = pApprox
            
        return samplingScalars

    def sampleInFrustum(self, samplePoint, pGuess, frustum):
        phiPlane = self.phiPlane
        rho = self.rho

        pApprox = phiPlane.inverseInFrustum(samplePoint, pGuess, frustum)
        gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])
        
        scalar = rho.evaluate(pApprox[0], pApprox[1])
        color = self.transfer(scalar)
        
        return [color, pApprox, gApprox]
    
    def sampleWithinTolerance(self, samplePoint, pGuess, tolerance):
        phiPlane = self.phiPlane
        rho = self.rho

        pApprox = phiPlane.inverseWithinTolerance(samplePoint, pGuess, tolerance)
        gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])
        
        scalar = rho.evaluate(pApprox[0], pApprox[1])
        color = self.transfer(scalar)
        
        return [color, pApprox, gApprox]        
    
    def raycast(self, viewRay, intersections, delta, plotter=None, tolerance=None):
        geomPoints = []
        sampleColors = []
        sampleDeltas = []
        sampleTypes = []
        
        inParamPoint = intersections[0].paramPoint
        inGeomPoint = intersections[0].geomPoint
        outParamPoint = intersections[1].paramPoint
        outGeomPoint = intersections[1].geomPoint
        
        scalar = self.rho.evaluate(inParamPoint[0], inParamPoint[1])
        color = self.transfer(scalar)
        sampleColors.append(color)
        
        geomPoints.append(inGeomPoint)
        sampleTypes.append(SamplingType.SPLINE_MODEL)
        
        pGuess = inParamPoint
        prevGeomPoint = inGeomPoint
        
        viewDirDelta = viewRay.viewDir * delta
        samplePoint = inGeomPoint + viewDirDelta
        
        while samplePoint[0] < outGeomPoint[0]:
            if tolerance == None:
                frustum = viewRay.frustumBoundingEllipse(samplePoint, delta)
                [sampleColor, pApprox, gApprox] = self.sampleInFrustum(samplePoint, pGuess, frustum)
            else:
                [sampleColor, pApprox, gApprox] = self.sampleWithinTolerance(samplePoint, pGuess, tolerance)
            
            sampleColors.append(sampleColor)         
            
            dist = gApprox - prevGeomPoint
            sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
                
            geomPoints.append(gApprox)
            sampleTypes.append(SamplingType.SPLINE_MODEL)
            
            pGuess = pApprox
            prevGeomPoint = gApprox

            samplePoint += viewDirDelta
        
        scalar = self.rho.evaluate(outParamPoint[0], outParamPoint[1])
        color = self.transfer(scalar)
        sampleColors.append(color)
        
        dist = outGeomPoint - prevGeomPoint
        sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
        
        geomPoints.append(outGeomPoint)
        sampleTypes.append(SamplingType.SPLINE_MODEL)

        if plotter != None:
            plotter.plotSamplePoints(geomPoints, sampleTypes)
        
        return [len(sampleColors), compositing.frontToBack(sampleColors, sampleDeltas)]
