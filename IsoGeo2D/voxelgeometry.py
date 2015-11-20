import itertools
import numpy as np

import compositing
from samplinglocation import SamplingLocation


class VoxelGeometry:
    samplingDefault = -1
    
    def __init__(self, scalarTexture, transfer, boundingBox, plotter=None, plotSamplePoints=True):
        self.boundingBox = boundingBox
        self.plotter = plotter
        self.scalarTexture = scalarTexture
        self.transfer = transfer
    
    def __getSamplePointLocations(self, samplePoints):
        bb = self.boundingBox
        scalarTexture = self.scalarTexture
        
        locations = np.empty(len(samplePoints))
        
        for i, samplePoint in enumerate(samplePoints):
            if bb.enclosesPoint(samplePoint):
                u = (samplePoint[0]-bb.left)/bb.getWidth()
                v = (samplePoint[1]-bb.bottom)/bb.getHeight()
                
                if not scalarTexture.closest([u, v]) == self.samplingDefault:
                    locations[i] = SamplingLocation.INSIDE_OBJECT
                else:
                    locations[i] = SamplingLocation.OUTSIDE_OBJECT
            else:
                locations[i] = SamplingLocation.OUTSIDE_BOUNDINGBOX
            
        return locations
    
    def raycast(self, viewRay, delta):
        bb = self.boundingBox
        plotter = self.plotter
        scalarTexture = self.scalarTexture
        
        sampleColors = []
        sampleDeltas = []
        
        samplePoints = viewRay.generateSamplePoints(0, 10, delta)
        locations = self.__getSamplePointLocations(samplePoints)
        
        for samplePoint, location in itertools.izip(samplePoints, locations):
            if location == SamplingLocation.INSIDE_OBJECT:
                u = (samplePoint[0]-bb.left)/bb.getWidth()
                v = (samplePoint[1]-bb.bottom)/bb.getHeight()
                
                sampleScalar = scalarTexture.fetch([u, v])
                sampleColors.append(self.transfer(sampleScalar))
                sampleDeltas.append(delta)
        
        if not plotter == None and self.plotSamplePoints:
            plotter.plotSamplePointsVoxelized(samplePoints, locations)
        
        return compositing.frontToBack(sampleColors, sampleDeltas)
