import matplotlib.pyplot as plt
import numpy as np
from scipy import interpolate


fig = plt.figure(figsize=[10, 6])

p = 3
t = [0, 0, 0, 0, 1, 1.5, 2, 2.5, 3.3, 4, 5, 5, 5, 5]
t_avg = []

for i in range(len(t) - p):
    avg = sum(t[i:i+3]) / float(p)
    t_avg.append(avg)

c = [0, 2.5, 1, 2.9, 3, 2.9, 2.7, 1.5, 0, 1.53]
tck = [t, c, p]

x = np.linspace(0.0, 5.0, 1000)
y = interpolate.splev(x, tck)

plt.plot(t_avg[1:], c, color='b', marker='o')
plt.plot(x, y, color='g')

fig.tight_layout()
plt.savefig("output/vg/spline.pdf", format="pdf", transparent=True)
