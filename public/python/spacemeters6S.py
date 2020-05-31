from Py6S import *
from spacemeters import *

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
