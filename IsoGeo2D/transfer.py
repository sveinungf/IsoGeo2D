import numpy as np

def createTransferArray(n):
    result = []
    
    incr = np.linspace(0.0, 1.0, n/4)
    decr = np.linspace(1.0, 0.0, n/4)
    
    for val in incr:
        result.append([0.0, val, 1.0, 1.0])
        
    for val in decr:
        result.append([0.0, 1.0, val, 1.0])
        
    for val in incr:
        result.append([val, 1.0, 0.0, 1.0])
        
    for val in decr:
        result.append([1.0, val, 0.0, 1.0])
        
    return result

def createTransferFunction(n):
    array = createTransferArray(n)
    
    def transfer(x):
        index = int(x * n)
        return array[index]
    
    return transfer
