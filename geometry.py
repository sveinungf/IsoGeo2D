import abc


class Geometry(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def min(self, axis):
        return

    @abc.abstractmethod
    def max(self, axis):
        return

    @abc.abstractmethod
    def evaluate(self, u, v):
        return

    @abc.abstractmethod
    def evaluatePartialDerivativeU(self, u, v):
        return

    @abc.abstractmethod
    def evaluatePartialDerivativeV(self, u, v):
        return

    @abc.abstractmethod
    def jacob(self, u, v):
        return
