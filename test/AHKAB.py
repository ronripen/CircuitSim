import ahkab
from ahkab import circuit, printing, time_functions

mycircuit = circuit.Circuit(title="Butterworth Example circuit")

gnd = mycircuit.get_ground_node()

# mycircuit.add_resistor("R1", n1="PWR", n2="n2", value=700)
# mycircuit.add_inductor("L1", n1="n2", n2="n3", value=0.05)
# mycircuit.add_capacitor("C1", n1="n3", n2="n15", value=1.5e-7)
# mycircuit.add_resistor("R3", n1="n15", n2=gnd, value=1.5e-7)
# mycircuit.add_inductor("L2", n1="n3", n2="n4", value=0.05)
# mycircuit.add_capacitor("C2", n1="n4", n2="n14", value=1.5e-7)
# mycircuit.add_resistor("R3", n1="n14", n2=gnd, value=1.5e-7)
# mycircuit.add_resistor("R3", n1="n4", n2='n16', value=1.5e-7)
# mycircuit.add_resistor("R2", n1="n16", n2=gnd, value=700)

mycircuit.add_resistor("Wire", n1=gnd, n2="N15", value=1e-4)
mycircuit.add_resistor("Wire", n1=gnd, n2="N12", value=1e-4)
mycircuit.add_resistor("Wire", n1=gnd, n2="N9", value=1e-4)
mycircuit.add_resistor("R7", n1="N14", n2="N15", value=700)
mycircuit.add_resistor("Wire", n1="N11", n2="N14", value=1e-4)
mycircuit.add_capacitor("C4", n1="N11", n2="N12", value=1.5e-07)
mycircuit.add_capacitor("C5", n1="N8", n2="N9", value=1.5e-07)
mycircuit.add_inductor("L3", n1="N8", n2="N11", value=0.05)
mycircuit.add_inductor("L2", n1="N5", n2="N8", value=0.05)
mycircuit.add_resistor("R1", n1="N2", n2="N5", value=700)
mycircuit.add_resistor("Wire", n1="PWR", n2="N2", value=1e-4)



PWR = time_functions.pulse(v1=0, v2=5, td=500e-9, tr=1e-11, pw=1, tf=1e-11, per=2)
mycircuit.add_vsource("V1", n1="PWR", n2=gnd, dc_value=5, ac_value=1, function=PWR)

tran_analysis = ahkab.new_tran(tstart=0, tstop=1.2e-3, tstep=1e-6, x0=None)
r = ahkab.run(mycircuit, an_list=[tran_analysis])

Vout = 'VN14'
print(r['tran'][Vout][-1])
print(r['tran']['VPWR'])

# schemdraw still not complete, temporary solution for the test on the 23.5.22
import schemdraw
import schemdraw.elements as elm
d = [schemdraw.Drawing()]
d[-1] += elm.Source().up()
d[-1] += elm.Resistor().right().label('R1')
d[-1] += elm.Inductor().right().label('L2')
d[-1].push()
d[-1] += elm.Capacitor().down().label('C4')
d[-1].pop()
d.append(schemdraw.Drawing())
d[-1] += elm.Inductor().right().label('L3')
d[-1].push()
d[-1] += elm.Capacitor().down().label('C5')
d[-1].pop()
d.append(schemdraw.Drawing())
d[-1] += elm.Line().right()
d[-1] += elm.Resistor().down().label('R6')
d[-1] += elm.Line().left()
d[-1] += elm.Line().left()
d[-1] += elm.Line().left()
d[-1] += elm.Line().left()

dTotal = schemdraw.Drawing()
for _ in d:
    dTotal += elm.ElementDrawing(_)
dTotal.draw()