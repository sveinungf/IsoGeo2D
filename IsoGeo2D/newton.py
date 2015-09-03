from scipy.linalg import solve

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


def newtonsMethod2D(f, fJacob, u, v, tolerance=0.00001, maxAttempts=100):
	attempt = 1
	
	while attempt < maxAttempts:
		x = solve(fJacob(u,v), -f(u,v))
		[u1, v1] = x + [u, v]
		
		if abs(u1 - u) < tolerance and abs(v1 - v) < tolerance:
			break
		
		u = u1
		v = v1
		++attempt
		
	if attempt == maxAttempts:
		return None
		
	return [u, v]
