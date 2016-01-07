import fileio.splinereader as splineio
from splines import Spline2DTrivialR1, Spline2DTrivialR2

class Dataset:    
    def __init__(self, rhoNumber, phiNumber):
        self.rhoNumber = rhoNumber
        self.phiNumber = phiNumber
        
        if rhoNumber == 0:
            self.rho = Spline2DTrivialR1()
        else:
            datasetDir = "datasets/" + `rhoNumber`
            self.rho = splineio.read(datasetDir + "/rho.json")
            
        if phiNumber == 0:
            self.phi = Spline2DTrivialR2()
        else:
            datasetDir = "datasets/" + `phiNumber`
            self.phi = splineio.read(datasetDir + "/phi.json")
