import numpy as np
import pylab as plt

class Plotter:
	def __init__(self):
		self.precision = 100
		
		self.selectGPlot()
		plt.axis((-0.6, 1.1, -0.1, 1.1))
		
		self.selectPPlot()
		plt.axis((-0.1, 1.1, -0.1, 1.1))
		
		plt.ion()
		plt.show()
	
	def selectGPlot(self):
		plt.subplot(1, 2, 1)
		
	def selectPPlot(self):
		plt.subplot(1, 2, 2)

	def generatePoints(self, f, xInputs, yInputs):
		xOutput = []
		yOutput = []
		
		for i in range(len(xInputs)):
			fResult = f(xInputs[i], yInputs[i])
			xOutput.append(fResult[0])
			yOutput.append(fResult[1])
		
		return [xOutput, yOutput]
	
	def generatePoints1(self, f, params):
		output = np.empty((len(params), 2))
		
		for i, param in enumerate(params):
			output[i] = f(param)
		
		return output
		
	def plotSurfaces(self, f, xInterval, yInterval, m, n):
		vLines = np.linspace(xInterval[0], xInterval[1], m)
		hLines = np.linspace(yInterval[0], yInterval[1], n)
		
		for vLine in vLines:
			paramsX = [vLine] * self.precision
			paramsY = np.linspace(yInterval[0], yInterval[1], self.precision)
			
			[geomX, geomY] = self.generatePoints(f, paramsX, paramsY)
			
			self.selectGPlot()
			plt.plot(geomX, geomY)
			
			self.selectPPlot()
			plt.plot(paramsX, paramsY)
			
		for hLine in hLines:
			paramsX = np.linspace(xInterval[0], xInterval[1], self.precision)
			paramsY = [hLine] * self.precision
			
			[geomX, geomY] = self.generatePoints(f, paramsX, paramsY)
			
			self.selectGPlot()
			plt.plot(geomX, geomY)
			
			self.selectPPlot()
			plt.plot(paramsX, paramsY)
		
	
	def plotLine(self, f, interval):
		params = np.linspace(interval[0], interval[1], self.precision)
		points = self.generatePoints1(f, params)
		
		self.selectGPlot()
		plt.plot(points[:,0], points[:,1])
	
	def plotIntersectionPoints(self, points):
		self.selectGPlot()
		
		for point in points:
			plt.plot(point[0], point[1], marker='o', color='b')

	def plotGeomPoints(self, points):
		self.selectGPlot()
		
		for point in points:
			plt.plot(point[0], point[1], marker='x', color='r')
			
	def plotParamPoints(self, points):
		self.selectPPlot()
		
		for point in points:
			plt.plot(point[0], point[1], marker='x', color='r')
		
	def draw(self):
		plt.draw()
