from pyqcm import *
from pyqcm.cdmft import *

import model_1D_2_4b

np.set_printoptions(precision=4, linewidth=512, suppress=True)

sec = 'R0:N6:S0'
set_target_sectors([sec])

set_parameters("""
    U=4
    mu=1
    t=1
    tb1_1=0.5
    tb2_1=0.5
    eb1_1=1
    eb2_1=-1
""")

pyqcm.solver='dvmc'
pyqcm.new_model_instance()
obs_mu = observable('mu_1', 1e-4, 4)
obs_t = observable('t_1', 1e-4, 4)
A = cdmft(varia=['tb1_1', 'tb2_1', 'eb1_1', 'eb2_1'], accur=1e-6, accur_hybrid=1e-8, accur_dist=1e-10, observables=[obs_mu, obs_t])
print(A)
