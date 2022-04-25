import sys
import yaml
import schemdraw
import schemdraw.elements as elm


# object class component
class Component:
    count = 0

    def __init__(self, comType, comLeg1, comLeg2, comName):
        self.comType = comType
        self.comLeg1 = comLeg1
        self.comLeg2 = comLeg2
        self.comName = comName
        self.direction = self.compDir()
        # TODO: DELETE COMPONENT.COUNT
        Component.count = Component.count + 1

    # determines what is the direction of the component
    def compDir(self):
        if self.comLeg1['y'] == self.comLeg2['y']:
            return 'right'
        else:
            return 'down'

    # prints general information about the current object
    # debug function
    def printComp(self):
        print(f'{self.comName} is a {self.comType} and is connected at {self.comLeg1} and {self.comLeg2}')
        print(f'the components direction is {self.direction}')


# ---------------------------END OF THE COMPONENT CLASS---------------------------


def yaml_load(filepath):
    # Loads a YAML file
    with open(filepath, "r") as circuitFile:
        code = yaml.safe_load(circuitFile)
    return code


# disassembles the dictionary into is parts and refactors into object
def dicToComp(comp):
    return Component(comp['type'], comp['leg1'], comp['leg2'], comp['name'])


# needs some work...
# inserts component to breadboard in the correct orientation
def insertComp(comp):
    if comp.comLeg1['x'] == comp.comLeg2['x']:  # if both legs have the same x, it is a shot circuit
        sys.stdout.write('short circuit, components must be connected vertically, please try again\n')
    else:
        y = comp.comLeg1['y']
        xMax = max(comp.comLeg1['x'], comp.comLeg2['x'])
        xMin = (comp.comLeg1['x'] + comp.comLeg2['x']) - xMax
        for x in range(xMin, xMax + 1):  # moves along the y-axis (horizontally)
            if breadboard[y][x] != 'N':
                sys.stdout.write('cannot connect two components in the same hole, please try again\n')
            else:
                breadboard[y][x] = '-'
        breadboard[y][xMin] = comp.comName  # beginning of the component
        breadboard[y][xMax] = 'E'  # end of component


def dicToDrawing(comp):
    return eval(f'elm.{comp.comType}().{comp.direction}().label(comp.comName)')


def drawCircuit(dic, board):
    d = [schemdraw.Drawing()]
    for x in range(63):
        count = 0
        for y in range(5):
            if board[y][x] != 'N' and board[y][x] != '-':
                if board[y][x] != 'E':
                    d[-1] += dicToDrawing(dic[board[y][x]])
                count += 1  # counts how many components in the same x
        if count > 2:  # if there are more than 2 components with the same x than they are part of a junction
            d[-1].push()
            d.append(schemdraw.Drawing())
    dTotal = schemdraw.Drawing()
    for _ in d:
        dTotal += elm.ElementDrawing(_)
        dTotal.draw()


# load the yaml file into a dictionary
circuitDic = yaml_load('Circuit.yaml')
compDic = {dicToComp(component).comName: dicToComp(component) for component in circuitDic['Circuit']}

# generates breadboard
# creates list of lists 5*63 represents top breadboard
breadboard = []
for y in range(5):
    breadboard.append([])
    for x in range(63):
        breadboard[y].append('N')

# testing!!!!
# print(circuitDic['Circuit'])
compList = [dicToComp(component) for component in circuitDic['Circuit']]
# print(compDic)
for comp in compList:
    insertComp(comp)
drawCircuit(compDic, breadboard)
for line in breadboard:
    print(line)
# print([_.printComp() for _ in compList])
# yaml.dump(circuitDic, sys.stdout) <------- important
