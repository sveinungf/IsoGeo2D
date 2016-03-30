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

    def createSamplingRays(self, boundingBox, width, height):
        bb = boundingBox
        rayCount = height
        samplingsPerRay = width

        xDelta = float(bb.getWidth())/samplingsPerRay
        yDelta = float(bb.getHeight())/rayCount

        yValues = np.linspace(bb.bottom+yDelta/2, bb.top-yDelta/2, rayCount)

        samplingRays = []

        for y in yValues:
            samplingRay = Ray2D(np.array([bb.left-xDelta/2, y]), np.array([bb.left, y]), 10, yDelta)
            samplingRays.append(samplingRay)

        return np.asarray(samplingRays)

    def approximateSamplePoints(self, boundingBox, width, height, tolerance):
        phiPlane = self.phiPlane
        bb = boundingBox
        rayCount = height
        samplingsPerRay = width

        xDelta = float(bb.getWidth())/samplingsPerRay
        yDelta = float(bb.getHeight())/rayCount

        yValues = np.linspace(bb.bottom+yDelta/2, bb.top-yDelta/2, rayCount)
        xValues = np.linspace(bb.left+xDelta/2, bb.right-xDelta/2, samplingsPerRay)

        geomPoints = []
        paramPoints = []
        samplingRays = self.createSamplingRays(bb, width, height)

        for i, samplingRay in enumerate(samplingRays):
            rayGeomPoints = []
            rayParamPoints = []

            intersections = phiPlane.findTwoIntersections(samplingRay)

            if intersections is None:
                geomPoints.append(rayGeomPoints)
                paramPoints.append(rayParamPoints)
                continue

            inGeomPoint = intersections[0].geomPoint
            outGeomPoint = intersections[1].geomPoint

            prevUV = intersections[0].paramPoint

            for j, x in enumerate(xValues):
                if x < inGeomPoint[0] or x > outGeomPoint[0]:
                    rayGeomPoints.append(None)
                    rayParamPoints.append(None)
                    continue

                samplePoint = np.array([x, yValues[i]])

                pApprox = phiPlane.inverseWithinTolerance(samplePoint, prevUV, tolerance)
                gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])

                rayGeomPoints.append(gApprox)
                rayParamPoints.append(pApprox)

                prevUV = pApprox

            geomPoints.append(rayGeomPoints)
            paramPoints.append(rayParamPoints)

        return np.asarray(paramPoints), np.asarray(geomPoints)
        
    def generateScalarMatrix(self, boundingBox, width, height, tolerance, paramPlotter=None, geomPlotter=None):
        bb = boundingBox
        
        samplingScalars = np.ones((height, width)) * SplineModel.samplingDefault

        samplingRays = self.createSamplingRays(bb, width, height)

        paramPoints, geomPoints = self.approximateSamplePoints(bb, width, height, tolerance)

        for i, rayParamPoints in enumerate(paramPoints):
            for j, paramPoint in enumerate(rayParamPoints):
                if paramPoint is not None:
                    scalar = self.rho.evaluate(paramPoint[0], paramPoint[1])
                    samplingScalars[i][j] = scalar
        
        if paramPlotter is not None:
            for rayParamPoints in paramPoints:
                paramPlotter.plotPoints(np.asarray(rayParamPoints))
            
        if geomPlotter is not None:
            for samplingRay in samplingRays:
                geomPlotter.plotViewRay(samplingRay, [-10, 10])

            for rayGeomPoints in geomPoints:
                geomPlotter.plotPoints(rayGeomPoints)

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
