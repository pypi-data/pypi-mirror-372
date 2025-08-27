from pyqcm import *
from pyqcm.Kolmogorov_Smirnov import *
import numpy as np
import pytest
from common import extract_GS_energy

format_to_test = ["S", "E"]

class Test_diagonalization_complex:
    
    @pytest.mark.parametrize("fmt", format_to_test)
    def test_simulation_complex(self,fmt):
        """
        Test if the simulation run
        """
        import model_1D_8
        set_target_sectors(['R0:N8:S0'])
        set_parameters("""
            U=1e-9
            mu = 0
            ti=1
        """)
        I = new_model_instance(record=True)
        I.print(fmt+"_complex.out")
        return
    
    @pytest.mark.parametrize("fmt", format_to_test)
    def test_simulation_complex(self,fmt):
        ref_gs_energy = extract_GS_energy("S_format_complex.ref")
        test_gs_energy = extract_GS_energy(fmt+"_complex.out")
        print("Ref:", ref_gs_energy)
        print("Test:", test_gs_energy)
        assert np.isclose(ref_gs_energy['R0:N8:S0:1'], test_gs_energy['R0:N8:S0:1'])

