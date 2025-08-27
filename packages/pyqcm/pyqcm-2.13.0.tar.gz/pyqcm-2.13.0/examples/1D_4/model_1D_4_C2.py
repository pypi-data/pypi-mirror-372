from pyqcm import *

new_cluster_model('L4', 4, 0, [[4,3,2,1]])
add_cluster('L4', [0, 0, 0], [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]])
lattice_model('1D_L4', [[4, 0, 0]])

interaction_operator('U')
hopping_operator('t', [1, 0, 0], -1)  # NN hopping
hopping_operator('tp', [2, 0, 0], -1)  # NNN hopping
hopping_operator('hx', [0, 0, 0], 1, tau=0, sigma=1)  # field in the x direction
hopping_operator('h', [0, 0, 0], 1, tau=0, sigma=3)  # field in the x direction
