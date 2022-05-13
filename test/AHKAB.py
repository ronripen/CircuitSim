import ahkab
from ahkab import circuit, printing, time_functions

mycircuit = circuit.Circuit(title="Butterworth Example circuit")

gnd = mycircuit.get_ground_node()

mycircuit.add_resistor("R1", n1="n1", n2="n2", value=700)
mycircuit.add_inductor("L1", n1="n2", n2="n3", value=0.05)
mycircuit.add_capacitor("C1", n1="n3", n2=gnd, value=1.5e-7)
mycircuit.add_inductor("L2", n1="n3", n2="n16", value=0.05)
mycircuit.add_capacitor("C2", n1="n16", n2=gnd, value=1.5e-7)
mycircuit.add_resistor("R2", n1="n16", n2=gnd, value=700)

voltage_step = time_functions.pulse(v1=0, v2=1, td=500e-9, tr=1e-12, pw=1, tf=1e-12, per=2)
mycircuit.add_vsource("V1", n1="n1", n2=gnd, dc_value=5, ac_value=1, function=voltage_step)

tran_analysis = ahkab.new_tran(tstart=0, tstop=1.2e-3, tstep=1e-6, x0=None)
r = ahkab.run(mycircuit, an_list=[tran_analysis])

Vout = 'VN16'
print(r['tran'][Vout][-1])
