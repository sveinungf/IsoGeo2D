import datasets.peakstransfer as peakstransfer
import datasets.simpletransfer as simpletransfer
import datasets.trivialtransfer as trivialtransfer
import fileio.splinereader as splineio
from datasets.sinefield import SineField
from datasets.sinegeometry import SineGeometry
from datasets.trivialfield import TrivialField
from datasets.trivialgeometry import TrivialGeometry


class Dataset:    
    def __init__(self, rhoNumber, phiNumber, tfNumber):
        self.rhoNumber = rhoNumber
        self.phiNumber = phiNumber
        self.tfNumber = tfNumber
        
        if rhoNumber == 0:
            self.rho = TrivialField()
        elif rhoNumber == 1:
            datasetDir = "datasets/" + repr(rhoNumber)
            self.rho = splineio.read(datasetDir + "/rho.json")
        else:
            self.rho = SineField()
            
        if phiNumber == 0:
            self.phi = TrivialGeometry()
        elif phiNumber == 1:
            datasetDir = "datasets/" + repr(phiNumber)
            self.phi = splineio.read(datasetDir + "/phi.json")
        else:
            self.phi = SineGeometry()

        if tfNumber == 0:
            self.tf = trivialtransfer.createTransferFunction()
        elif tfNumber == 1:
            self.tf = simpletransfer.createTransferFunction()
        else:
            self.tf = peakstransfer.createTransferFunction()
