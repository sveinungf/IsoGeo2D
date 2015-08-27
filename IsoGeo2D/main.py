import newton
from plotter import Plotter

def f(x):
    return x**3

def df(x):
    return 3*x**2

def g(x):
    return -40*x + 500

def dg(x):
    return -40

def h(x):
    return f(x) - g(x)

def dh(x):
    return df(x) - dg(x)

def main():
    x = newton.newtonsMethod(h, dh, 7, 0.00001)

    plotter = Plotter()
    plotter.plotFunction(f)
    plotter.plotFunction(g)
    plotter.plotVerticalLine(x)
