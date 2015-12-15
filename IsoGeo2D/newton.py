import math
import numpy as np
import scipy.linalg as linalg

def newtonsMethod1D(f, df, x, tolerance):
	'''
	f is the function f(x) and df its derivative
	x is the first guess
	'''

	while True:
		x1 = x - f(x)/float(df(x))
		t = abs(x1 - x)

		if t < tolerance:
			break

		x = x1

	return x

def clampToInterval(value, interval):
	if interval != None:
		value = interval[0] if value < interval[0] else value
		value = interval[1] if value > interval[1] else value
	
	return value

def newtonsMethod2DTolerance(phi, uvInitialGuess, xyTarget, uvIntervals, tolerance, maxAttempts=20):
	attempt = 1
	u = uvInitialGuess[0]
	v = uvInitialGuess[1]
	uInterval = uvIntervals[0]
	vInterval = uvIntervals[1]
	
	def f(u, v):
		return phi.evaluate(u, v) - xyTarget
	
	xyIterativeGuess = phi.evaluate(u, v)
	
	while attempt < maxAttempts:
		if math.sqrt((xyIterativeGuess[0]-xyTarget[0])**2 + (xyIterativeGuess[1]-xyTarget[1])**2) < tolerance:
			u = clampToInterval(u, uInterval)
			v = clampToInterval(v, vInterval)
			
			return [u, v]
		
		jacob = phi.jacob(u, v) 
		
		x = linalg.solve(jacob, -f(u, v))
		
		[u, v] = x + [u, v]
		u = clampToInterval(u, uInterval)
		v = clampToInterval(v, vInterval)
		
		xyIterativeGuess = phi.evaluate(u, v)
		
		attempt += 1
		
	if attempt == maxAttempts:
		return None
		
	return [u, v]

def newtonsMethod2DIntersect(boundaryPhi, boundaryPhiJacob, ray, uInitialGuess, uInterval, tolerance, maxAttempts=20):
	attempt = 1
	u = uInitialGuess
	v = 0.0
	
	def f(u, v):
		return boundaryPhi(u) - ray.eval(v)
	
	def fJacob(u, v):
		return np.matrix([boundaryPhiJacob(u), -ray.deval(v)]).transpose()
	
	xyBoundaryGuess = boundaryPhi(u)
	xyRayGuess = ray.eval(v)
	
	while attempt < maxAttempts:
		if math.sqrt((xyBoundaryGuess[0]-xyRayGuess[0])**2 + (xyBoundaryGuess[1]-xyRayGuess[1])**2) < tolerance:
			return [u, v]
		
		jacob = fJacob(u, v)
		
		if abs(linalg.det(jacob)) < 1e-6:
			return None
		
		x = linalg.solve(jacob, -f(u, v))
		
		[u, v] = x + [u, v]
		u = clampToInterval(u, uInterval)
		
		xyBoundaryGuess = boundaryPhi(u)
		xyRayGuess = ray.eval(v)
		
		attempt += 1
		
	if attempt == maxAttempts:
		return None
		
	return [u, v]

def newtonsMethod2DFrustum(f, fJacob, uv, clampInterval, phi, frustum, maxAttempts=20):
	attempt = 1
	u = clampToInterval(uv[0], clampInterval)
	v = clampToInterval(uv[1], clampInterval)
	
	while attempt < maxAttempts:
		gApprox = phi.evaluate(u, v)
		
		if frustum.enclosesPoint(gApprox):
			return [u, v]
		
		jacob = fJacob(u, v)
		
		x = linalg.solve(jacob, -f(u, v))
		[u, v] = x + [u, v]
		
		u = clampToInterval(u, clampInterval)
		v = clampToInterval(v, clampInterval)

		attempt += 1
		
	if attempt == maxAttempts:
		return None
		
	return [u, v]
