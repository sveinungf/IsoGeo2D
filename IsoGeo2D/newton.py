import numpy as np
import pylab as plt
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

def f(u):
	return np.array([u, u**3])

def df(u):
	return np.array([1, 3*u**2])

def g(v):
	return np.array([v, -50*v+100])

def dg(v):
	return np.array([1, -50])

def h(u, v):
	return f(u) - g(v)

def hJacob(u, v):
	dfu = df(u)
	dgv = dg(v)
	return np.matrix([[dfu[0], -dgv[0]], [dfu[1], -dgv[1]]])

def newtonsMethod2D(f, fJacob, u, v, tolerance=0.00001, maxAttempts=100):
	attempt = 1
	
	while attempt < maxAttempts:
		[fx, fy] = f(u,v)
		x = solve(fJacob(u,v), [-fx, -fy])
		[u1, v1] = x + [u, v]
		
		if abs(u1 - u) < tolerance and abs(v1 - v) < tolerance:
			break
		
		u = u1
		v = v1
		++attempt
		
	if attempt == maxAttempts:
		return None
		
	return [u, v]


def testplot():
	u = np.linspace(-10, 10, 100)
	v = np.linspace(-10, 10, 100)
	
	fxValues = []
	fyValues = []
	gxValues = []
	gyValues = []
	
	for i in range(len(u)):
		[fx,fy] = f(u[i])
		[gx,gy] = g(v[i])
		fxValues.append(fx)
		fyValues.append(fy)
		gxValues.append(gx)
		gyValues.append(gy)
		
		
	plt.plot(fxValues, fyValues)
	plt.plot(gxValues, gyValues)
	
	uGuess = 4
	vGuess = 4
	uvIntersect = newtonsMethod2D(h, hJacob, uGuess, vGuess)
	[xIntersect, yIntersect] = f(uvIntersect[0])
	plt.plot(xIntersect, yIntersect, marker='x')
	
	plt.show()
	