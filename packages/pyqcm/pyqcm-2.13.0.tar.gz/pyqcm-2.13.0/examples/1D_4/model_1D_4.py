from pyqcm import *
set_global_parameter('verb_warning')

new_cluster_model('L4', 4, 0)
add_cluster('L4', [0, 0, 0], [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]])
lattice_model('1D_L4', [[4, 0, 0]])

interaction_operator('U')
interaction_operator('V', link=[1,0,0], amplitude=1)
interaction_operator('J', link=[1,0,0], type='Hund')
hopping_operator('t', [1, 0, 0], -1)  # NN hopping
hopping_operator('ti', [1, 0, 0], -1, tau=2)  # NN hopping with imaginary amplitude
hopping_operator('tp', [2, 0, 0], -1)  # NNN hopping
hopping_operator('hx', [0, 0, 0], 1, tau=0, sigma=1)  # field in the x direction
hopping_operator('h', [0, 0, 0], 1, tau=0, sigma=3)  # field in the x direction
anomalous_operator('D', [1, 0, 0], 1)  # NN singlet
anomalous_operator('Di', [1, 0, 0], 1j)  # NN singlet with imaginary amplitude
anomalous_operator('S', [0, 0, 0], 1)  # on-site singlet
anomalous_operator('Si', [0, 0, 0], 1j)  # on-site singlet with imaginary amplitude
anomalous_operator('Pz', [1, 0, 0], 1, type='dz')  # NN triplet
anomalous_operator('Py', [1, 0, 0], 1, type='dy')  # NN triplet
anomalous_operator('Px', [1, 0, 0], 1, type='dx')  # NN triplet
density_wave('M', 'Z', [1, 0, 0])
density_wave('H', 'Z', [0, 0, 0])
density_wave('Hx', 'X', [0, 0, 0])
density_wave('cdw', 'N', [1, 0, 0])

e = np.sqrt(0.5)
explicit_operator('V0m', [
([0,0,0], [0,0,0], e),
([3,0,0], [0,0,0], e),
], tau=0, type='one-body')

explicit_operator('V1m', [
([0,0,0], [0,0,0], e),
([3,0,0], [0,0,0],-e),
], tau=0, type='one-body')

# from pyqcm.draw_operator import draw_operator
# draw_operator('t')