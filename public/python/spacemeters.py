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
  El output va tener el dominio de la primer lista
"""
def listMult(x1,y1,x2,y2):
  N = len(x1)
  if min(x1)>max(x2) or max(x1) < min(x2):
    print('Dominio de listas no coincidentes')
    raise
  X = []
  Y = []
  for i in range(N):
    x, y = x1[i], y1[i]
    for j in range(1,len(x2)):
      if x2[j] >= x and x2[j-1] < x:
        X.append(x)
        Y.append( float(y * y2[j]))
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
	

