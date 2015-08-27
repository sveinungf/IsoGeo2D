import numpy
import pylab

class Plotter:
	def __init__(self):
		self.fromX = -10
		self.toX = 10
		self.precision = 100

		pylab.ion()

	def plotFunction(self, f):
		X = numpy.linspace(self.fromX, self.toX, self.precision)
		fY = f(X)

		pylab.plot(X, fY)

	def plotVerticalLine(self, x):
		pylab.vlines(x, -10, 10)

