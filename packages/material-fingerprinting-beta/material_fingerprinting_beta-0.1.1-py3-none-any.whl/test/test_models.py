import numpy as np
import unittest

import material_fingerprinting as mf

# hard coded material models for testing
def compute_P11_BlatzKo_triaxial_incompressible(F11,F22,F33,theta):
    # if F is a diagonal matrix with F11, F22, F33 on the diagonal
    # the 1st Piola-Kirchhoff stress component P11 for the Blatz-Ko model is
    return 2*theta*(F11*F22**2 - np.power(F11,-3))
def compute_P11_BlatzKo_triaxial_incompressible_2(F11,F22,F33,theta):
    # if F is a diagonal matrix with F11, F22, F33 on the diagonal
    # the 1st Piola-Kirchhoff stress component P11 for the Blatz-Ko model is
    return 2*theta*(F11*(F22**2+F33**2) - (F11**2+F22**2)*F33**2/F11)
def compute_P11_Demiray_uniaxial_tension(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="uniaxial tension/compression")
    return 2*theta*alpha*np.exp(alpha*(I1-3))*(lam - np.power(lam,-2))
def compute_P12_Demiray_simple_shear(gamma,theta,alpha):
    I1 = mf.Kinematics.compute_I1(gamma,format="simple shear")
    return 2*theta*alpha*np.exp(alpha*(I1-3))*gamma
def compute_P11_Demiray_pure_shear(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="pure shear")
    return 2*theta*alpha*np.exp(alpha*(I1-3))*(lam - np.power(lam,-3))
def compute_P11_Demiray_equibiaxial_tension(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="equibiaxial tension/compression")
    return 2*theta*alpha*np.exp(alpha*(I1-3))*(lam - np.power(lam,-5))
def compute_P11_Gent_uniaxial_tension(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="uniaxial tension/compression")
    return 2*theta*alpha/(1 - alpha*(I1-3)) * (lam - np.power(lam,-2))
def compute_P12_Gent_simple_shear(gamma,theta,alpha):
    I1 = mf.Kinematics.compute_I1(gamma,format="simple shear")
    return 2*theta*alpha/(1 - alpha*(I1-3)) * gamma
def compute_P11_Gent_pure_shear(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="pure shear")
    return 2*theta*alpha/(1 - alpha*(I1-3)) * (lam - np.power(lam,-3))
def compute_P11_Gent_equibiaxial_tension(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="equibiaxial tension/compression")
    return 2*theta*alpha/(1 - alpha*(I1-3)) * (lam - np.power(lam,-5))
def compute_P11_Holzapfel_uniaxial_tension(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="uniaxial tension/compression")
    return 4*theta*alpha*(I1-3)*np.exp(alpha*(I1-3)**2)*(lam - np.power(lam,-2))
def compute_P12_Holzapfel_simple_shear(gamma,theta,alpha):
    I1 = mf.Kinematics.compute_I1(gamma,format="simple shear")
    return 4*theta*alpha*(I1-3)*np.exp(alpha*(I1-3)**2)*gamma
def compute_P11_Holzapfel_pure_shear(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="pure shear")
    return 4*theta*alpha*(I1-3)*np.exp(alpha*(I1-3)**2)*(lam - np.power(lam,-3))
def compute_P11_Holzapfel_equibiaxial_tension(lam,theta,alpha):
    I1 = mf.Kinematics.compute_I1(lam,format="equibiaxial tension/compression")
    return 4*theta*alpha*(I1-3)*np.exp(alpha*(I1-3)**2)*(lam - np.power(lam,-5))
def compute_P11_NeoHooke_triaxial_incompressible(F11,F22,F33,theta):
    # if F is a diagonal matrix with F11, F22, F33 on the diagonal
    # the 1st Piola-Kirchhoff stress component P11 for the Neo-Hooke model is
    return 2*theta*(F11 - F33**2/F11)
def compute_P11_NeoHooke_uniaxial_tension(lam,theta):
    return 2*theta*(lam - lam**(-2))
def compute_P12_NeoHooke_simple_shear(gamma,theta):
    return 2*theta*gamma
def compute_P11_NeoHooke_pure_shear(lam,theta):
    return 2*theta*(lam - lam**(-3))
def compute_P11_NeoHooke_equibiaxial_tension(lam,theta):
    return 2*theta*(lam - lam**(-5))
def compute_P11_Ogden_triaxial_incompressible(F11,F22,F33,theta,alpha):
    # if F is a diagonal matrix with F11, F22, F33 on the diagonal
    # the 1st Piola-Kirchhoff stress component P11 for the Ogden model is
    return theta*alpha*(np.power(F11,alpha-1) - np.power(F33,alpha)/F11)
def compute_P11_Ogden_uniaxial_tension(lam,theta,alpha):
    return theta*alpha*(np.power(lam,alpha-1) - np.power(lam,-alpha/2-1))
def compute_P12_Ogden_simple_shear(gamma,theta,alpha):
    C_bar = 1 + 1.0/2.0 * gamma**2.0
    C_aux = np.sqrt(C_bar**2.0 - 1.0)
    dQ_dC1 = alpha/2.0 * np.power(C_bar - C_aux,alpha/2.0-1.0) * (1.0 - C_bar/C_aux) # own derivation
    dQ_dC2 = alpha/2.0 * np.power(C_bar + C_aux,alpha/2.0-1.0) * (1.0 + C_bar/C_aux) # own derivation
    return theta * gamma * (dQ_dC1 + dQ_dC2)
def compute_P12_Ogden_simple_shear_2(gamma,theta,alpha):
    C_bar = 1 + 1.0/2.0 * gamma**2.0
    C_aux = np.sqrt(C_bar**2.0 - 1.0)
    dQ_dC1 = - alpha * np.power(C_bar - C_aux,alpha/2.0) / (2.0*C_aux) # Wolfram
    dQ_dC2 = alpha * np.power(C_bar + C_aux,alpha/2.0) / (2.0*C_aux) # Wolfram
    return theta * gamma * (dQ_dC1 + dQ_dC2)
def compute_P11_Ogden_pure_shear(lam,theta,alpha):
    return theta*alpha*(np.power(lam,alpha-1) - np.power(lam,-alpha-1))
def compute_P11_Ogden_equibiaxial_tension(lam,theta,alpha):
    return theta*alpha*(np.power(lam,alpha-1) - np.power(lam,-2*alpha-1))

class test_models(unittest.TestCase):

    def test_BlatzKo(self):
        theta = 5.0
        lam = 2.4
        mat = mf.Material(name="Blatz-Ko - incompressible")

        # uniaxial tension\compression
        exp = mf.Experiment(name="uniaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_BlatzKo_triaxial_incompressible(lam,1/np.sqrt(lam),1/np.sqrt(lam),theta))
        self.assertAlmostEqual(P11, compute_P11_BlatzKo_triaxial_incompressible_2(lam,1/np.sqrt(lam),1/np.sqrt(lam),theta))

        # pure shear
        exp = mf.Experiment(name="pure shear",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_BlatzKo_triaxial_incompressible(lam,1,1/lam,theta))
        self.assertAlmostEqual(P11, compute_P11_BlatzKo_triaxial_incompressible_2(lam,1,1/lam,theta))

        # equibiaxial tension\compression
        exp = mf.Experiment(name="equibiaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_BlatzKo_triaxial_incompressible(lam,lam,1/lam**2,theta))
        self.assertAlmostEqual(P11, compute_P11_BlatzKo_triaxial_incompressible_2(lam,lam,1/lam**2,theta))

    def test_Demiray(self):
        theta = 5.0
        alpha = 3.0
        lam = 1.1
        mat = mf.Material(name="Demiray - incompressible")

        # uniaxial tension\compression
        exp = mf.Experiment(name="uniaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Demiray_uniaxial_tension(lam,theta,alpha))

        # simple shear
        exp = mf.Experiment(name="simple shear",control_min=1.0,control_max=lam,n_steps=2)
        P12 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P12, compute_P12_Demiray_simple_shear(lam,theta,alpha))

        # pure shear
        exp = mf.Experiment(name="pure shear",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Demiray_pure_shear(lam,theta,alpha))

        # equibiaxial tension\compression
        exp = mf.Experiment(name="equibiaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Demiray_equibiaxial_tension(lam,theta,alpha))

    def test_Gent(self):
        theta = 5.0
        alpha = 3.0
        lam = 2.4
        mat = mf.Material(name="Gent - incompressible")

        # uniaxial tension\compression
        exp = mf.Experiment(name="uniaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Gent_uniaxial_tension(lam,theta,alpha))

        # simple shear
        exp = mf.Experiment(name="simple shear",control_min=1.0,control_max=lam,n_steps=2)
        P12 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P12, compute_P12_Gent_simple_shear(lam,theta,alpha))

        # pure shear
        exp = mf.Experiment(name="pure shear",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Gent_pure_shear(lam,theta,alpha))

        # equibiaxial tension\compression
        exp = mf.Experiment(name="equibiaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Gent_equibiaxial_tension(lam,theta,alpha))

    def test_Holzapfel(self):
        theta = 5.0
        alpha = 3.0
        lam = 1.1
        mat = mf.Material(name="Holzapfel - incompressible")

        # uniaxial tension\compression
        exp = mf.Experiment(name="uniaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Holzapfel_uniaxial_tension(lam,theta,alpha))

        # simple shear
        exp = mf.Experiment(name="simple shear",control_min=1.0,control_max=lam,n_steps=2)
        P12 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P12, compute_P12_Holzapfel_simple_shear(lam,theta,alpha))

        # pure shear
        exp = mf.Experiment(name="pure shear",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Holzapfel_pure_shear(lam,theta,alpha))

        # equibiaxial tension\compression
        exp = mf.Experiment(name="equibiaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Holzapfel_equibiaxial_tension(lam,theta,alpha))

    def test_NeoHooke(self):
        theta = 5.0
        lam = 2.4
        mat = mf.Material(name="Neo-Hooke - incompressible")

        # uniaxial tension\compression
        exp = mf.Experiment(name="uniaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_NeoHooke_triaxial_incompressible(lam,1/np.sqrt(lam),1/np.sqrt(lam),theta))
        self.assertAlmostEqual(P11, compute_P11_NeoHooke_uniaxial_tension(lam,theta))

        # simple shear
        exp = mf.Experiment(name="simple shear",control_min=1.0,control_max=lam,n_steps=2)
        P12 = mat.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P12, compute_P12_NeoHooke_simple_shear(lam,theta))

        # pure shear
        exp = mf.Experiment(name="pure shear",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_NeoHooke_triaxial_incompressible(lam,1,1/lam,theta))
        self.assertAlmostEqual(P11, compute_P11_NeoHooke_pure_shear(lam,theta))

        # equibiaxial tension\compression
        exp = mf.Experiment(name="equibiaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_NeoHooke_triaxial_incompressible(lam,lam,1/lam**2,theta))
        self.assertAlmostEqual(P11, compute_P11_NeoHooke_equibiaxial_tension(lam,theta))

    def test_Ogden(self):
        theta = 5.0
        alpha = 3.0
        lam = 2.4
        mat = mf.Material(name="Ogden - incompressible")

        # uniaxial tension\compression
        exp = mf.Experiment(name="uniaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Ogden_triaxial_incompressible(lam,1/np.sqrt(lam),1/np.sqrt(lam),theta,alpha))
        self.assertAlmostEqual(P11, compute_P11_Ogden_uniaxial_tension(lam,theta,alpha))

        # simple shear
        exp = mf.Experiment(name="simple shear",control_min=1.0,control_max=lam,n_steps=2)
        P12 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P12, compute_P12_Ogden_simple_shear(lam,theta,alpha))
        self.assertAlmostEqual(P12, compute_P12_Ogden_simple_shear_2(lam,theta,alpha))

        # pure shear
        exp = mf.Experiment(name="pure shear",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Ogden_triaxial_incompressible(lam,1,1/lam,theta,alpha))
        self.assertAlmostEqual(P11, compute_P11_Ogden_pure_shear(lam,theta,alpha))

        # equibiaxial tension\compression
        exp = mf.Experiment(name="equibiaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)
        P11 = mat.conduct_experiment(exp,parameters = [theta, alpha]).reshape(-1)[-1]
        self.assertAlmostEqual(P11, compute_P11_Ogden_triaxial_incompressible(lam,lam,1/lam**2,theta,alpha))
        self.assertAlmostEqual(P11, compute_P11_Ogden_equibiaxial_tension(lam,theta,alpha))

    def test_uniaxial_tension(self):
        lam = 2.4
        exp = mf.Experiment(name="uniaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)

        # material parameters
        theta = 5.0

        # test if Neo-Hooke is a special case of Mooney-Rivlin
        mat1 = mf.Material(name="Neo-Hooke - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Mooney-Rivlin - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [theta,0]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

        # test if Neo-Hooke is a special case of Ogden
        mat1 = mf.Material(name="Neo-Hooke - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Ogden - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [theta,2]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

        # test if Blatz-Ko is a special case of Mooney-Rivlin
        mat1 = mf.Material(name="Blatz-Ko - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Mooney-Rivlin - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [0,theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

    def test_simple_shear(self):
        gamma = 2.4
        exp = mf.Experiment(name="simple shear",control_min=1.0,control_max=gamma,n_steps=2)

        # material parameters
        theta = 5.0

        # test if Neo-Hooke is a special case of Mooney-Rivlin
        mat1 = mf.Material(name="Neo-Hooke - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Mooney-Rivlin - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [theta,0]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

        # test if Neo-Hooke is a special case of Ogden
        mat1 = mf.Material(name="Neo-Hooke - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Ogden - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [theta,2]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

        # test if Blatz-Ko is a special case of Mooney-Rivlin
        mat1 = mf.Material(name="Blatz-Ko - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Mooney-Rivlin - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [0,theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

    def test_pure_shear(self):
        lam = 2.4
        exp = mf.Experiment(name="pure shear",control_min=1.0,control_max=lam,n_steps=2)

        # material parameters
        theta = 5.0

        # test if Neo-Hooke is a special case of Mooney-Rivlin
        mat1 = mf.Material(name="Neo-Hooke - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Mooney-Rivlin - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [theta,0]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

        # test if Neo-Hooke is a special case of Ogden
        mat1 = mf.Material(name="Neo-Hooke - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Ogden - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [theta,2]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

        # test if Blatz-Ko is a special case of Mooney-Rivlin
        mat1 = mf.Material(name="Blatz-Ko - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Mooney-Rivlin - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [0,theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

    def test_equibiaxial_tension(self):
        lam = 2.4
        exp = mf.Experiment(name="equibiaxial tension/compression",control_min=1.0,control_max=lam,n_steps=2)

        # material parameters
        theta = 5.0
        
        # test if Neo-Hooke is a special case of Mooney-Rivlin
        mat1 = mf.Material(name="Neo-Hooke - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Mooney-Rivlin - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [theta,0]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

        # test if Neo-Hooke is a special case of Ogden
        mat1 = mf.Material(name="Neo-Hooke - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Ogden - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [theta,2]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

        # test if Blatz-Ko is a special case of Mooney-Rivlin
        mat1 = mf.Material(name="Blatz-Ko - incompressible")
        P11_comp1 = mat1.conduct_experiment(exp,parameters = [theta]).reshape(-1)[-1]
        mat2 = mf.Material(name="Mooney-Rivlin - incompressible")
        P11_comp2 = mat2.conduct_experiment(exp,parameters = [0,theta]).reshape(-1)[-1]
        self.assertAlmostEqual(P11_comp1, P11_comp2)

if __name__ == "__main__":
    unittest.main()