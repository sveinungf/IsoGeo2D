import numpy as np

class Printer:
    def __init__(self):
        pass

    def printDirectDiffs(self, directDiffs):
        print "Direct color diffs:"
        self.__printDiffs(directDiffs)
        
    def printVoxelizedDiffs(self, voxelizedDiffs):
        print "Voxelized color diffs:"
        self.__printDiffs(voxelizedDiffs)

    def __printDiffs(self, diffs):
        print "max  = {}".format(np.amax(diffs))
        print "mean = {}".format(np.mean(diffs))
        print "var  = {}".format(np.var(diffs))
        