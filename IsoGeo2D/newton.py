import math
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
	
def newtonsMethod2DTolerance(f, fJacob, uv, uvIntervals, tolerance, maxAttempts=20):
	attempt = 1
	u = uv[0]
	v = uv[1]
	uInterval = uvIntervals[0]
	vInterval = uvIntervals[1]
	
	while attempt < maxAttempts:
		u = clampToInterval(u, uInterval)
		v = clampToInterval(v, vInterval)
				
		jacob = fJacob(u, v)
		
		x = linalg.solve(jacob, -f(u, v))
		[u1, v1] = x + [u, v]

		if math.sqrt((u1-u)**2 + (v1-v)**2) < tolerance:
			return [u1, v1]
		
		u = u1
		v = v1

		attempt += 1

	if attempt == maxAttempts:
		return None
		
	return [u, v]

def newtonsMethod2DFrustum(f, fJacob, uv, clampInterval, phi, frustum, maxAttempts=20):
	attempt = 1
	u = uv[0]
	v = uv[1]
	
	while attempt < maxAttempts:
		jacob = fJacob(u, v)
		
		x = linalg.solve(jacob, -f(u, v))
		[u, v] = x + [u, v]
		
		u = clampToInterval(u, clampInterval)
		v = clampToInterval(v, clampInterval)
		
		gApprox = phi.evaluate(u, v)
		
		if frustum.enclosesPoint(gApprox):
			return [u, v]

		attempt += 1
		
	if attempt == maxAttempts:
		return None
		
	return [u, v]
