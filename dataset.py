import fileio.splinereader as splineio
from datasets.sinegeometry import SineGeometry
from datasets.trivialfield import TrivialField
from datasets.trivialgeometry import TrivialGeometry


class Dataset:    
    def __init__(self, rhoNumber, phiNumber):
        self.rhoNumber = rhoNumber
        self.phiNumber = phiNumber
        
        if rhoNumber == 0:
            self.rho = TrivialField()
        else:
            datasetDir = "datasets/" + repr(rhoNumber)
            self.rho = splineio.read(datasetDir + "/rho.json")
            
        if phiNumber == 0:
            self.phi = TrivialGeometry()
        elif phiNumber == 1:
            datasetDir = "datasets/" + repr(phiNumber)
            self.phi = splineio.read(datasetDir + "/phi.json")
        else:
            self.phi = SineGeometry()
