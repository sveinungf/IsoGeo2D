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
    def __init__(self, transfer, superSamplingSteps=20):
        self.dst = np.zeros(4)
        self.prevSample = None
        self.superSamplingSteps = superSamplingSteps
        self.transfer = transfer

    def addSample(self, sample, delta):
        prevSample = self.prevSample
        steps = self.superSamplingSteps

        # TODO: Find cause for this
        if sample.scalar > 1.0:
            sample.scalar = 1.0

        if sample.scalar < 0.0:
            sample.scalar = 0.0

        if prevSample is not None:
            for i in range(steps):
                scalar = prevSample.scalar + (sample.scalar - prevSample.scalar) * i/steps
                c = self.transfer(scalar)

                A = (1.0 - self.dst[3]) * (1.0 - pow(max(1e-8, 1.0-c[3]), delta/0.01/(steps+1)))

                self.dst += A * np.array([c[0], c[1], c[2], 1.0])

        self.prevSample = sample

    def saturated(self):
        return self.dst[3] >= 1.0
