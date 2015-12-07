import math
import matplotlib.gridspec as gridspec
import numpy as np
import pylab as plt
from matplotlib.patches import Ellipse
from matplotlib.patches import Rectangle

from splineplotter import SplinePlotter
from voxelplotter import VoxelPlotter

class Plotter:
	def __init__(self, splineInterval):
		self.splineInterval = splineInterval
		self.precision = 100
		
		plt.figure(figsize=(18, 12))
		mainGrid = gridspec.GridSpec(2, 3)

		gPlotAxis = (-0.5, 1.3, -0.3, 1.3)
		ax = plt.subplot(mainGrid[0, 0])
		ax.axis(gPlotAxis)
		self.gPlot = ax
		self.refSplineModelPlotter = SplinePlotter(ax, splineInterval)
		
		ax = plt.subplot(mainGrid[0, 1])
		ax.axis(gPlotAxis)
		self.directSplineModelPlotter = SplinePlotter(ax, splineInterval)
		
		ax = plt.subplot(mainGrid[0, 2])
		ax.axis(gPlotAxis)
		self.samplingPlot = ax		
		self.voxelModelPlotter = VoxelPlotter(ax)
		
		ax = plt.subplot(mainGrid[1, 0])
		ax.axis((-0.1, 1.1, -0.1, 1.1))
		self.pPlot = ax
		
		ax = plt.subplot(mainGrid[1, 1])
		ax.axis((-0.1, 1.1, -0.1, 1.1))
		self.interpolationPlot = ax
		
		pixelGrid = gridspec.GridSpecFromSubplotSpec(5, 1, subplot_spec=mainGrid[1, 2], hspace=0.4)
		
		ax = plt.subplot(pixelGrid[0])
		ax.set_title("Reference")
		ax.xaxis.set_major_locator(plt.NullLocator()) # Removes ticks
		ax.yaxis.set_major_locator(plt.NullLocator())
		self.pixelReferencePlot = ax
		
		ax = plt.subplot(pixelGrid[1])
		ax.set_title("Direct")
		ax.xaxis.set_major_locator(plt.NullLocator())
		ax.yaxis.set_major_locator(plt.NullLocator())
		self.pixelDirectPlot = ax
		
		ax = plt.subplot(pixelGrid[2])
		ax.set_title("Direct color difference")
		ax.xaxis.set_major_locator(plt.NullLocator())
		ax.yaxis.set_major_locator(plt.NullLocator())
		self.pixelDirectDiffPlot = ax
		
		ax = plt.subplot(pixelGrid[3])
		ax.set_title("Voxelized")
		ax.xaxis.set_major_locator(plt.NullLocator())
		ax.yaxis.set_major_locator(plt.NullLocator())
		self.pixelVoxelizedPlot = ax
		
		ax = plt.subplot(pixelGrid[4])
		ax.set_title("Voxelized color difference")
		ax.xaxis.set_major_locator(plt.NullLocator())
		ax.yaxis.set_major_locator(plt.NullLocator())
		self.pixelVoxelizedDiffPlot = ax
		
		plt.ion()
		plt.show()

	def getPixelPlotAxis(self, numPixels):
		return (-0.5, numPixels-0.5, 0, 1)
	
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
			
			ax = self.pPlot
			ax.plot(paramsX, paramsY, color=lineColor)
			
		for hLine in hLines:
			paramsX = np.linspace(interval[0], interval[1], self.precision)
			paramsY = [hLine] * self.precision
			
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
		ax.plot(points[:,0], points[:,1], color='r')

	def plotViewRayFrustum(self, ray, interval):
		params = np.linspace(interval[0], interval[1], self.precision)
		upperPoints = self.generatePoints1var(ray.evalFrustumUpper, params)
		lowerPoints = self.generatePoints1var(ray.evalFrustumLower, params)
		
		ax = self.gPlot
		ax.plot(upperPoints[:,0], upperPoints[:,1], color='b', linestyle='--')
		ax.plot(lowerPoints[:,0], lowerPoints[:,1], color='b', linestyle='--')
		
	def plotEllipse(self, ellipse):
		point = tuple(ellipse.point)
		degrees = math.degrees(ellipse.angle)
		e = Ellipse(point, ellipse.width, ellipse.height, degrees, fill=False)
		
		ax = self.gPlot
		ax.add_artist(e)
	
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
	
	def __plotPixelColors(self, ax, pixelColors):
		numPixels = len(pixelColors)
		ax.axis(self.getPixelPlotAxis(numPixels))
		
		for i, pixelColor in enumerate(pixelColors):
			r = Rectangle((i-0.5, 0), 1, 1, facecolor=tuple(pixelColor), linewidth=0)
			ax.add_patch(r)
			
	def __plotPixelColorDiffs(self, ax, colorDiffs):
		colors = np.empty((len(colorDiffs), 3))
		
		for i, colorDiff in enumerate(colorDiffs):
			if colorDiff <= 1.0:
				colors[i] = np.array([0.75, 0.75, 0.75])
			elif colorDiff <= 5.0:
				colors[i] = np.array([0.0, 0.0, 1.0])
			elif colorDiff <= 10.0:
				colors[i] = np.array([0.0, 1.0, 0.0])
			else:
				colors[i] = np.array([1.0, 0.0, 0.0])
				
		self.__plotPixelColors(ax, colors)
	
	def plotPixelColorsDirect(self, pixelColors):
		self.__plotPixelColors(self.pixelDirectPlot, pixelColors)
		
	def plotPixelColorsReference(self, pixelColors):
		self.__plotPixelColors(self.pixelReferencePlot, pixelColors)
					
	def plotPixelColorsVoxelized(self, pixelColors):
		self.__plotPixelColors(self.pixelVoxelizedPlot, pixelColors)
		
	def plotPixelColorDiffsDirect(self, colorDiffs):
		self.__plotPixelColorDiffs(self.pixelDirectDiffPlot, colorDiffs)
		
	def plotPixelColorDiffsVoxelized(self, colorDiffs):
		self.__plotPixelColorDiffs(self.pixelVoxelizedDiffPlot, colorDiffs)
		
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
