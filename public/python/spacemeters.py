# Colab setup
import pandas as pd
import matplotlib.pyplot as plt
import requests
import subprocess as sp
from pathlib import Path
from string import Template
from Py6S import *


# Constantes
h = 6.62607015e-34    # Planck constant       # m² kg s⁻¹
boltz = 1.38064852e-23  # Boltzmann constant  # m² kg s⁻² K⁻¹
stefan = 5.67e-8 # Stefan-boltzmann constant  # W m⁻² K⁻⁴
q = 1.60217662e-19 # Fundamental   charge     # Coulomb
c = 299792458 # Light speed                   # m s⁻¹
pi = 3.14159265358979323846264338328
e = 2.7182818284590452353602874713527
nan = float("NaN")

# SHELL
def sh(cmd, prnt = True): # Shell command execution
  exitCode = sp.call(cmd, shell = True)
  if exitCode !=0:
    if prnt:
      print('[WRN%d] %s' % (exitCode, cmd))
    return exitCode
  else:
    if prnt:
      print('[INFO]',cmd)
    return exitCode

"""
Downloads file from internet to director with url endpoint
name by default (like !wget). Can specify optional keyword arguments:

	`filename`: Filename to be saved as. String.
	`dir`: Directory to save to. Can be absolute or relative
	`prnt`: Print file contents. Default False.
"""
def wget(url, **args):
    filename = args["name"] if "name" in args else url[url.rfind('/') + 1::]
    dir = args["dir"] + "/" if "dir" in args else ""
    Path(dir).mkdir(parents=True, exist_ok=True)
    showContents = args["prnt"] if "prnt" in args else False
    try:
      r = requests.get(url, allow_redirects=True)
    except:
      raise ValueError('Error retrieving ' + url)
    with open(dir+filename, 'wb') as f:
        f.write(r.content)
    if showContents:
    	print(r.content)

# INIT 6S
def build6S():
    sh('make -C ./build/6SV1.1')

def init6SWindows():
  try:
    ec = sh('make -h', prnt=False)
    if ec != 0: # We have a compiler
      print('Fortran compiler not found! Downloading compiler to /source. Please install before continuing!')
      wget('http://www.cse.yorku.ca/~roumani/fortran/gnu99/Fort99.zip',dir="source")
      raise SystemExit(0)
    ec = sh('\\build\\6SV1.1\\sixsV1.1 < build\\Examples\\Example_In_1.txt',prnt=False)
    if ec != 0: # If binary exists don't init
        print('Binary not found. Downloading 6S')
        raise Exception('')

  except:
    sh('pip install Py6S')
    sh('mkdir build\\6SV1.1')
    wget("http://rtwilson.com/downloads/6SV-1.1.tar", dir="source")
    sh('tar -xvf source\\6SV-1.1.tar -C build')
    filein = open( 'source\\Makefile_edited.txt' )
    filereplace = open('build/6SV1.1/Makefile','w')
    filereplace.write(filein.read())
    filereplace.close()
    build6S()
    ec = sh('build\\6SV1.1\\sixsV1.1 < build\\Examples\\Example_In_1.txt') # Test binary
    if ec!=0:
        raise ValueError("6S binary test failed")


def init6SLinux():
  try:
    ec = sh('./build/6SV1.1/sixsV1.1 < ./build/Examples/Example_In_1.txt',prnt=False)
    if ec != 0: # If binary exists don't init
      print('Binary not found. Downloading 6S')
      raise Exception('')
    print('Binary exists! Not downloading 6S!')
  except:
    sh('pip install Py6S')
    wget("http://rtwilson.com/downloads/6SV-1.1.tar", dir="source")
    sh('mkdir -p ./build/6SV/1.1')
    sh('tar -xvf ./source/6SV-1.1.tar -C ./build')
    # Edit makefile for compiler
    sh("sed -i 's/FC      = g77 $(FFLAGS)/FC      = gfortran -std=legacy -ffixed-line-length-none -ffpe-summary=none $(FFLAGS)/g' ./build/6SV1.1/Makefile")
    build6S()
    sh('./build/6SV1.1/sixsV1.1 < ./build/Examples/Example_In_1.txt') # Test binary
    sh('ln ./build/6SV1.1/sixsV1.1 /usr/local/bin/sixs') # Add 6S to $PATH environment variable

# Regular functions

def irradianceToPower(IR, altitudeSatellite , areaObsTierra , areaLente ): #iradiance from earth to power upstream the satellite lens
  #RT = 6371e3 # earth radius in meters [m]
  h_space = 100e3 # Altitude of space in meters (as 6S sets it)
  #	factor = areaObsTierra * areaLente * (RT + altitudeSatellite)**-2 #OLD
  factor = areaObsTierra * areaLente * (altitudeSatellite)**-2
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

def wavenumberToWavelength(wavenumber):
  wl = []
  for i in range(len(wavenumber)):
    nu = float(wavenumber[i])
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
  if N != len(yv):
      raise ValueError("Length of x and y lists should be equal!")
  for i in range(1,N):
    dx = abs(xv[i] - xv[i-1])
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
  X = [];  Y = []
  for i in range(N):
    x, y = x1[i], y1[i]
    for j in range(1,len(x2)):
      if x == x2[j-1]:
        X.append(x)
        Y.append( float(y * y2[j-1]))
        break
      if x == x2[j]:
        X.append(x)
        Y.append( float(y * y2[j]))
        break
      if x <= x2[j] and x >= x2[j-1]:
        yint = interpolate(x, x2[j-1:j+1],y2[j-1:j+1]) if interp else y2[j]
        X.append(x)
        Y.append( float(y * yint))
        break
  return X, Y

def ceil(x):
    return int(x//1 + 1) if x != x//1 else int(x//1)
def floor(x):
    return int(x//1)
def sin(x):
  return ((e**(1j*x) - e**(-1j*x))/2j).real
def cos(x):
  return ((e**(1j*x) + e**(-1j*x))/2).real
def sqrt(x):
  return x**0.5
def exp(x):
  return e**x
def gaussN(x,mu,sd):
  return 1/sd/sqrt(2*pi) * exp(-.5*((x-mu)/sd)**2 )

#EXTRA/unused
def irradianceToIntensity(IR, altitudeSatellite,areaObsTierra):
  pi = 3.14159265359
  #RT = 6371e3 # earth radius in meters [m] #We no longer need it
  h_space = 100e3 # Altitude of space in meters (as 6S sets it)
  #  	factor = 4*pi*RT**2 * (RT + altitudeSatellite)**-2 # OLD
  # 	factor = areaObsTierra  * (RT + altitudeSatellite)**-2 #OLD
  factor = areaObsTierra * (altitudeSatellite)**-2
  I = []
  for i in range(len(IR)):
    I.append( factor * IR[i] )
  return I # Returns W/m^2/micrometer


"""
	Get multiple files
"""
def wgetData(urls,host):
    if not isinstance(urls, list):
        raise ValueError("urls must be in a list!")
    for url in urls:
        folder = url[len(host):url.rfind('/')+1]
        print(url,folder)
        wget(url, dir = folder)

"""
   replaces NaN values with values closest to the right in a list. Returns reconstructed list
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

"""
   Interpolates gaps in curves where nan values present. returns reconstructed y list.
"""
def interpolateNans(xlst, ylst):
  N = len(ylst)
  for i in range(N):
    if ylst[i] != ylst[i]:
      if i == N-1:
        ylst[i] = ylst[i-1]
      if i==0:
        raise ValueError('First value is nan! Cannot interpolate!')
      for j in range(i,N):
        if ylst[j] == ylst[j]:
          ylst[i] = interpolate(xlst[i], [xlst[i-1], xlst[j]], [ylst[i-1], ylst[j]])
          break
  return ylst

"""
  Saves x and y values to a simple csv file with 'x' and 'y' headers by default.
  change header key to a 2 value list with desired header
"""
def xyToCSV(xlst, ylst, filename, header=['x','y']):
    if len(xlst) != len(ylst):
        raise ValueError("Length of x and y lists should be equal!")
    pd.DataFrame({header[0]:xlst, header[1]:ylst}).to_csv(filename, index=False)

"""
    Saves dict as .csv file. By default `filename`= 'dict.csv'
"""
def dictToCSV(dict, filename='dict.csv'):
    pd.DataFrame(dict).to_csv(filename, index=False)

"""
    Samples x and y lists at quasi-evenly spaced discrete points.
    Parameter `samples` describes the sampling points. Useful before spectra plotting

"""
def sampleXY(X,Y, samples=50):
    N=len(X)
    if N != len(Y):
        raise ValueError("Length of lists should be equal!")
    if N < samples:
        raise ValueError("Length of list should be greater than number of samples!")
    k = (N-1)/(samples-1)
    Xs = [X[floor(i*k)] for i in range(samples)]
    Ys = [Y[floor(i*k)] for i in range(samples)]
    return Xs,Ys

"""
  Une los datos de multiples archivos spectraplot sobre las longitudes de onda que abarcan
"""
def joinSpectraPlots(simNames, filename='joinedSpectra.csv'):
  nuSet = set(); nuList = []; abList = []
  for i in range(len(simNames)):
    path = simNames[i]
    folder = path[:path.rfind('/')+1]
    fname = simNames[i][len(folder):]
    simColName = fname[:fname.find('cm')+2].replace(',','/')
    data = pd.read_csv(simNames[i])
    nu  = data["nu"]
    ab  = data[simColName]
    for j in range(len(nu)):
      if nu[j] not in nuSet:
        nuSet.add(nu[j])
        nuList.append(nu[j])
        abList.append(ab[j])
  pd.DataFrame({'nu': nuList,simColName: abList}).sort_values('nu').to_csv(filename,index=False)

"""
Class sixs for spacemeters lets user change 6S's hardcoded concentration and
recompile the binary to apply changes using the concentration object. Must use
set6S method to set concentration. ABSTRA_template.txt must be in source/ folder
and the 6S source code must be located under build/6SV1.1/ 

User can also create a usual 6S instance easily for testing purposes
with quickSixS
"""
class sixs:
  """
      Crea el objeto SixS con opciones/parametros genericos para ahorrar espacio de codigo
  """
  def quickSixS(dir="./build/6SV1.1/sixsV1.1"):
      s = SixS(path=dir)
      s.aero_profile = AeroProfile.PredefinedType(AeroProfile.Urban)
      s.atmos_profile = AtmosProfile.PredefinedType(AtmosProfile.Tropical)
      s.geometry.from_time_and_location(-25.31, 33.23, "11:41", 14.9, 171.3)
      s.altitudes.set_sensor_satellite_level()
      s.ground_reflectance = GroundReflectance.HomogeneousLambertian(GroundReflectance.GreenVegetation)
      return s

  class concentration:
      def __init__(self, **args):
          self.ch4ppm = args["ch4ppm"] if "ch4ppm" in args else 1.72
          self.n2oppm = args["n2oppm"] if "n2oppm" in args else 310e-3
          self.co2ppm = args["co2ppm"] if "co2ppm" in args else 330
          self.coppm = args["coppm"] if "coppm" in args else 1e-3
          self.o2cent = args["o2cent"] if "o2cent" in args else 20.947
      def print(self):
          for attr, value in self.__dict__.items():
              print(attr,': ',value, sep='')
      def set6S(self,prnt=False):
          filein = open( 'source/ABSTRA_template.txt' )
          src = Template( filein.read() )
          d = { 'ch4ppm':self.ch4ppm,'coppm':self.coppm,'co2ppm':self.co2ppm,'n2oppm':self.n2oppm,'o2cent':self.o2cent }
          result = src.substitute(d)
          fid = open('build/6SV1.1/ABSTRA.f','w')
          fid.write(result)
          build6S()
          if prnt:
              print('Following concentrations have been set:')
              self.print()
