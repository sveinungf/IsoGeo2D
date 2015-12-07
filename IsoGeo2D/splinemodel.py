import math

import compositing
from samplingtype import SamplingType


class SplineModel:
    def __init__(self, phiPlane, rho, transfer):
        self.phiPlane = phiPlane
        self.rho = rho
        self.transfer = transfer

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
            
            if inGeomPoint[0] <= samplePoint[0] <= outGeomPoint[0]:
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
        
        return compositing.frontToBack(sampleColors, sampleDeltas)
