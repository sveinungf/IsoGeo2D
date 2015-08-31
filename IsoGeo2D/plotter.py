import numpy as np
import pylab as plt

class Plotter:
	def __init__(self):
		self.precision = 100

	def generatePoints(self, f, xInput, yInput):
		xOutput = []
		yOutput = []
		
		for i in range(len(xInput)):
			fResult = f(xInput[i], yInput[i])
			xOutput.append(fResult[0])
			yOutput.append(fResult[1])
		
		return [xOutput, yOutput]
		
	def plot(self, f, m, n):
		vLines = np.linspace(0, 1, m)
		hLines = np.linspace(0, 1, n)
		
		for vLine in vLines:
			paramsX = [vLine] * self.precision
			paramsY = np.linspace(0, 1, self.precision)
			
			[geomX, geomY] = self.generatePoints(f, paramsX, paramsY)
			
			plt.subplot(1, 2, 1)
			plt.plot(geomX, geomY)
			
			plt.subplot(1, 2, 2)
			plt.plot(paramsX, paramsY)
			
		for hLine in hLines:
			paramsX = np.linspace(0, 1, self.precision)
			paramsY = [hLine] * self.precision
			
			[geomX, geomY] = self.generatePoints(f, paramsX, paramsY)
			
			plt.subplot(1, 2, 1)
			plt.plot(geomX, geomY)
			
			plt.subplot(1, 2, 2)
			plt.plot(paramsX, paramsY)
		
		plt.subplot(1, 2, 1)
		plt.axis((-0.1, 1.1, -0.1, 1.1))
		
		plt.subplot(1, 2, 2)
		plt.axis((-0.1, 1.1, -0.1, 1.1))
		
		plt.show()
