import itertools
import numpy as np
import pylab as plt

class Plotter:
	def __init__(self, splineInterval):
		self.splineInterval = splineInterval
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
		
	def plotGrids(self, f, m, n):
		interval = self.splineInterval
		vLines = np.linspace(interval[0], interval[1], m)
		hLines = np.linspace(interval[0], interval[1], n)
		lineColor = '0.5'
		
		for vLine in vLines:
			paramsX = [vLine] * self.precision
			paramsY = np.linspace(interval[0], interval[1], self.precision)
			
			[geomX, geomY] = self.generatePoints(f, paramsX, paramsY)
			
			self.selectGPlot()
			plt.plot(geomX, geomY, color=lineColor)
			
			self.selectPPlot()
			plt.plot(paramsX, paramsY, color=lineColor)
			
		for hLine in hLines:
			paramsX = np.linspace(interval[0], interval[1], self.precision)
			paramsY = [hLine] * self.precision
			
			[geomX, geomY] = self.generatePoints(f, paramsX, paramsY)
			
			self.selectGPlot()
			plt.plot(geomX, geomY, color=lineColor)
			
			self.selectPPlot()
			plt.plot(paramsX, paramsY, color=lineColor)
		
	def plotScalarField(self, rho, transfer):
		interval = self.splineInterval
		uRange = np.linspace(interval[0], interval[1], self.precision)
		vRange = np.linspace(interval[1], interval[0], self.precision)
		
		img = []
		
		for v in vRange:
			row = []
			
			for u in uRange:
				x = rho.evaluate(u,v)
				row.append(transfer(x[0]))
		
			img.append(row)
		
		plt.imshow(img, aspect='auto', extent=(interval[0], interval[1], interval[0], interval[1]))
	
	def plotLine(self, f, interval):
		params = np.linspace(interval[0], interval[1], self.precision)
		points = self.generatePoints1(f, params)
		
		self.selectGPlot()
		plt.plot(points[:,0], points[:,1], color='k')
	
	def plotIntersectionPoints(self, points):
		self.selectGPlot()
		
		for point in points:
			plt.plot(point[0], point[1], marker='o', color='b')

	def plotGeomPoints(self, points, colors):
		self.selectGPlot()
		
		for point, c in itertools.izip(points, colors):
			plt.plot(point[0], point[1], marker='.', color=tuple(c))
			
	def plotParamPoints(self, points):
		self.selectPPlot()
		
		for point in points:
			plt.plot(point[0], point[1], marker='x', color='k')
		
	def draw(self):
		plt.draw()
