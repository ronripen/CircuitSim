import sys

import yaml


def yaml_load(filepath):
    # Loads a YAML file
    with open(filepath, "r") as circuitFile:
        code = yaml.safe_load(circuitFile)
    return code


Circuit = yaml_load('Circuit.yaml')
yaml.dump(Circuit, sys.stdout)

import schemdraw
import schemdraw.elements as elm


def orientation(comLeg1, comLeg2):
    if comLeg1['x'] == comLeg2['x']:
        if comLeg1['y'] > comLeg2['y']:
            return 'up()'
        else:
            return 'down()'
    else:
        if comLeg1['x'] < comLeg2['x']:
            return 'right()'
        else:
            return 'left()'




def drawCircuit():
    lst = []
    for component in Circuit['Circuit']:
        d = ""
        comType = component['component']['type']
        comLeg1 = component['component']['leg1']
        comLeg2 = component['component']['leg2']
        comName = component['component']['name']
        print(f'{comName} is a {comType} and is connected at {comLeg1} and {comLeg2}')
        d = f'elm.{comType}().{orientation(comLeg1, comLeg2)}.label(\'{comName}\')'
        lst.append(d)
    return lst


lst = drawCircuit()
d1 = schemdraw.Drawing()
d1.push()
for i in lst:
    d1 += eval(i)
d1.pop()
d2 = schemdraw.Drawing()
d2 += elm.ElementDrawing(d1)
d2.draw()
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
