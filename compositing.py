import itertools
import math
import numpy as np


def frontToBack(rgbaValues, deltas):
    dst = np.zeros(4)
    
    for rgba, delta in itertools.izip(rgbaValues, deltas):
        dst = accumulate(dst, rgba, delta)
    
        if dst[3] >= 1.0:
            break
        
    return dst


def accumulateOld(dst, src, delta):
    xi = 0.01

    t = (1 - src[3])**(delta/xi)
    factor = (1 - t)*(1 - dst[3])

    dst[:3] += factor * src[:3]
    dst[3] += factor

    return dst


def accumulate(dst, src, delta):
    xi = 0.01
    
    t = (1.0 - src[3])**(delta/xi)
    factor = (1.0 - t)*(1.0 - dst[3])

    if (1.0 - dst[3]) < 1e-10:
        factor = 1.0 - dst[3]

    dst[:3] += factor * src[:3]
    dst[3] += factor
    
    return dst


class FrontToBack:
    def __init__(self, transfer):
        self.dst = np.zeros(4)
        self.prevSample = None
        self.transfer = transfer

    def addSample(self, sample):
        prevSample = self.prevSample

        if prevSample is not None:
            prevColor = self.transfer(prevSample.scalar)

            dist = sample.geomPoint - prevSample.geomPoint
            actualDelta = math.sqrt(dist[0]**2 + dist[1]**2)

            accumulate(self.dst, prevColor, actualDelta)

        self.prevSample = sample

    def saturated(self):
        return self.dst[3] >= 1.0
