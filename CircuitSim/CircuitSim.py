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


# prints the given matrix debug function
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
    # debug ->
    printMat(breadboard)
    return breadboard


# parses a component into schemdraw code
def compToDrawing(comp, prev):
    # if prev.endLeg['y'] > comp.startLeg['y']:
    #     comp.direction = 'up'
    comp.setDirection(prev)
    return eval(f'elm.{comp.comType}().{comp.direction}().label(comp.comName)')


# reorders the list so the components that go down are drawn first
def downFirst(nameList, compDic):
    endList = []
    downList = []
    rightList = []
    for name in nameList:
        if name != 'E':
            if compDic[name].direction == 'vertical':
                downList.append(name)
            else:
                rightList.append(name)
        else:
            endList.append(name)
    return endList + downList + rightList


# def findBranch(compDic, compName, board):
#     compList = list(compDic.keys())


# draws a circuit from a dictionary of component objects and a metrix
def createDrawingList(compDic, compList, board, d):

    tmp = {'type': 'Line', 'name': 'R', 'leg1': {'place': 'bot', 'x': 0, 'y': 0},
           'leg2': {'place': 'bot', 'x': 0, 'y': 0}}
    prev = dicToComp(tmp)

    for x in range(63):  # moves along the x-axis
        # list of all components within this x -->
        tmp = [board[_][x] for _ in range(10) if board[_][x] != 'N' and board[_][x] != '-']
        compInX = downFirst(tmp, compDic)
        for comp in compInX:
            if comp != 'E':
                if len(compInX) > 2:  # if there are 3 component or more, they are part of a junction
                    d.append(schemdraw.Drawing())
                    # d [-1] += drawBranch(x, board, compDic)
                    d[-1].push()  # saves the current state
                    d[-1] += compToDrawing(compDic[comp], prev)
                    if compInX[-1] != comp:
                        d[-1].pop()  # returns to the last pushed state
                else:
                    d[-1] += compToDrawing(compDic[comp], prev)
                    prev = compDic[comp]
                    d[-1].push()

                # debug ->
                # tmpDebug(d)


# draws a circuit from a list of schemdraw drawings
def drawCircuit(compDic):
    d = [schemdraw.Drawing()]
    createDrawingList(compDic, list(compDic.keys()), generateBoard(compDic), d)
    dTotal = schemdraw.Drawing()
    for _ in d:
        dTotal += elm.ElementDrawing(_)
    dTotal.draw()


def tmpDebug(d):
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
    return f"N{leg['x']}"


# parses a component into ahkab code
def compToAhkab(comp, myCircuit, GND):
    comType = comp.comType.lower()
    n1 = legToN(comp.startLeg)
    n2 = legToN(comp.endLeg)

    # to add a diode to a circuit ->
    # myCircuit.add_model('diode', 'Diode', dict(IS=1e-14, N=1, ISR=0, NR=2, RS=0))
    # f'myCircuit.add_diode("D{comp.comName}", n1="{n1}", n2="{n2}", model_label="Diode")'

    # if leg is a GND then it is not a string
    strN = 'n1='
    if n1 == 'GND':
        strN += f'{n1}, n2="{n2}"'
    elif n2 == 'GND':
        strN += f'"{n1}", n2={n2}'
    else:
        strN += f'"{n1}", n2="{n2}"'

    if comType == 'line':
        # if the component is a wire, it is implemented as a resistor with extremely low resistance
        tmp = f'myCircuit.add_resistor("Wire", {strN}, value=1e-9)'
        eval(tmp)
    else:
        tmp = f'myCircuit.add_{comType}("{comp.comName}", {strN}, value={comp.comValue})'
        eval(tmp)


# start the circuit simulation
def startAhkab(compList):
    # builds the circuit
    myCircuit = circuit.Circuit(title="My Circuit")
    GND = myCircuit.get_ground_node()
    PWR = time_functions.pulse(v1=0, v2=5, td=500e-9, tr=1e-11, pw=1, tf=1e-11, per=2)
    myCircuit.add_vsource("V1", n1='PWR', n2=GND, dc_value=5, ac_value=1, function=PWR)

    # adding components to the circuit
    NVout = 'NV0'
    for comp in compList:
        tmp = f'V{legToN(comp.startLeg)}'
        if tmp[2::].isdigit() and int(tmp[2::]) > int(NVout[2::]):
            NVout = tmp
        compToAhkab(comp, myCircuit, GND)
    # debug -->
    # print(myCircuit)
    return NVout, myCircuit


# ---------------------------END OF AHKAB---------------------------

# ---------------------------MATPLOTLIB---------------------------
# TODO: needs some work
import matplotlib.pylab as plt
import numpy as np


# draw a graph for myCircuit
def drawGraph(NVout, myCircuit):
    # ahkab stuff -->
    # op_analysis = ahkab.new_op()
    # ac_analysis = ahkab.new_ac(start=1e3, stop=1e5, points=100)
    tran_analysis = ahkab.new_tran(tstart=0, tstop=1.2e-3, tstep=1e-6, x0=None)
    r = ahkab.run(myCircuit, an_list=[tran_analysis])

    fig = plt.figure()
    plt.title(myCircuit.title + " - TRAN Simulation")
    plt.plot(r['tran']['T'], r['tran']['VPWR'], label="Input voltage")
    plt.plot(r['tran']['T'], r['tran'][NVout], label="output voltage")
    plt.legend()
    plt.grid(True)
    plt.ylim([0, 6])
    plt.ylabel('Amplitude [V]')
    plt.xlabel('Time [s]')
    fig.savefig("C:/Users/USER/Desktop/hermelin/Project/UNITY/VRlab/VRlab/Assets/image results/tran_plot.png")
    plt.show()
    Vout = r['tran'][NVout][-1]
    return Vout


# ---------------------------END OF MATPLOTLIB---------------------------


def startCircuit():
    # yaml ->
    compDic = yamlToDic()
    # ahkab ->
    NVout, myCircuit = startAhkab(list(compDic.values()))
    # schamdraw ->
    drawCircuit(compDic)
    # matplotlib ->
    Vout = str(drawGraph(NVout, myCircuit))[0:5]
    # the string displayed on the screen ->
    return f'V={Vout}V'


def result():
    return startCircuit()
