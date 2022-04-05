import schemdraw
import schemdraw.elements as elm

# push for every Vsource, from negative side of next Vsource
d1 = schemdraw.Drawing()
d1.push()
# d1 += elm.Line().left()
d1 += elm.Resistor().up().label('R1')
d1 += elm.SourceV().up().label('E1')
d1 += elm.Line().right()
d1.pop()

d2 = schemdraw.Drawing()
d2 += elm.Line().right()
d2.push()
d2 += elm.Resistor().up().label('R2')
d2 += elm.SourceV().up().label('E2')
d2 += elm.Line().right()
d2.pop()

d3 = schemdraw.Drawing()
d3 += elm.Resistor().right().label('R5')
d3 += elm.Resistor().up().label('R3')
d3 += elm.SourceV().up().label('E3')
d3.push()
d3 += elm.Line().right()
d3 += elm.Resistor().down().label('R4')
d3 += elm.Line().down()
d3 += elm.Line().left()
d3.pop()

d4 = schemdraw.Drawing()
d4 += elm.ElementDrawing(d1)
d4 += elm.ElementDrawing(d2)
d4 += elm.ElementDrawing(d3)
d4.draw()

import ahkab
from ahkab import circuit, printing, time_functions

mycircuit = circuit.Circuit(title="RON EXAMPLE CIRCUT")

voltage_step = time_functions.pulse(v1=0, v2=1, td=500e-9, tr=1e-12, pw=1, tf=1e-12, per=2)
gnd = mycircuit.get_ground_node()

mycircuit.add_resistor('R1', n1='n1', n2='n2', value=1)
mycircuit.add_vsource('E1', n1='n2', n2='n3', dc_value=24)  # , ac_value=1, function=voltage_step)
mycircuit.add_resistor('R2', n1='n1', n2='n4', value=1)
mycircuit.add_vsource('E2', n1='n4', n2='n3', dc_value=16)  # , ac_value=1, function=voltage_step)
mycircuit.add_resistor('R5', n1='n1', n2=gnd, value=2.166)
mycircuit.add_resistor('R3', n1=gnd, n2='n5', value=2)
mycircuit.add_vsource('E3', n1='n5', n2='n3', dc_value=12)  # , ac_value=1, function=voltage_step)
mycircuit.add_resistor('R4', n1=gnd, n2='n3', value=4)

# mycircuit.add_vsource("V1", n1="n1", n2=gnd, dc_value=5, ac_value=1, function=voltage_step)

print(mycircuit)

op_analysis = ahkab.new_op()
ac_analysis = ahkab.new_ac(start=1e3, stop=1e5, points=100)
tran_analysis = ahkab.new_tran(tstart=0, tstop=1.2e-3, tstep=1e-6, x0=None)

r = ahkab.run(mycircuit, an_list=[op_analysis, ac_analysis, tran_analysis])
print('\n\n\n\n\n\n')
print(r)
print('\n\n\n\n\n\n')
print(r['tran']['T'], '\n')
print(r['op']['Vn3'], '\n')

# print('r[\'op\'].results =',r['op'].results,'\n')
# print('r[\'op\'].keys() =',r['op'].keys(),'\n')
# print('r[\'op\'][\'VN4\'] =',r['op']['VN4'],'\n')
# print("The DC output voltage is %s %s" % (r['op']['VN4'] , r['op'].units['VN4']),'/n') #'The DC output voltage is 3.33333333333 V')
# print("The DC input voltage is %s %s" % (r['op']['VN1'] , r['op'].units['VN1']),'/n') #'The DC output voltage is 3.33333333333 V')
# print('r[\'ac\'] =',r['ac'],'\n')
# print('r[\'ac\'].keys() =',r['ac'].keys(),'\n')
# print('r[\'tran\'] =',r['tran'],'\n')
# print('r[\'tran\'].keys() =',r['tran'].keys(),'\n')
# print("The AC output voltage is %s %s" % (r['tran']['Vn4'] , r['tran'].units['Vn4']),'/n')

import matplotlib.pylab as plt
import numpy as np

fig = plt.figure()
plt.title(mycircuit.title + " - TRAN Simulation")
plt.plot(r['tran']['T'], r['tran']['VN1'], label="Input voltage")
# plt.hold(True)
plt.plot(r['tran']['T'], r['tran']['VN3'], label="output voltage")
plt.legend()
# plt.hold(False)
plt.grid(True)
# plt.ylim([0,1.2])
plt.ylabel('Step response')
plt.xlabel('Time [s]')
fig.savefig('tran_plot.png')

fig = plt.figure()
plt.subplot(211)
plt.semilogx(r['ac']['f'], np.abs(r['ac']['Vn4']))  # , 'o-')
plt.ylabel('abs(V(n4)) [V]')
plt.title(mycircuit.title + " - AC Simulation")
plt.subplot(212)
plt.grid(True)
plt.semilogx(r['ac']['f'], np.angle(r['ac']['Vn4']))  # , 'o-')
plt.xlabel('Angular frequency [rad/s]')
plt.ylabel('arg(V(n4)) [rad]')
fig.savefig('ac_plot.png')
plt.show()
