import matplotlib.pylab as plt
import numpy as np


# ---------------------------OBJECT CLASS COMPONENT---------------------------
class Component:
    legCount = 0  # static variable to count the amount of legs in the circuit, used by legToN()

    def __init__(self, comType, startLeg, endLeg, comName):
        self.comType = comType
        self.startLeg = startLeg
        self.endLeg = endLeg
        self.comName = comName
        self.comValue = self.getValue()
        self.direction = self.getDirection()

    # determines what is the direction of the component
    def getDirection(self):
        if self.startLeg == 'PWR':
            return 'down'
        elif self.startLeg == 'GND':
            return 'up'
        elif self.startLeg['y'] == self.endLeg['y']:
            return 'right'
        else:
            return 'down'

    # determines the value if a component based on its type
    def getValue(self):
        if self.comType == 'Resistor':
            return 500
        elif self.comType == 'Inductor':
            return 0.5
        elif self.comType == 'Capacitor':
            return 0.5

    # debug functions
    # prints general information about the current object
    def printComp(self):
        print(f'{self.comName} is a {self.comType} and is connected at {self.startLeg} and {self.endLeg}')
        print(f'the components direction is {self.direction}')


# ---------------------------END OF THE COMPONENT CLASS---------------------------
import sys
import yaml


def yaml_load(filepath):
    # Loads a YAML file
    with open(filepath, "r") as circuitFile:
        code = yaml.safe_load(circuitFile)
    return code


# load the yaml file into a dictionary
def yamlToDic():
    circuitDic = yaml_load('Circuit.yaml')
    return {dicToComp(component).comName: dicToComp(component) for component in circuitDic['Circuit']}


# disassembles the dictionary into is parts and refactors into object
def dicToComp(comp):
    if isinstance(comp['leg1'], str):
        startLeg = comp['leg1']
        endLeg = comp['leg2']
    elif isinstance(comp['leg2'], str):
        startLeg = comp['leg2']
        endLeg = comp['leg1']
    elif comp['leg1']['x'] < comp['leg2']['x']:
        startLeg = comp['leg1']
        endLeg = comp['leg2']
    else:
        startLeg = comp['leg2']
        endLeg = comp['leg1']
    return Component(comp['type'], startLeg, endLeg, comp['name'])


# prints the given matrix
def printMat(matrix):
    for line in matrix:
        print (line)


# ---------------------------SCHAMDRAW---------------------------
import schemdraw
import schemdraw.elements as elm

4


# inserts component to breadboard in the correct orientation
def insertComp(comp, board):
    if type(comp.startLeg) == str:
        pass
    else:
        if comp.startLeg['x'] == comp.endLeg['x']:
            # if both legs have the same x, it is a shot circuit
            sys.stdout.write('short circuit, components must be connected vertically, please try again\n')
        else:
            y = comp.startLeg['y']
            xMax = comp.endLeg['x']
            xMin = comp.startLeg['x']
            for x in range(xMin, xMax + 1):  # moves along the y-axis (horizontally)
                if board[y][x] != 'N':
                    sys.stdout.write('cannot connect two components in the same hole, please try again\n')
                else:
                    board[y][x] = '-'
            board[y][xMin] = comp.comName  # placement of start leg
            board[y][xMax] = 'E'  # placement of end leg


# generates breadboard
def generateBoard(compDic):
    breadboard = []
    for y in range(5):
        breadboard.append([])
        for x in range(63):
            breadboard[y].append('N')
    compList = list(compDic.values())
    for comp in compList:
        insertComp(comp, breadboard)

    # debug ->
    printMat(breadboard)    # prints the breadboard for debugging purposes
    return breadboard


# parses a component into schemdraw code
def compToDrawing(comp, prev):
    if prev.endLeg['y'] > comp.startLeg['y'] and comp.direction == 'down':
        comp.direction = 'up'
    return eval(f'elm.{comp.comType}().{comp.direction}().label(comp.comName)')


# draws a circuit from a dictionary of component objects and a metrix
def createDrawingList(dic, board):
    d = [schemdraw.Drawing()]
    tmp = {'type': 'Line', 'name': 'R', 'leg1': {'place': 'bot', 'x': 0, 'y': 0},
           'leg2': {'place': 'bot', 'x': 0, 'y': 0}}
    prev = dicToComp(tmp)
    for x in range(63):
        compInX = [board[_][x] for _ in range(5) if
                   board[_][x] != 'N' and board[_][x] != '-']  # list of all components with in this x
        count = len(compInX)  # counts how many components in the same x
        for comp in compInX:
            if comp != 'E':
                if count > 2:
                    d[-1].pop()
                    d.append(schemdraw.Drawing())
                    if dic[comp].direction == 'right':
                        d[-1].push()
                    d[-1] += compToDrawing(dic[comp], prev)
                else:
                    d[-1] += compToDrawing(dic[comp], prev)
                    prev = dic[comp]
                    if dic[comp].direction == 'right':
                        d[-1].push()
    return d


# draws a circuit from a list of schemdraw drawings
def drawCircuit(compDic):
    d = createDrawingList(compDic, generateBoard(compDic))
    dTotal = schemdraw.Drawing()
    for _ in d:
        dTotal += elm.ElementDrawing(_)
    dTotal.draw()


# ---------------------------END OF SCHAMDRAW---------------------------

# ---------------------------AHKAB---------------------------
import ahkab
from ahkab import circuit, printing, time_functions


def legToN(leg):
    if leg == 'GND':
        return leg
    Component.legCount += 1
    return f"n{leg['x']}"


# parses a component into ahkab code
def compToAhkab(comp, mycircuit):
    type = comp.comType.lower()
    if type != 'Line':
        eval(
            f'mycircuit.add_{type}("{comp.comName}", n1="{legToN(comp.startLeg)}", n2="{legToN(comp.endLeg)}", value={comp.comValue})')


def startAhkab(compList):
    mycircuit = circuit.Circuit(title="EXAMPLE CIRCUIT")
    for comp in compList:
        compToAhkab(comp, mycircuit)
    print(mycircuit)


# ---------------------------END OF AHKAB---------------------------
# TODO: pyserial for communication with Arduino UNO

# begins the process
def startCircuit():
    # yaml ->
    compDic = yamlToDic()
    # schamdraw ->
    drawCircuit(compDic)
    # ahkab ->
    startAhkab(list(compDic.values()))


startCircuit()
