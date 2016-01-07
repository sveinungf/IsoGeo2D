import json
import numpy as np

from splines import Spline2D

def read(filename):
    with open(filename) as dataFile:
        data = json.load(dataFile)
    
    p = data["degree"]
    uKnots = np.array(data["uKnots"])
    vKnots = np.array(data["vKnots"])
    coeffs = np.array(data["coeffs"])
    
    return Spline2D(p, uKnots, vKnots, coeffs)
