from pyqcm import *
from pyqcm.cdmft import *
from pyqcm.spectral import *

import model_1D_2_4b

np.set_printoptions(precision=4, linewidth=512, suppress=True)

sec = 'R0:S0'

set_target_sectors([sec])
set_parameters("""
    U=4
    mu=1
    t=1
    tb1_1=0.5
    tb2_1=0.5
    eb1_1=1.5
    eb2_1=-1
    sb1_1 = 0.1
    sb2_1 = 0.1
    sbi1_1 = 1e-9
    sbi2_1 = 1e-9
""")
var = [
'eb1_1',
'eb2_1',
'tb1_1',
'tb2_1',
'sbi1_1',
'sbi2_1',
'sb1_1',
'sb2_1',
]

pyqcm.new_model_instance()
params = parameters() # params is a dict
nvar = len(var)
S = np.empty(nvar)
for i in range(nvar):
    S[i] = params[var[i]]

vset = [S]
print(vset)
cdmft_distance_debug(var, vset, beta=20, wc=1); exit()


# cluster_spectral_function(self=True, file = 's1.pdf')
# hybridization_function(wmax=4, file = 'h1.pdf')