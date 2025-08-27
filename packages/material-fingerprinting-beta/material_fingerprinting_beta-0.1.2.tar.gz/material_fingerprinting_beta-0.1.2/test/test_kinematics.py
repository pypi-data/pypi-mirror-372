import numpy as np
import unittest

import material_fingerprinting as mf

class test_kinematics(unittest.TestCase):
    
    def test_invariants(self):
        
        # uniaxial tension/compression
        lam = 2.4
        F = np.array([[lam,0,0],[0,np.sqrt(1/lam),0],[0,0,np.sqrt(1/lam)]])
        C = F.T @ F
        I1 = np.trace(C)
        I2 = 0.5*(I1**2 - np.trace(C @ C))
        I3 = np.linalg.det(C)

        I1_comp = mf.compute_I1(lam,format="uniaxial tension/compression")
        I2_comp = mf.compute_I2(lam,format="uniaxial tension/compression")

        self.assertAlmostEqual(I1, I1_comp)
        self.assertAlmostEqual(I2, I2_comp)
        self.assertAlmostEqual(I3, 1.0)

        # simple shear
        gamma = 2.4
        F = np.array([[1,gamma,0],[0,1,0],[0,0,1]])
        C = F.T @ F
        I1 = np.trace(C)
        I2 = 0.5*(I1**2 - np.trace(C @ C))
        I3 = np.linalg.det(C)

        I1_comp = mf.compute_I1(lam,format="simple shear")
        I2_comp = mf.compute_I2(lam,format="simple shear")

        self.assertAlmostEqual(I1, I1_comp)
        self.assertAlmostEqual(I2, I2_comp)
        self.assertAlmostEqual(I3, 1.0)

        # pure shear
        lam = 2.4
        F = np.array([[lam,0,0],[0,1/lam,0],[0,0,1]])
        C = F.T @ F
        I1 = np.trace(C)
        I2 = 0.5*(I1**2 - np.trace(C @ C))
        I3 = np.linalg.det(C)

        I1_comp = mf.compute_I1(lam,format="pure shear")
        I2_comp = mf.compute_I2(lam,format="pure shear")

        self.assertAlmostEqual(I1, I1_comp)
        self.assertAlmostEqual(I2, I2_comp)
        self.assertAlmostEqual(I3, 1.0)

        # equibiaxial tension/compression
        lam = 2.4
        F = np.array([[lam,0,0],[0,lam,0],[0,0,1/(lam**2)]])
        C = F.T @ F
        I1 = np.trace(C)
        I2 = 0.5*(I1**2 - np.trace(C @ C))
        I3 = np.linalg.det(C)

        I1_comp = mf.compute_I1(lam,format="equibiaxial tension/compression")
        I2_comp = mf.compute_I2(lam,format="equibiaxial tension/compression")

        self.assertAlmostEqual(I1, I1_comp)
        self.assertAlmostEqual(I2, I2_comp)
        self.assertAlmostEqual(I3, 1.0)

    def test_invariant_derivatives_triaxial_incompressible(self):

        control = 2.4

        # uniaxial tension/compression
        dI1 = mf.compute_I1_derivative(control,format="uniaxial tension/compression")
        dI1_mod = mf.compute_I1_derivative_triaxial_incompressible(control, np.sqrt(1/control), np.sqrt(1/control))
        self.assertAlmostEqual(dI1, dI1_mod)
        dI2 = mf.compute_I2_derivative(control,format="uniaxial tension/compression")
        dI2_mod = mf.compute_I2_derivative_triaxial_incompressible(control, np.sqrt(1/control), np.sqrt(1/control))
        self.assertAlmostEqual(dI2, dI2_mod)

        # pure shear
        dI1 = mf.compute_I1_derivative(control,format="pure shear")
        dI1_mod = mf.compute_I1_derivative_triaxial_incompressible(control, 1, 1/control)
        self.assertAlmostEqual(dI1, dI1_mod)
        dI2 = mf.compute_I2_derivative(control,format="pure shear")
        dI2_mod = mf.compute_I2_derivative_triaxial_incompressible(control, 1, 1/control)
        self.assertAlmostEqual(dI2, dI2_mod)

        # equibiaxial tension/compression
        dI1 = mf.compute_I1_derivative(control,format="equibiaxial tension/compression")
        dI1_mod = mf.compute_I1_derivative_triaxial_incompressible(control, control, 1/control**2)
        self.assertAlmostEqual(dI1, dI1_mod)
        dI2 = mf.compute_I2_derivative(control,format="equibiaxial tension/compression")
        dI2_mod = mf.compute_I2_derivative_triaxial_incompressible(control, control, 1/control**2)
        self.assertAlmostEqual(dI2, dI2_mod)

    def test_invariant_derivatives(self):

        pass
        
        
if __name__ == "__main__":
    unittest.main()