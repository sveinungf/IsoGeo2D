import itertools
import numpy as np
import pylab as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle

class Plotter:
	def __init__(self, splineInterval, numPixels):
		self.splineInterval = splineInterval
		self.precision = 100
		
		plt.figure(figsize=(15,5))
		gridSpec = GridSpec(2, 3, height_ratios=[4, 1])
		self.gridSpec = gridSpec
		
		ax = plt.subplot(gridSpec[:, 0])
		ax.axis((-0.6, 1.1, -0.1, 1.1))
		self.gPlot = ax
		
		ax = plt.subplot(gridSpec[:, 1])
		ax.axis((-0.1, 1.1, -0.1, 1.1))
		self.pPlot = ax
		
		ax = plt.subplot(gridSpec[0, 2])
		ax.axis((-0.1, numPixels-0.9, -0.1, 1.1))
		ax.set_xticks(np.arange(numPixels))
		self.pixelComponentsPlot = ax
		
		ax = plt.subplot(gridSpec[1, 2])
		ax.axis((-0.1, numPixels-0.9, -0.1, 1.1))
		ax.set_xticks(np.arange(numPixels))
		self.pixelPlot = ax
		
		plt.ion()
		plt.show()

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
			
			ax = self.gPlot
			ax.plot(geomX, geomY, color=lineColor)
			
			ax = self.pPlot
			ax.plot(paramsX, paramsY, color=lineColor)
			
		for hLine in hLines:
			paramsX = np.linspace(interval[0], interval[1], self.precision)
			paramsY = [hLine] * self.precision
			
			[geomX, geomY] = self.generatePoints(f, paramsX, paramsY)
			
			ax = self.gPlot
			ax.plot(geomX, geomY, color=lineColor)
			
			ax = self.pPlot
			ax.plot(paramsX, paramsY, color=lineColor)
		
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
		
		ax = self.pPlot
		ax.imshow(img, aspect='auto', extent=(interval[0], interval[1], interval[0], interval[1]))
	
	def plotLine(self, f, interval):
		params = np.linspace(interval[0], interval[1], self.precision)
		points = self.generatePoints1(f, params)
		
		ax = self.gPlot
		ax.plot(points[:,0], points[:,1], color='k')
	
	def plotIntersectionPoints(self, points):
		ax = self.gPlot
		
		for point in points:
			ax.plot(point[0], point[1], marker='o', color='b')

	def plotGeomPoints(self, points, colors):
		ax = self.gPlot
		
		for point, c in itertools.izip(points, colors):
			ax.plot(point[0], point[1], marker='.', color=tuple(c))
			
	def plotParamPoints(self, points):
		ax = self.pPlot
		
		for point in points:
			ax.plot(point[0], point[1], marker='x', color='k')
		
	def draw(self):
		plt.draw()
