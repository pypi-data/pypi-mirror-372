"""Module to calculate different stress strain models."""
import math as ma
import numpy as np


#pylint: disable=R0914
# pylint: disable=line-too-long
def volume(a, b, c, alp, bet, gam):
    """Calculates Volume."""
    
    
    thetsqrtv = ma.pow(ma.cos(ma.radians(alp)),2) + ma.pow(ma.cos(ma.radians(bet)),2)+ma.pow(ma.cos(ma.radians(gam)),2)-2*ma.cos(ma.radians(alp)) * ma.cos(ma.radians(bet))*ma.cos(ma.radians(gam))
    vol = a * b * c * ma.sqrt(1 - thetsqrtv)
    return vol
def dhkl(a, b, c, alp, bet, gam, h, k, l, vol):
    """Calculates lattice spacing.
    Parameters
    ----------
    - a, b, c: float
        Lattice constants in Å.
    - alp, bet, gam: float
        Unit-cell angles in degrees (α, β, γ respectively).
    - h, k, l: array_like of float or int, broadcastable to same shape
        Miller indices for the planes.
    - vol: float
        Unit cell volume in Å^3 (as returned by volume()).
    
    Returns
    ----------
    - d: ndarray
        Interplanar spacing d_{hkl} in Å, same shape as h/k/l.
    
    Notes
    ----------
    - For a triclinic cell, the general expression is:
      1/d^2 = (h^2 b^2 c^2 sin^2 α + k^2 a^2 c^2 sin^2 β + l^2 a^2 b^2 sin^2 γ
               + 2 h k a b c^2 (cos α cos β - cos γ)
               + 2 k l a^2 b c (cos β cos γ - cos α)
               + 2 h l a b^2 c (cos α cos γ - cos β)) / V^2
      Then d = V / sqrt(denominator).
    """

    hbc = np.power(h, 2) * np.power(b, 2) * np.power(c, 2) * np.power(np.sin(np.radians(alp)), 2)
    kac = np.power(k, 2) * np.power(a, 2) * np.power(c, 2) * np.power(np.sin(np.radians(bet)), 2)
    lab = np.power(l, 2) * np.power(a, 2) * np.power(b, 2) * np.power(np.sin(np.radians(gam)), 2)
    abg = 2.0 * h * k * a * b * np.power(c, 2) * (
    np.cos(np.radians(alp)) * np.cos(np.radians(bet)) - np.cos(np.radians(gam)))
    bga = 2.0 * k * l * np.power(a, 2) * b * c * (
    np.cos(np.radians(bet)) * np.cos(np.radians(gam)) - np.cos(np.radians(alp)))
    agb = 2.0 * h * l * a * np.power(b, 2) * c * (
    np.cos(np.radians(alp)) * np.cos(np.radians(gam)) - np.cos(np.radians(bet)))
    den = hbc + kac + lab + abg + bga + agb
    d =vol/np.power(den,.5)
    return d
def gammacal(hk):
    """Calculates gamma coefficient.
    Parameters
    - hk: ndarray, shape (Nrefl, 3)
        Miller indices per row [h, k, l].
    
    Returns
    - gamma: ndarray, shape (Nrefl,)
        γ = (h^2 k^2 + k^2 l^2 + h^2 l^2) / (h^2 + k^2 + l^2)^2.
    
    Notes
    - In LaTeX: \\gamma = \\dfrac{h^2 k^2 + k^2 l^2 + h^2 l^2}{(h^2 + k^2 + l^2)^2}.
    - For (h, k, l) = (0, 0, 0), returns 0 to avoid division by zero.
"""
    num=np.square(hk[:,0])*np.square(hk[:,1])+np.square(hk[:,1])*np.square(hk[:,2])+np.square(hk[:,0])*np.square(hk[:,2])
    den=np.square(np.square(hk[:,0])+np.square(hk[:,1])+np.square(hk[:,2]))
    return num/den
class StressStrainModels:
    """Class different stress strain models
        Parameters
    - bunge: ndarray, shape (Ngrains, 3, 3)
        Orientation (rotation) matrices per grain.
    - hkl: ndarray, shape (Nrefl, 3)
        Miller indices.
    - lattice: ndarray, shape (1, 6)
        [a, b, c, α, β, γ] with angles in degrees.
    - stress: ndarray, shape (6, 1) or (6,)
        Applied macroscopic stress in Voigt order [σ11, σ22, σ33, σ23, σ13, σ12].
        Units must be consistent with stiffness coefficients to produce dimensionless strains.
    - c11, c12, c44: float
        Single-crystal stiffness coefficients (e.g., GPa).
    
    Attributes
    - samplec: ndarray, shape (Nrefl, Ngrains, 3)
        Scattering direction vectors (per hkl, per grain) in the sample frame.
    - lathkl: ndarray, shape (Nrefl,)
        d_{hkl} in Å.
    - hklmag: ndarray, shape (Nrefl, 1)
        |G| ∝ c / d_{hkl} (used as a magnitude to normalize scattering direction).
    - c11p, c12p, c44p: float
        Popa’s isotropized stiffnesses for the Voigt model.
"""
    def __init__(self,bunge,hkl,lattice, stress,c11,c12,c44):
        """construct  the precompute geometry
        Parameters
        ----------
        bunge : orientation matrices
        hkl :  miller index
        lattice : lattice parameters 
        stress : stress matrix
        c11,c12,c44: stiffness coefficient """
        self.bunge=bunge
        self.stress=stress
        self.hkl=hkl
        self.lattice=lattice
        self.samplec=np.dot(self.hkl,self.bunge)
        self.volume=volume(self.lattice[0,0],self.lattice[0,1],self.lattice[0,2],self.lattice[0,3],self.lattice[0,4],self.lattice[0,5])
        self.lathkl=dhkl(self.lattice[0,0],self.lattice[0,1],self.lattice[0,2],self.lattice[0,3],self.lattice[0,4],self.lattice[0,5],self.hkl[:,0],self.hkl[:,1],self.hkl[:,2],self.volume)
        self.hklmag=float(self.lattice[0,2])/self.lathkl
        self.hklmag=np.reshape(self.hklmag,(len(self.hkl),1))
        self.c11=c11
        self.c12=c12
        self.c44=c44
        self.c11p=(3*self.c11/5)+(2*c12/5)+(4*c44/5)
        self.c12p=(self.c11-2*self.c44)/5 +4*c12/5
        self.c44p=(self.c11p-self.c12p)/2
    def voigt(self):
        """Calculates Voigt strain from a stress matrix using the model by Popa ,
         see reference https://doi.org/10.1107/97809553602060000967
         Returns
    - vstrain: ndarray, shape (Ngrains, Nrefl)
        Projected strains along the scattering directions.

    Method
    - Popa’s isotropized stiffnesses (c'_{11}, c'_{12}, c'_{44}) -> Voigt compliances:
      s_{11}^V = (c'_{11} + c'_{12}) / [(c'_{11} - c'_{12})(c'_{11} + 2c'_{12})],
      s_{12}^V = -c'_{12} / [(c'_{11} - c'_{12})(c'_{11} + 2c'_{12})],
      s_{44}^V = 1 / (4 c'_{44}).
    - Strain in Voigt notation: ε^V = S^V σ.
    - Projection with n = (B1, B2, B3):
      ε_{hkl} = B1^2 ε_{11} + B2^2 ε_{22} + B3^2 ε_{33}
                + 2 B2 B3 ε_{23} + 2 B1 B3 ε_{13} + 2 B1 B2 ε_{12}. 
        """
        s11v=(self.c11p+self.c12p)/((self.c11p-self.c12p)*(self.c11p+2*self.c12p))
        s12v=-self.c12p/((self.c11p-self.c12p)*(self.c11p+2*self.c12p))
        s44v=1/self.c44p/4
        smatrixv=1e-3*np.array([[s11v,s12v,s12v,0,0,0],[s12v,s11v,s12v,0,0,0],
                           [s12v,s12v,s11v,0,0,0],[0,0,0,s44v,0,0],[0,0,0,0,s44v,0],[0,0,0,0,0,s44v]])

        voightstrain=np.dot(smatrixv,self.stress)
        B1=self.samplec[:,:,0]/self.hklmag
        B2=self.samplec[:,:,1]/self.hklmag
        B3=self.samplec[:,:,2]/self.hklmag
        vstrain=np.power(B1,2)*voightstrain[0,0]+np.power(B2,2)*voightstrain[1,0]+np.power(B3,2)*voightstrain[2,0]+2*B2*B3*voightstrain[3,0]+2*B1*B3*voightstrain[4,0]+2*B1*B2*voightstrain[5,0]# Voight conribution of the strain
        return vstrain.T
    def reuss(self):
        """Calculates Reuss strain from a stress matrix using the model by Popa , 
        see reference https://doi.org/10.1107/97809553602060000967.
        Returns
        - rstrain: ndarray, shape (Ngrains, Nrefl)
            Projected strains along the scattering directions.
    
        Method
        - Reuss compliances:
          s_{11} = (c_{11} + c_{12}) / [(c_{11} - c_{12})(c_{11} + 2c_{12})],
          s_{12} = -c_{12} / [(c_{11} - c_{12})(c_{11} + 2c_{12})],
          s_{44} = 1 / (4 c_{44}).
        - Rotate stress σ to the crystal frame with a 6×6 Q-matrix built from a_{ij} (rotation),
          apply ε = S σ in the crystal frame.
        - Project along reciprocal direction A (normalized by |G|):
          A = [h^2, k^2, l^2, 2kl, 2hl, 2hk] / |G|^2,
          and ε_{hkl} = A · ε.
    """
       
        s11=(self.c11+self.c12)/((self.c11-self.c12)*(self.c11+2*self.c12))#Reuss
        s12=-self.c12/((self.c11-self.c12)*(self.c11+2*self.c12))#Reuss
        s44=1/self.c44/4
        smatrix=1e-3*np.array([[s11,s12,s12,0,0,0],[s12,s11,s12,0,0,0],
                           [s12,s12,s11,0,0,0],[0,0,0,s44,0,0],[0,0,0,0,s44,0],[0,0,0,0,0,s44]])##  Reuss
        a11=self.bunge[:,0,0]
        a12=self.bunge[:,0,1]
        a13=self.bunge[:,0,2]
        a21=self.bunge[:,1,0]
        a22=self.bunge[:,1,1]
        a23=self.bunge[:,1,2]
        a31=self.bunge[:,2,0]
        a32=self.bunge[:,2,1]
        a33=self.bunge[:,2,2]
        Qmatrix=np.array([[a11*a11,a12*a12,a13*a13,2*a12*a13,2*a11*a13,2*a11*a12],[a21*a21,a22*a22,a23*a23,2*a22*a23,2*a21*a23,2*a21*a22],[a31*a31,a32*a32,a33*a33,2*a32*a33,2*a31*a33,2*a31*a32],
                           [a21*a31,a22*a32,a33*a23,a22*a33+a23*a32,a33*a21+a31*a23,a22*a31+a21*a32],[a11*a31,a12*a32,a13*a33,a33*a12+a32*a13,a11*a33+a13*a31,a11*a32+a12*a31],
                           [a11*a21,a12*a22,a13*a23,a22*a13+a23*a12,a11*a23+a13*a21,a11*a22+a12*a21]])
        rstress=np.array([np.dot(Qmatrix[:,:,i],self.stress)for  i in range (len(self.bunge))])
        rhomatrix=np.array([[1],[1],[1],[2],[2],[2]])
        rrstress=rhomatrix*rstress
        rstrain=np.dot(smatrix,rrstress)
        A1=self.hkl[:,0]/self.hklmag[:,0]
        A2=self.hkl[:,1]/self.hklmag[:,0]
        A3=self.hkl[:,2]/self.hklmag [:,0]
        Amatrix=np.array([[np.power(A1,2),np.power(A2,2),np.power(A3,2),2*A2*A3,2*A1*A3,2*A1*A2]])
        rstrainv=np.array([np.dot(Amatrix[0,:,h],rstrain[:,i,0]) for h in range(len(self.hkl)) for  i in range (len(self.bunge))])
        rstrainv=rstrainv.reshape(len(self.hkl),len(self.bunge))
        return rstrainv.T
    def hill (self):
        """Calculates Hill strain from a stress matrix using the model by Popa , 
        see reference https://doi.org/10.1107/97809553602060000967.
        Hill strain projection as an average of Voigt and Reuss.

        Returns
        - hstrain: ndarray, shape (Ngrains, Nrefl)
            ε^H_{hkl} = (ε^V_{hkl} + ε^R_{hkl}) / 2.
        """

        return (self.reuss()+self.voigt())/2.0
    def kronerrandom(self):
        """Calculates Eshelby-Kroner strain from a stress matrix using the model by Popa , 
        see reference https://doi.org/10.1107/97809553602060000967.
        

        
      
        Returns
        - kstrain: ndarray, shape (Ngrains, Nrefl)
            Projected strains along the scattering directions.
      
        Method sketch
        - From Reuss compliances s_{11}, s_{12}, s_{44}:
          K = 1 / [3 (s_{11} + 2 s_{12})], μ_k = 1 / s_{44}, ν_k = 1 / [2 (s_{11} - s_{12})],
          r = μ_k / ν_k.
        - Define coefficients (as in the code): α_V, β_V, γ_V and their γ-weighted forms.
        - For each (h, k, l), compute γ = (h^2 k^2 + k^2 l^2 + h^2 l^2)/(h^2 + k^2 + l^2)^2.
          Form the cubic coefficients and select the largest root G.
        - Effective compliances:
          s_{12}^K = 1/(9K) - 1/(6G), s_{11}^K = s_{12}^K + 1/(2G), s_{44}^K = 0.
        - Compute ε^K = S^K σ and project with n = (B1, B2, B3) as in Voigt.
        """

        s11=(self.c11+self.c12)/((self.c11-self.c12)*(self.c11+2*self.c12))#Reuss
        s12=-self.c12/((self.c11-self.c12)*(self.c11+2*self.c12))#Reuss
        s44=1/self.c44
        kk=1/(3*(s11+2*s12))
        muk=1/s44
        nuk=1/(2*(s11-s12))
        mukr=muk/nuk
#         gamzero=1/(3+2/mukr)
        alpv=3/8*(3*kk+4*muk)-muk/5 *(3+2/mukr)
        aptg=-9/2 * muk*(1-1/mukr)
        betv=(3/4)*kk*muk*(1-.1*((6/mukr)+9+(20/mukr)*muk/kk))
        betgv=-9/4 *kk* muk*(1-1/mukr)
        gamv=(-3/4)*kk*nuk*muk
        gamval=gammacal(self.hkl)
        gvalu=gamval
        G=np.zeros([len(gvalu)])
        for j in range(len(gvalu)):
            gcoeff=np.array([1,alpv+aptg*gvalu[j],betv+betgv*gvalu[j],gamv])
            gsolve=np.roots(gcoeff)
            G[j]=gsolve.max()
        ES1=(1/(9*kk))-1/(6*G)
        ES2=1/(G)
        s12k=ES1
        s11k=ES1+ES2/2
        s44k=0
        B1=self.samplec[:,:,0]/self.hklmag
        B2=self.samplec[:,:,1]/self.hklmag
        B3=self.samplec[:,:,2]/self.hklmag
        kstrain=np.zeros([len(self.hkl),len(self.bunge)])
        for i in range(len(self.hkl)):
            smatrix=1e-3*np.array([[s11k[i],s12k[i],s12k[i],0,0,0],[s12k[i],s11k[i],s12k[i],0,0,0],[s12k[i],s12k[i],s11k[i],0,0,0],[0,0,0,s44k,0,0],[0,0,0,0,s44k,0],[0,0,0,0,0,s44k]])
            kroenerstrain=np.dot(smatrix,self.stress)
            kstrain[i,:]=np.power(B1[i,:],2)*kroenerstrain[0,0]+np.power(B2[i,:],2)*kroenerstrain[1,0]+np.power(B3[i,:],2)*kroenerstrain[2,0]+2*B2[i,:]*B3[i,:]*kroenerstrain[3,0]+2*B1[i,:]*B3[i,:]*kroenerstrain[4,0]+2*B1[i,:]*B2[i,:]*kroenerstrain[5,0]# kroener conribution of the strain
        return kstrain.T
class StrainStrainModels:
    """Class strain models
      Parameters
    - bunge: ndarray, shape (Ngrains, 3, 3)
        Orientation matrices (currently unused, kept for symmetry).
    - hkl: ndarray, shape (Nrefl, 3)
        Miller indices (unused here).
    - strain: ndarray, shape (6,) or (6, 1)
        Macroscopic strain in Voigt order: [ε11, ε22, ε33, ε23, ε13, ε12].
    - omega: float
        Vertical angle in degrees.
    - psi: float
        Azimuthal angle in degrees.
    """
     
    
    
    def __init__(self,bunge,hkl,strain,omega,psi):
        """construct the model
        Parameter
        ----------
        bunge : orientation matrices
        hkl :  miller index
        psi:  azimuthal angle in laboratory frame
        omg :  vertical angle  in laboratory frame
        strain : strain matrix"""
        self.bunge=bunge
        self.hkl=hkl 
        self.Es=strain
        self.omega=omega
        self.psi=psi
    def macstrain(self):
        """Compute macroscopic projected strain ε(ω, ψ) and tile over grains/reflections.

        Returns
        - Ematrix: ndarray, shape (Ngrains, Nrefl)
            Matrix filled with the scalar ε(ω, ψ).
    
        Formula
        - With E = [ε11, ε22, ε33, ε23, ε13, ε12] and angles in degrees:
          ε(ω, ψ) =
          ε11 cos^2 ψ sin^2 ω + ε22 sin^2 ψ + ε33 cos^2 ω cos^2 ψ
          + ε23 sin(2ψ) cos ω + ε13 cos^2 ψ sin(2ω) + ε12 sin(2ψ) sin ω.
        - In LaTeX:
          \\varepsilon(\\omega, \\psi) =
          \\varepsilon_{11}\\cos^2\\psi\\sin^2\\omega + \\varepsilon_{22}\\sin^2\\psi
          + \\varepsilon_{33}\\cos^2\\omega\\cos^2\\psi
          + \\varepsilon_{23}\\sin(2\\psi)\\cos\\omega
          + \\varepsilon_{13}\\cos^2\\psi\\sin(2\\omega)
          + \\varepsilon_{12}\\sin(2\\psi)\\sin\\omega.
   """
        E=self.Es[0]* np.power(np.cos(np.radians(self.psi)), 2) * np.power(np.sin(np.radians(self.omega)), 2) + self.Es[1]* np.power(np.sin(np.radians(self.psi)),2) +self.Es[2]* np.power(np.cos(np.radians(self.omega)), 2)* np.power(np.cos(np.radians(self.psi)), 2)+ self.Es[3] * np.sin(2.0 * np.radians(self.psi)) * np.cos(np.radians(self.omega)) + self.Es[4]* np.power(np.cos(
        np.radians(self.psi)),2) * np.sin(2.0 * np.radians(self.omega)) + self.Es[5] * np.sin(2*np.radians(self.psi)) * np.sin(np.radians(self.omega))
        Ematrix=np.zeros([len(self.bunge), len(self.hkl)])
        Ematrix[:,:]=E[0]
        return Ematrix 
        
    
