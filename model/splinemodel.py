import numpy as np

from model.basemodel import BaseModel, Sample
from ray import Ray2D
from samplingtype import SamplingType


class SplineSample(Sample):
    def __init__(self, geomPoint, scalar, paramPoint):
        super(SplineSample, self).__init__(geomPoint, scalar, SamplingType.SPLINE_MODEL)
        self.paramPoint = paramPoint


class SplineModel(BaseModel):
    samplingDefault = -1
    
    def __init__(self, transfer, phiPlane, rho, samplingTolerance=None):
        super(SplineModel, self).__init__(transfer)
        
        self.phiPlane = phiPlane
        self.rho = rho
        self.samplingTolerance = samplingTolerance
        
    def generateScalarMatrix(self, boundingBox, width, height, tolerance, paramPlotter=None, geomPlotter=None):
        phiPlane = self.phiPlane
        bb = boundingBox
        
        rayCount = height
        samplingsPerRay = width
        
        xDelta = float(bb.getWidth())/samplingsPerRay
        yDelta = float(bb.getHeight())/rayCount
        
        xValues = np.linspace(bb.left+xDelta/2, bb.right-xDelta/2, samplingsPerRay)
        yValues = np.linspace(bb.bottom+yDelta/2, bb.top-yDelta/2, rayCount)
        
        samplingScalars = np.ones((rayCount, samplingsPerRay)) * SplineModel.samplingDefault
        
        geomPoints = []
        paramPoints = []
        samplingRays = []
        
        for i, y in enumerate(yValues):
            samplingRay = Ray2D(np.array([bb.left-xDelta/2, y]), np.array([bb.left, y]), 10, yDelta)
            samplingRays.append(samplingRay)
            
            intersections = phiPlane.findTwoIntersections(samplingRay)
            
            if intersections is None:
                continue

            inGeomPoint = intersections[0].geomPoint
            outGeomPoint = intersections[1].geomPoint
            
            prevUV = intersections[0].paramPoint
            
            for j, x in enumerate(xValues):
                if x < inGeomPoint[0] or x > outGeomPoint[0]:
                    continue
                
                samplePoint = np.array([x, y])

                pApprox = phiPlane.inverseWithinTolerance(samplePoint, prevUV, tolerance)
                gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])
                geomPoints.append(gApprox)

                paramPoints.append(pApprox)
                
                scalar = self.rho.evaluate(pApprox[0], pApprox[1])
                samplingScalars[i][j] = scalar
                
                prevUV = pApprox
        
        if paramPlotter is not None:
            paramPlotter.plotPoints(paramPoints)
            
        if geomPlotter is not None:
            for samplingRay in samplingRays:
                geomPlotter.plotViewRay(samplingRay, [-10, 10])

            geomPlotter.plotPoints(geomPoints)

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

    def sample(self, samplePoint, prevSample, viewRay, delta):
        phiPlane = self.phiPlane
        rho = self.rho
        
        pGuess = prevSample.paramPoint
        
        if self.samplingTolerance is None:
            frustum = viewRay.frustumBoundingEllipse(samplePoint, delta)
            pApprox = phiPlane.inverseInFrustum(samplePoint, pGuess, frustum)
        else:
            pApprox = phiPlane.inverseWithinTolerance(samplePoint, pGuess, self.samplingTolerance)

        gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])
        scalar = rho.evaluate(pApprox[0], pApprox[1])[0]

        return SplineSample(gApprox, scalar, pApprox)
    
    def inSample(self, intersection, viewRay):
        pApprox = intersection.paramPoint
        scalar = self.rho.evaluate(pApprox[0], pApprox[1])[0]
        
        return SplineSample(intersection.geomPoint, scalar, pApprox)
    
    def outSample(self, intersection, viewRay):
        return self.inSample(intersection, viewRay)

    def findIntersections(self, viewRay):
        return self.phiPlane.findTwoIntersections(viewRay)
