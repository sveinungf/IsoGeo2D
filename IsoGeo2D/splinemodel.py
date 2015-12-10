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
                if tolerance == None:
                    frustum = viewRay.frustumBoundingEllipse(samplePoint, delta)
                    [sampleColor, pApprox, gApprox] = self.sampleInFrustum(samplePoint, pGuess, frustum)
                else:
                    [sampleColor, pApprox, gApprox] = self.sampleWithinTolerance(samplePoint, pGuess, tolerance)
                    
                pGuess = pApprox
                samplePoint = gApprox
                sampleType = SamplingType.SPLINE_MODEL
                
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
        
        if plotter != None:
            plotter.plotSamplePoints(samplePoints, sampleTypes)
        
        return [len(sampleColors), compositing.frontToBack(sampleColors, sampleDeltas)]
