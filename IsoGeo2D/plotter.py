import itertools
import numpy as np
import pylab as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
from samplingtag import SamplingTag

class Plotter:
	def __init__(self, splineInterval, numPixels):
		self.splineInterval = splineInterval
		self.precision = 100
		
		plt.figure(figsize=(14, 12))
		gridSpec = GridSpec(2, 3, width_ratios=[10, 10, 1])
		self.gridSpec = gridSpec
		
		gPlotAxis = (-0.6, 1.3, -0.2, 1.3)
		ax = plt.subplot(gridSpec[0, 0])
		ax.axis(gPlotAxis)
		self.gPlot = ax
		
		ax = plt.subplot(gridSpec[0, 1])
		ax.axis((-0.1, 1.1, -0.1, 1.1))
		self.pPlot = ax
		
		ax = plt.subplot(gridSpec[1, 0])
		ax.axis(gPlotAxis)
		self.samplingPlot = ax
		
		ax = plt.subplot(gridSpec[1, 1])
		ax.axis((-0.1, 1.1, -0.1, 1.1))
		self.interpolationPlot = ax

		ax = plt.subplot(gridSpec[1, 2])
		ax.axis((0, 1, -0.5, numPixels-0.5))
		ax.set_yticks(np.arange(numPixels))
		ax.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
		self.pixelPlot = ax
		
		plt.ion()
		plt.show()

	def generatePoints2var(self, f, xInputs, yInputs):
		xOutput = []
		yOutput = []
		
		for i in range(len(xInputs)):
			fResult = f(xInputs[i], yInputs[i])
			xOutput.append(fResult[0])
			yOutput.append(fResult[1])
		
		return [xOutput, yOutput]
	
	def generatePoints1var(self, f, params):
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
			
			[geomX, geomY] = self.generatePoints2var(f, paramsX, paramsY)
			
			ax = self.gPlot
			ax.plot(geomX, geomY, color=lineColor)
			
			ax = self.pPlot
			ax.plot(paramsX, paramsY, color=lineColor)
			
		for hLine in hLines:
			paramsX = np.linspace(interval[0], interval[1], self.precision)
			paramsY = [hLine] * self.precision
			
			[geomX, geomY] = self.generatePoints2var(f, paramsX, paramsY)
			
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
	
	def plotSamplingRay(self, ray, interval):
		params = np.linspace(interval[0], interval[1], self.precision)
		points = self.generatePoints1var(ray.evalFromEye, params)
		
		ax = self.gPlot
		ax.plot(points[:,0], points[:,1], color='k')
		
	def plotViewRay(self, ray, interval):
		params = np.linspace(interval[0], interval[1], self.precision)
		points = self.generatePoints1var(ray.evalFromEye, params)
		
		ax = self.samplingPlot
		ax.plot(points[:,0], points[:,1], color='r')
	
	def plotIntersectionPoints(self, points):
		ax = self.gPlot
		
		for point in points:
			ax.plot(point[0], point[1], marker='o', color='b')

	def plotGeomPoints(self, points):
		ax = self.gPlot

		for point in points:
			ax.plot(point[0], point[1], marker='x', color='k')
			
	def plotParamPoints(self, points):
		ax = self.pPlot
		
		for point in points:
			ax.plot(point[0], point[1], marker='x', color='k')
			
	def plotSamplePoints(self, points, tags):
		ax = self.samplingPlot
		
		for point,tag in itertools.izip(points,tags):
			if tag == SamplingTag.IN_TEXTURE:
				pointColor = 'g'
			elif tag == SamplingTag.NOT_IN_TEXTURE:
				pointColor = '#de7e00'
			else:
				pointColor = 'r'
				

			ax.plot(point[0], point[1], marker='o', color=pointColor)
			
	def plotPixelPoints(self, pixels):
		ax = self.gPlot
		
		for i, pixel in enumerate(pixels):
			ax.text(pixel[0], pixel[1], str(i))
		
	def plotPixelColors(self, pixelColors):
		ax = self.pixelPlot
		
		for i, pixelColor in enumerate(pixelColors):
			r = Rectangle((0, i-0.5), 1, 1, facecolor=tuple(pixelColor))
			ax.add_patch(r)
		
	def plotBoundingBox(self, boundingBox):
		lowerLeft = (boundingBox.left, boundingBox.bottom)
		width = boundingBox.getWidth()
		height = boundingBox.getHeight()
		
		r = Rectangle(lowerLeft, width, height, fill=False, linestyle='dashed')
		self.gPlot.add_patch(r)
		
		r = Rectangle(lowerLeft, width, height, fill=False, linestyle='dashed')
		self.samplingPlot.add_patch(r)
			
	def plotSampleScalars(self, scalars, boundingBox):
		ax = self.samplingPlot
		deltaX = boundingBox.getWidth() / float(len(scalars[0]))
		deltaY = boundingBox.getHeight() / float(len(scalars))
		
		for (i, j), scalar in np.ndenumerate(scalars):
			if not scalar == -1:
				lowerLeft = (boundingBox.left+j*deltaX, boundingBox.bottom+i*deltaY)
				r = Rectangle(lowerLeft, deltaX, deltaY, facecolor=tuple([scalar]*3))
				ax.add_patch(r)
		
	def plotSampleColors(self, colors, boundingBox):
		ax = self.samplingPlot
		deltaX = boundingBox.getWidth() / float(len(colors[0]))
		deltaY = boundingBox.getHeight() / float(len(colors))
		
		for i in range(len(colors)):
			for j in range(len(colors[0])):
				color = colors[i][j]
				
				if not color[3] == 0:
					lowerLeft = (boundingBox.left+j*deltaX, boundingBox.bottom+i*deltaY)
					r = Rectangle(lowerLeft, deltaX, deltaY, facecolor=tuple(color))
					ax.add_patch(r)
		
	def plotScalarTexture(self, scalarTexture):
		uRange = np.linspace(0, 1, self.precision)
		vRange = np.linspace(1, 0, self.precision)
		
		img = []
		
		for v in vRange:
			row = []
			
			for u in uRange:
				x = scalarTexture.fetch([u, v])
				x = max(0.,x)
				row.append((x,x,x))
		
			img.append(row)
		
		ax = self.interpolationPlot
		ax.imshow(img, aspect='auto', extent=(0, 1, 0, 1))
		
	def draw(self):
		plt.draw()
