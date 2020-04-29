from spacemeters import *

yv = [5,10,20,nan,nan,70,nan,nan]
xv = range(len(yv))
yr = interpolateNans(xv,yv)
fig, ax = plt.subplots()
ax.plot(xv,yv,'o'); ax.plot(xv,yr)
plt.show()