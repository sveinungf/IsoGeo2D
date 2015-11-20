import itertools
import math
import numpy as np

import compositing
from samplinglocation import SamplingLocation


class SplineGeometry:
    def __init__(self, phiPlane, rho, transfer, plotter=None, plotSamplePoints=True, plotEllipse=False):
        self.phiPlane = phiPlane
        self.rho = rho
        self.transfer = transfer
        self.plotter = plotter
        self.plotSamplePoints = plotSamplePoints
        self.plotEllipse = plotEllipse
        
        self.boundingBox = phiPlane.createBoundingBox()
    
    def __getSamplePointLocations(self, samplePoints, intersections):
        bb = self.boundingBox
        
        locations = np.empty(len(samplePoints))
        
        if intersections == None:
            for i, samplePoint in enumerate(samplePoints):
                if bb.enclosesPoint(samplePoint):
                    locations[i] = SamplingLocation.OUTSIDE_OBJECT
                else:
                    locations[i] = SamplingLocation.OUTSIDE_BOUNDINGBOX
        else:
            inGeomPoint = intersections[0].geomPoint
            outGeomPoint = intersections[1].geomPoint
            
            for i, samplePoint in enumerate(samplePoints):
                if bb.enclosesPoint(samplePoint):
                    if inGeomPoint[0] <= samplePoint[0] <= outGeomPoint[0]:
                        locations[i] = SamplingLocation.INSIDE_OBJECT
                    else:
                        locations[i] = SamplingLocation.OUTSIDE_OBJECT
                else:
                    locations[i] = SamplingLocation.OUTSIDE_BOUNDINGBOX
                    
        return locations
    
    def raycast(self, viewRay, delta):
        phiPlane = self.phiPlane
        rho = self.rho
        plotter = self.plotter
        
        sampleColors = []
        sampleDeltas = []
        
        samplePoints = viewRay.generateSamplePoints(0, 10, delta)
        intersections = phiPlane.findTwoIntersections(viewRay)
        locations = self.__getSamplePointLocations(samplePoints, intersections)
        
        if not intersections == None:
            geomPoints = []
            prevUV = intersections[0].paramPoint
            firstIteration = True
            
            for samplePoint, location in itertools.izip(samplePoints, locations):
                if location == SamplingLocation.INSIDE_OBJECT:
                    pixelFrustum = viewRay.frustumBoundingEllipse(samplePoint, delta)
                    
                    pApprox = phiPlane.inverseInFrustum(samplePoint, prevUV, pixelFrustum)
                    gApprox = phiPlane.evaluate(pApprox[0], pApprox[1])
                    geomPoints.append(gApprox)
                    
                    if not plotter == None and self.plotEllipse:
                        plotter.plotEllipse(pixelFrustum)
                    
                    sampleScalar = rho.evaluate(pApprox[0], pApprox[1])
                    sampleColors.append(self.transfer(sampleScalar))
                    
                    if not firstIteration:
                        dist = geomPoints[-1] - geomPoints[-2]
                        sampleDeltas.append(math.sqrt(dist[0]**2 + dist[1]**2))
                    
                    firstIteration = False
                    prevUV = pApprox
                else:
                    geomPoints.append(samplePoint)
        else:
            geomPoints = samplePoints
            
        if not plotter == None and self.plotSamplePoints:
            plotter.plotSamplePointsDirect(geomPoints, locations)
        
        return compositing.frontToBack(sampleColors, sampleDeltas)
