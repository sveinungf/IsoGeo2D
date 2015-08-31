import numpy as np
import pylab as plt

class Plotter:
	def __init__(self):
		self.precision = 100

	def plot(self, f):
		asdf = [0, 0.5, 1]
		
		for asd in asdf:
			paramsX = [asd] * self.precision
			paramsY = np.linspace(0, 1, self.precision)
			
			geomX = []
			geomY = []
			
			for i in range(len(paramsX)):
				fResult = f(paramsX[i], paramsY[i])
				geomX.append(fResult[0])
				geomY.append(fResult[1])
			
			plt.subplot(1, 2, 1)
			plt.plot(geomX, geomY)
			#plt.axis((-0.1, 1.1, -0.1, 1.1))
			
			# Parameter domain
			plt.subplot(1, 2, 2)
			plt.plot(paramsX, paramsY)
			plt.axis((-0.1, 1.1, -0.1, 1.1))
		
		plt.show()
