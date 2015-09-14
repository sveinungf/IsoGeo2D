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
	
def newtonsMethod2DClamped(f, fJacob, uv, clampInterval, tolerance=0.000001, maxAttempts=20):
	attempt = 1
	u = uv[0]
	v = uv[1]
	
	while attempt < maxAttempts:
		u = clampInterval[0] if u < clampInterval[0] else u
		u = clampInterval[1] if u > clampInterval[1] else u
		
		v = clampInterval[0] if v < clampInterval[0] else v
		v = clampInterval[1] if v > clampInterval[1] else v
		
		jacob = fJacob(u, v)
		
		if linalg.det(jacob) == 0:
			return None
		
		x = linalg.solve(jacob, -f(u, v))
		[u1, v1] = x + [u, v]

		if math.sqrt((u1-u)**2 + (v1-v)**2) < tolerance:
			break
		
		u = u1
		v = v1

		attempt += 1
		
	if attempt == maxAttempts:
		return None
		
	return [u, v]
