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
        self.direction = self.getOrientation()
        self.first = True

    # determines what is the direction of the component
    def setDirection(self, prev):
        if self.direction == 'horizontal':
            if prev.endLeg['x'] < self.endLeg['x']:
                self.direction = 'right'
            else:
                self.direction = 'left'
        else:
            if prev.endLeg['y'] < self.startLeg['y']:
                self.direction = 'down'
            else:
                self.direction = 'up'

    # determines what is the orientation of the component
    def getOrientation(self):
        if self.startLeg == 'PWR':
            return 'down'
        elif self.startLeg == 'GND':
            return 'up'
        elif self.startLeg['y'] == self.endLeg['y']:
            return 'horizontal'
        return 'vertical'

    # determines the value if a component based on its type
    def getValue(self):
        if self.comType == 'Resistor':
            return 700
        elif self.comType == 'Inductor':
            return 0.05
        elif self.comType == 'Capacitor':
            return 1.5e-7

    # debug functions
    # prints general information about the current object
    def printComp(self):
        print(f'{self.comName} is a {self.comType} and is connected at {self.startLeg} and {self.endLeg}')
        print(f'the components direction is {self.direction}')


# ---------------------------END OF THE COMPONENT CLASS---------------------------
import sys
import yaml


# loads a YAML file
def yaml_load(filepath):
    with open(filepath, "r") as circuitFile:
        code = yaml.safe_load(circuitFile)
    return code


# load the yaml file into a dictionary
def yamlToDic():
    circuitDic = yaml_load('C:/Users/USER/Desktop/hermelin/Project/PYTHON/CircuitSim/CircuitSim/Circuit.yaml')
    return {dicToComp(component).comName: dicToComp(component) for component in circuitDic['Circuit']}


# disassembles the dictionary into is parts and refactors into object
def dicToComp(comp):
    # if leg is PWR or GND
    if isinstance(comp['leg1'], str):
        startLeg = comp['leg1']
        endLeg = comp['leg2']
    elif isinstance(comp['leg2'], str):
        startLeg = comp['leg2']
        endLeg = comp['leg1']

    # if regular leg
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
        print(line)


# ---------------------------SCHAMDRAW---------------------------
import schemdraw
import schemdraw.elements as elm


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
    for y in range(10):
        breadboard.append([])
        for x in range(63):
            breadboard[y].append('N')
    for comp in list(compDic.values()):
        insertComp(comp, breadboard)
    # printMat(breadboard)  # prints the breadboard for debugging purposes
    return breadboard


# parses a component into schemdraw code
def compToDrawing(comp, prev):
    # if prev.endLeg['y'] > comp.startLeg['y']:
    #     comp.direction = 'up'
    comp.setDirection(prev)
    return eval(f'elm.{comp.comType}().{comp.direction}().label(comp.comName)')


# draws a circuit from a dictionary of component objects and a metrix
def createDrawingList(compDic, board):
    d = [schemdraw.Drawing()]
    tmp = {'type': 'Line', 'name': 'R', 'leg1': {'place': 'bot', 'x': 0, 'y': 0},
           'leg2': {'place': 'bot', 'x': 0, 'y': 0}}
    prev = dicToComp(tmp)
    for x in range(63):  # moves along the x-axis
        # list of all components within this x -->
        compInX = [board[_][x] for _ in range(10) if board[_][x] != 'N' and board[_][x] != '-']
        for comp in compInX:
            if comp != 'E':
                if len(compInX) > 2:  # if there are 3 component or more, they are part of a junction
                    d.append(schemdraw.Drawing())
                    d[-1].push()  # saves the current state
                    d[-1] += compToDrawing(compDic[comp], prev)
                    d[-2].pop()  # returns to the last pushed state
                else:
                    d[-1] += compToDrawing(compDic[comp], prev)
                    prev = compDic[comp]
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


# returns a representation of the leg placement on the board
def legToN(leg):
    if leg == 'GND' or leg == 'PWR':
        return leg
    Component.legCount += 1
    return f"n{leg['x']}"


# parses a component into ahkab code
def compToAhkab(comp, myCircuit, GND):
    comType = comp.comType.lower()
    n1 = legToN(comp.startLeg)
    n2 = legToN(comp.endLeg)

    if comp.first:
        comp.first = False
        Vin = f'V{n1}'
    Vout = f'V{n1}'

    if comType == 'line':
        eval(f'myCircuit.add_resistor("wire", n1="{n1}", n2="{n2}", value=1e-9)')
    else:
        eval(f'myCircuit.add_{comType}("{comp.comName}", n1="{n1}", n2="{n2}", value={comp.comValue})')
    return Vin, Vout


# start the circuit simulation
def startAhkab(compList):
    # builds the circuit
    myCircuit = circuit.Circuit(title="Example Circuit")
    GND = myCircuit.get_ground_node()
    PWR = time_functions.pulse(v1=0, v2=1, td=500e-9, tr=1e-12, pw=1, tf=1e-12, per=2)
    myCircuit.add_vsource("V1", n1=legToN(compList[0].startLeg), n2=GND, dc_value=5, ac_value=1, function=PWR)
    print(myCircuit)

    # adding components to the circuit
    for comp in compList:
        Vin, Vout = compToAhkab(comp, myCircuit, GND)
    # debug -->
    print(myCircuit)
    return Vin, Vout, myCircuit


# ---------------------------END OF AHKAB---------------------------

# ---------------------------MATPLOTLIB---------------------------
import matplotlib.pylab as plt
import numpy as np


# draw a graph for myCircuit
def drawGraph(Vin, Vout, myCircuit):
    # ahkab stuff -->
    # op_analysis = ahkab.new_op()
    # ac_analysis = ahkab.new_ac(start=1e3, stop=1e5, points=100)
    tran_analysis = ahkab.new_tran(tstart=0, tstop=5, tstep=1e-2, x0=None)
    r = ahkab.run(myCircuit, an_list=[tran_analysis])

    fig = plt.figure()
    plt.title(f'{myCircuit.title} Simulation')
    plt.plot()
    plt.plot(r['tran']['T'], r['tran'][Vin], label="Input voltage")
    plt.plot(r['tran']['T'], r['tran'][Vout], label="output voltage")
    plt.legend()
    plt.grid(True)
    plt.ylim([-5, 5])
    plt.xlim([0, 5])
    plt.ylabel('Step response')
    plt.xlabel('Time [s]')
    plt.show()


# ---------------------------END OF MATPLOTLIB---------------------------

# # ---------------------------PYSERIAL---------------------------
# import serial
# import time
# # arduino = serial.Serial(port='COM5', baudrate=9600, timeout=.1)
#
#
# # sends serial output to Arduino
# def serialWrite(x):
#     arduino.write(bytes(x, 'utf-8'))
#     time.sleep(0.1)
#
#
# # starts the communication process to the Arduino
# def startSerialCom(Vout):
#     arduino.cancel_write()
#
#
# # ---------------------------END OF PYSERIAL---------------------------


def startCircuit():
    # yaml ->
    compDic = yamlToDic()
    # schamdraw ->
    drawCircuit(compDic)
    # ahkab ->
    Vin, Vout, myCircuit = startAhkab(list(compDic.values()))
    # matplotlib ->
    drawGraph(Vin, Vout, myCircuit)
    # pyserial ->
    # startSerialCom('ABCDEFG')
    Vout = 3.456
    return f'V={Vout}V'

def result():
    return startCircuit()

