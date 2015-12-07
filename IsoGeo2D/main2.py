import numpy as np

import splineexample
import transfer as trans
from plotter.pixelfigure import PixelFigure
from ray import Ray2D
from splinemodel import SplineModel
from splineplane import SplinePlane

class Main2:
    def __init__(self):
        self.splineInterval = [0, 0.99999]
        self.rho = splineexample.createRho()
        self.phi = splineexample.createPhi()
        self.phiPlane = SplinePlane(self.phi, self.splineInterval, 0.00001)
        self.transfer = trans.createTransferFunction(100)

        self.numPixels = 100
        self.pixelX = -0.5
        self.screenTop = 0.90
        self.screenBottom = 0.2
        
        self.eye = np.array([-2.0, 0.65])
        self.viewRayDelta = 0.1
        self.viewRayDeltaRef = 0.01
        self.refTolerance = 0.000000001
        
    def createPixels(self, numPixels):
        pixels = np.empty((numPixels, 2))
        pixelXs = np.ones(numPixels) * self.pixelX
        
        deltaY = (self.screenTop - self.screenBottom) / numPixels
        firstPixelY = self.screenBottom + (deltaY/2.0)
        lastPixelY = self.screenTop - (deltaY/2.0)
        
        pixels[:,0] = pixelXs
        pixels[:,1] = np.linspace(firstPixelY, lastPixelY, numPixels)
        
        return pixels
        
    def run(self):
        numPixels = self.numPixels
        
        figure = PixelFigure()
        
        splineModel = SplineModel(self.phiPlane, self.rho, self.transfer)

        refPixels = self.createPixels(numPixels)
        refPixelWidth = (self.screenTop-self.screenBottom) / numPixels
        refPixelColors = np.empty((numPixels, 4))
        
        for i, refPixel in enumerate(refPixels):
            viewRay = Ray2D(self.eye, refPixel, 10, refPixelWidth)
            
            intersections = splineModel.phiPlane.findTwoIntersections(viewRay)
            
            if intersections != None:
                refPixelColors[i] = splineModel.raycast(viewRay, intersections, self.viewRayDeltaRef, tolerance=self.refTolerance)
            else:
                refPixelColors[i] = np.array([0.0, 0.0, 0.0, 0.0])
        
        figure.refPixelsPlot.plotPixelColors(refPixelColors)
        
        figure.draw()
    
def run():
    main = Main2()
    main.run()

if __name__ == "__main__":
    run()
