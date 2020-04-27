# Colab setup
import pandas as pd
import matplotlib.pyplot as plt
import requests

# Constantes

h = 6.62607015e-34    # Planck constant       # m² kg s⁻¹
boltz = 1.38064852e-23  # Boltzmann constant  # m² kg s⁻² K⁻¹
stefan = 5.67e-8 # Stefan-boltzmann constant  # W m⁻² K⁻⁴
q = 1.60217662e-19 # Fundamental   charge     # Coulomb
c = 299792458 # Light speed                   # m s⁻¹
pi = 3.14159265358979323846264338328
e = 2.7182818284590452353602874713527


def irradianceToPower(IR, altitudeSatellite , areaObsTierra , areaLente ): #iradiance from earth to power upstream the satellite lens
  RT = 6371e3 # earth radius in meters [m]
  h_space = 100e3 # Altitude of space in meters (as 6S sets it)
  factor = areaObsTierra * areaLente * (RT + altitudeSatellite)**-2
  I = []
  for i in range(len(IR)):
    I.append( factor * IR[i] )
  return I # Returns W/m^2/micrometer

def frecuencyToWavelength(frec):
  wl = []
  for i in range(len(frec)):
    nu = float(frec[i])
    wl.append(1e4/nu)
  return wl

#SPECTRA
def isCSVSorted(filename):
	dfcheck = pd.read_csv(filename)
	nu = dfcheck["nu"]
	ab = dfcheck[simCol]
	isSorted = True
	for i in range(1,len(ab)):
		if  abs(nu[i]-nu[i-1]) > 1 or nu[i] == nu[i-1]: 
			print('index ',i,' detect badness:nu1=',nu[i-1],', nu2=',nu[i],sep='')
			print(dfcheck[i-2:i+2])
			isSorted = False
	plt.plot(nu,ab)
	plt.show()
	return isSorted


# MATH
"""
  Interpola en una recta definida por los vectores de longitud 2 `xvalues`, `yvalues` 
  sobre el punto x  `xint`.
"""
def interpolate(xint, xvalues, yvalues):
  if xint < xvalues[0] or xint > xvalues[1]:
    raise ValueError("interp tried to extrapolate and that is wrong.")
  return float(yvalues[0] + (xint - xvalues[0])/(xvalues[1] - xvalues[0]) * (yvalues[1] - yvalues[0]))

"""
función que interpola los valores de Y2 para matchear con x1, se necesita pasarle el dominio x1 (master) y la función x2 (slave) e y2
el dominio de x2 tiene que abarcar al de x1 ya que el programa interpola linealmente a y2 y no extrapola
"""
def listInterpolate(x1,x2,y2):
  if min(x1)<min(x2):
    raise Exception("Mínimo de x1 es menor al mínimo de x2, cambiarlo para que el rango de x2 abarque al de x1. \n") 
  elif max(x1)>max(x2):
    raise Exception("Máximo de x1 es mayor al máximo de x2, cambiarlo para que el rango de x2 abarque al de x1. \n")
  
  N =len(x1)
  y2New = [0 for x in range(N)] 
  
  for i in range(N):
    x = x1[i]
    for j in range(1,len(x2)):
      if x2[j-1]<= x and x < x2[j]:
        y2New[i] = interpolate(x, x2[j-1:j+1], y2[j-1:j+1])
  return y2New

"""
Integrates a (x,y) iterable pair using trapezoidal rule. 
Only integrates between xv[0] and xv[len(xv)]. Skips NaN values.
"""
def Intgrt(xv,yv):
  theSum=0
  N = len(xv)
  for i in range(1,N):
    dx = xv[i] - xv[i-1]
    ymax, ymin = max(yv[i-1:i+1]), min(yv[i-1:i+1])
    if ymax!=ymax or ymin!=ymin: #skips nan values
      continue
    triang = dx * (ymax-ymin)/2
    box = dx * ymin
    theSum += triang + box
  return theSum

"""
  Multiplicamos dos se~nales de iterables, cada una tiene su dominio
  El output va tener el dominio de la primer lista. por defecto interpola linealmente
  `interp` bool. Si es falso no interpola
"""
def listMult(x1,y1,x2,y2, interp=True):
  N = len(x1)
  if min(x1)>max(x2) or max(x1) < min(x2):
    raise ValueError('Dominio de listas no coincidentes')
  X = []
  Y = []
  for i in range(N):
    x, y = x1[i], y1[i]
    for j in range(1,len(x2)):
      if x2[j] >= x and x2[j-1] < x:
        yint = interpolate(x, x2[j-1:j+1],y2[j-1:j+1]) if interp else y2[j]
        X.append(x)
        Y.append( float(y * yint))
  return X, Y


def sin(x):
  return ((e**(1j*x) - e**(-1j*x))/2j).real
def cos(x):
  return ((e**(1j*x) + e**(-1j*x))/2).real


#EXTRA/unused
def irradianceToIntensity(IR, altitudeSatellite,areaObsTierra):
  pi = 3.14159265359
  RT = 6371e3 # earth radius in meters [m]
  h_space = 100e3 # Altitude of space in meters (as 6S sets it)
  #  factor = 4*pi*RT**2 * (RT + altitudeSatellite)**-2 # OLD
  factor = areaObsTierra  * (RT + altitudeSatellite)**-2
  I = []
  for i in range(len(IR)):
    I.append( factor * IR[i] )
  return I # Returns W/m^2/micrometer

"""
Downloads file from internet to director with url endpoint
name by default (like !wget). Can specify optional keyword arguments:

	`filename`: Filename to be saved as. String.
	`dir`: Directory to save to. Can be absolute or relative
	`prnt`: Print file contents. Default False.
"""
def wget(url, **args):
    filename = args["name"] if "name" in args else url[url.rfind('/') + 1::]
    dir = args["dir"]+filename if "dir" in args else filename
    showContents = args["prnt"] if "dir" in args else False
    try:
      r = requests.get(url, allow_redirects=True)
    except:
      raise ValueError('Error retrieving ' + url)
    with open(dir, 'wb') as f:
        f.write(r.content)
    if showContents:
    	print(r.content)
	
def wgetData(url, **args):
    args["dir"] = "data"
    wget(url, args)
	
"""
   replaces NaN values with values closest to the right.
"""
def bridgeNans(lst): 
  N = len(lst)
  for i in range(N):
    if lst[i] != lst[i]:
      if i == N-1:
        lst[i] = lst[i-1]
      for j in range(i,N):
        if lst[j] == lst[j]:
          lst[i] = lst[j]
          break
  return lst

# TESTS!
dom = [0.01 * i for i in range(1000)]
xv = dom[200:800]
yv = [sin(x) for x in xv]
uv = dom[300:700] # reduzco el dominio de la segunda señal
vv = [sin(3*x+3.1415/2) for x in uv]

listInterpolate(uv, xv, yv)

X,Y = listMult(xv,yv,uv,vv, interp=False)
plt.plot(X,Y);plt.title('Demo de listMult()');plt.show()

# print(interp(.2,[0, 2],[20, 40]))