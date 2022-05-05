import ahkab
from ahkab import circuit, printing, time_functions
mycircuit = circuit.Circuit(title="Example circuit")

gnd = mycircuit.get_ground_node()

mycircuit.add_resistor("R1", n1="n1", n2="n2", value=600)
mycircuit.add_inductor("L1", n1="n2", n2="n3", value=15.24e-3)
mycircuit.add_capacitor("C1", n1="n3", n2=gnd, value=119.37e-9)
mycircuit.add_inductor("L2", n1="n3", n2="n4", value=61.86e-3)
mycircuit.add_capacitor("C2", n1="n4", n2=gnd, value=155.12e-9)
mycircuit.add_resistor("R2", n1="n4", n2=gnd, value=1.2e3)

voltage_step = time_functions.pulse(v1=0, v2=1, td=500e-9, tr=1e-12, pw=1, tf=1e-12, per=2)
mycircuit.add_vsource("V1", n1="n1", n2=gnd, dc_value=5, ac_value=1, function=voltage_step)

print(mycircuit)

op_analysis = ahkab.new_op()
ac_analysis = ahkab.new_ac(start=1e3, stop=1e5, points=100)
tran_analysis = ahkab.new_tran(tstart=0, tstop=1.2e-3, tstep=1e-6, x0=None)

r = ahkab.run(mycircuit, an_list=[op_analysis, ac_analysis, tran_analysis])

import matplotlib.pylab as plt
import numpy as np

fig = plt.figure()
plt.title(mycircuit.title + " - TRAN Simulation")
plt.plot(r['tran']['T'], r['tran']['VN1'], label="Input voltage")
#plt.hold(True)
plt.plot(r['tran']['T'], r['tran']['VN4'], label="output voltage")
plt.legend()
#plt.hold(False)
plt.grid(True)
plt.ylim([0,1.2])
plt.ylabel('Step response')
plt.xlabel('Time [s]')
plt.show()

import schemdraw
import schemdraw.elements as elm

# count = 1
d1 = schemdraw.Drawing()
d1 += elm.Resistor().right().label('R1')
d1.push()

# count = 3
d2 = schemdraw.Drawing()
d2.push()
d2 += elm.Resistor().right().label('R2')
d1.pop()


d3 = schemdraw.Drawing()
d3.push()
d3 += elm.Resistor().down().label('R3')
d3 += elm.Resistor().right().label('R4')
d3 += elm.Resistor().up().label('R5')
d2.pop()

d4 = schemdraw.Drawing()
d4 += elm.Resistor().right().label('R6')

d5 = schemdraw.Drawing()
d5 += elm.ElementDrawing(d1)
d5 += elm.ElementDrawing(d2)
d5 += elm.ElementDrawing(d3)
d5 += elm.ElementDrawing(d4)
d5.draw()
