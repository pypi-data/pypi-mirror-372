from pyqcm import *
new_cluster_model('L4', 4, 0, generators=None, bath_irrep=False)
add_cluster('L4', [0, 0, 0], [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]], ref = 0)
lattice_model('1D_L4', [[4, 0, 0]], None)
interaction_operator('U', band1=1, band2=1)
interaction_operator('V', band1=1, band2=1, link=[1, 0, 0], amplitude=1)
interaction_operator('J', band1=1, band2=1, link=[1, 0, 0], type='Hund')
hopping_operator('t', [1, 0, 0], -1, band1=1, band2=1)
hopping_operator('ti', [1, 0, 0], -1, band1=1, band2=1, tau=2)
hopping_operator('tp', [2, 0, 0], -1, band1=1, band2=1)
hopping_operator('hx', [0, 0, 0], 1, band1=1, band2=1, tau=0, sigma=1)
hopping_operator('h', [0, 0, 0], 1, band1=1, band2=1, tau=0, sigma=3)
anomalous_operator('D', [1, 0, 0], 1, band1=1, band2=1)
anomalous_operator('Di', [1, 0, 0], 1j, band1=1, band2=1)
anomalous_operator('S', [0, 0, 0], 1, band1=1, band2=1)
anomalous_operator('Si', [0, 0, 0], 1j, band1=1, band2=1)
anomalous_operator('Pz', [1, 0, 0], 1, band1=1, band2=1, type='dz')
anomalous_operator('Py', [1, 0, 0], 1, band1=1, band2=1, type='dy')
anomalous_operator('Px', [1, 0, 0], 1, band1=1, band2=1, type='dx')
density_wave('M', 'Z', [1, 0, 0])
density_wave('H', 'Z', [0, 0, 0])
density_wave('Hx', 'X', [0, 0, 0])
density_wave('cdw', 'N', [1, 0, 0])
explicit_operator('V0m', [([0, 0, 0], [0, 0, 0], 0.7071067811865476), ([3, 0, 0], [0, 0, 0], 0.7071067811865476)], tau=0, type='one-body')
explicit_operator('V1m', [([0, 0, 0], [0, 0, 0], 0.7071067811865476), ([3, 0, 0], [0, 0, 0], -0.7071067811865476)], tau=0, type='one-body')

try:
    import model_extra
except:
    pass		
set_target_sectors(['R0:N4'])
set_parameters("""

t=1
U=0
mu = 2
hx = 0.1
""")
set_parameter("U", 0.0)
set_parameter("hx", 0.1)
set_parameter("mu", 2.0)
set_parameter("t", 1.0)

new_model_instance(0)

solution=[None]*1

#--------------------- cluster no 1 -----------------
solution[0] = """
hx	0.1
mu	2
t	1

GS_energy: -16 GS_sector: 
GF_format: bl
mixing	2
state
R0	0	-1.49167e-154
w	8	8
-3.7180339887499	-0.26286555605957	-0.42532540417602	-0.42532540417602	-0.26286555605957	0.26286555605957	0.42532540417602	0.42532540417602	0.26286555605957
-3.5180339887499	-0.26286555605957	-0.42532540417602	-0.42532540417602	-0.26286555605957	-0.26286555605957	-0.42532540417602	-0.42532540417602	-0.26286555605957
-2.7180339887499	-0.42532540417602	-0.26286555605957	0.26286555605957	0.42532540417602	0.42532540417602	0.26286555605957	-0.26286555605957	-0.42532540417602
-2.5180339887499	0.42532540417602	0.26286555605957	-0.26286555605957	-0.42532540417602	0.42532540417602	0.26286555605957	-0.26286555605957	-0.42532540417602
-1.4819660112501	0.42532540417602	-0.26286555605957	-0.26286555605957	0.42532540417602	-0.42532540417602	0.26286555605957	0.26286555605957	-0.42532540417602
-1.2819660112501	0.42532540417602	-0.26286555605957	-0.26286555605957	0.42532540417602	0.42532540417602	-0.26286555605957	-0.26286555605957	0.42532540417602
-0.48196601125011	0.26286555605957	-0.42532540417602	0.42532540417602	-0.26286555605957	-0.26286555605957	0.42532540417602	-0.42532540417602	0.26286555605957
-0.28196601125011	-0.26286555605957	0.42532540417602	-0.42532540417602	0.26286555605957	-0.26286555605957	0.42532540417602	-0.42532540417602	0.26286555605957

"""
read_cluster_model_instance(solution[0], 0)
