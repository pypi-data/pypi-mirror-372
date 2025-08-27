from pyqcm import *
from pyqcm.Kolmogorov_Smirnov import *
import numpy as np
import pytest
from common import extract_GS_energy, extract_pole


format_to_test = ["S", "E"]

class Test_diagonalization:
    
    @pytest.mark.parametrize("fmt", format_to_test)
    def test_simulation(self,fmt):
        """
        Test if the simulation run
        """
        from scipy.optimize import minimize
        import model_2x2_2C_8b_C2v_L
        nb = 8
        set_global_parameter('verb_ED')
        set_global_parameter('Hamiltonian_format', fmt)
        set_target_sectors(['R0:N12:S0', 'R0:N8:S0'])
        set_parameters(
            """
            U = 14
            e = 2.3
            tpd = 2.1
            tpp = 1
            tppp = 0.2
            mu = 9.68
            eb1_1 = -0.006655534
            eb2_1 = -3.3502828
            eb3_1 = -4.1133163
            eb4_1 = -0.10235806
            eb5_1 = -4.113222
            eb6_1 = -0.1023468
            eb7_1 = 0.14108001
            eb8_1 = -3.7537133
            tb1_1 = -0.11240159
            tb2_1 = -1.1061747
            tb3_1 = 1.7476608
            tb4_1 = 0.057892245
            tb5_1 = -1.7476438
            tb6_1 = -0.057886658
            tb7_1 = 0.22749261
            tb8_1=-2.3061557
            """
        )
        I = new_model_instance(record=True)
        I.print(fmt+".out")
        return
    
    @pytest.mark.parametrize("fmt", format_to_test)
    def test_GS_energy(self,fmt):
        ref_gs_energy = extract_GS_energy("S_format.ref")
        test_gs_energy = extract_GS_energy(fmt+".out")
        print("Ref:", ref_gs_energy)
        print("Test:", test_gs_energy)
        assert np.isclose(ref_gs_energy["R0:N12:S0:1"], test_gs_energy["R0:N12:S0:1"])
    
    @pytest.mark.parametrize("fmt", format_to_test)
    def test_pole(self,fmt):
        """
        This test the results of the previous simulation against a reference file
        """
        M = extract_pole(fmt+".out")[0]
        print("Test:", M)
        M = M[M[:, 0].argsort(), :]
        M = (M[:,0],M[:,1]*M[:,1])
        R = extract_pole('S_format.ref')[0]
        print("Ref:", R)
        R = R[R[:, 0].argsort(), :]
        R = (R[:,0],R[:,1]*R[:,1])
        distance = Kolmogorov_Smirnov(M, R, tol=1e-6, plot=False)
        print('Kolmogorov-Smirnov distance = ', distance)
        assert distance < 0.01


