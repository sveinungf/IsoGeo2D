import abc


class Field(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def evaluate(self, u, v):
        return
