import math
import matplotlib.gridspec as gridspec
import numpy as np
import pylab as plt
from matplotlib.patches import Ellipse

from paramplotter import ParamPlotter
from pixelplotter import PixelPlotter
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
		self.paramPlotter = ParamPlotter(ax, splineInterval)
		
		ax = plt.subplot(mainGrid[1, 1])
		ax.axis((-0.1, 1.1, -0.1, 1.1))
		self.interpolationPlot = ax
		
		pixelGrid = gridspec.GridSpecFromSubplotSpec(6, 1, subplot_spec=mainGrid[1, 2], hspace=0.4)
		
		ax = plt.subplot(pixelGrid[0])
		self.pixelReferencePlot = PixelPlotter(ax, "Reference")
		
		ax = plt.subplot(pixelGrid[2])
		self.pixelDirectPlot = PixelPlotter(ax, "Direct")
		
		ax = plt.subplot(pixelGrid[3])
		self.pixelDirectDiffPlot = PixelPlotter(ax, "Direct color difference")
		
		ax = plt.subplot(pixelGrid[4])
		self.pixelVoxelizedPlot = PixelPlotter(ax, "Voxelized")
		
		ax = plt.subplot(pixelGrid[5])
		self.pixelVoxelizedDiffPlot = PixelPlotter(ax, "Voxelized color difference")
		
		plt.ion()
		plt.show()
	
	def generatePoints1var(self, f, params):
		output = np.empty((len(params), 2))
		
		for i, param in enumerate(params):
			output[i] = f(param)
		
		return output
	
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
		
	def plotScalarTexture(self, scalarTexture, transfer=None):
		uRange = np.linspace(0, 1, self.precision)
		vRange = np.linspace(1, 0, self.precision)
		
		img = []
		
		for v in vRange:
			row = []
			
			for u in uRange:
				x = scalarTexture.fetch([u, v])
				
				if x == -1:
					if transfer == None:
						cell = [0.0, 0.0, 1.0]
					else:
						cell = [0.0, 0.0, 0.0]
				else:
					if transfer == None:
						cell = [x, x, x]
					else:
						cell = transfer(x)[:3]
						
				row.append(cell)
		
			img.append(row)
		
		ax = self.interpolationPlot
		ax.imshow(img, aspect='auto', extent=(0, 1, 0, 1))
		
	def draw(self):
		plt.draw()
