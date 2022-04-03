import sys
import schemdraw
import schemdraw.elements as elm
#import ahkab
#from ahkab import circuit, printing, time_functions
import matplotlib.pylab as plt
import numpy as np
import yaml


def yaml_load(filepath):
    #Loads a YAML file
    with open(filepath, "r") as Circuit:
        code = yaml.safe_load(Circuit)
    return code
yaml.dump(yaml_load('Circuit.yaml'), sys.stdout)



# class CircuitSim:
#     def calc(self, data):
#         file = open('test.py', 'a')
#         file.write(data)
#
#
# test = CircuitSim()



# x = sys.argv[1]
# z = calculatorObj.calc(x)
# print(z)

