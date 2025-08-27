import pyqcm
from pyqcm.spectral import *
import model_1D_4

# pyqcm.set_global_parameter('verb_ED')

pyqcm.set_target_sectors(['R0:N4:S0'])
pyqcm.set_parameters("""
t=1
U=4
mu=2
""")


pyqcm.new_model_instance()

spectral_function(path='line')