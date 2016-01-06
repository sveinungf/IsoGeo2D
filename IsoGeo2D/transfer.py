import math
import numpy as np

def createTransferArray(n):
    result = []
    
    incr = np.linspace(0.0, 1.0, n/4)
    decr = np.linspace(1.0, 0.0, n/4)
    
    for val in incr:
        result.append(np.array([0.0, val, 1.0, 0.9]))
        
    for val in decr:
        result.append(np.array([0.0, 1.0, val, 0.5]))
        
    for val in incr:
        result.append(np.array([val, 1.0, 0.0, 0.7]))
        
    for val in decr:
        result.append(np.array([1.0, val, 0.0, 0.9]))
        
    return result

def createTransferFunction(n):
    array = createTransferArray(n)
    
    def transfer(x):
        index = int(math.floor(x * (n-1)))
        return array[index]
    
    return transfer
