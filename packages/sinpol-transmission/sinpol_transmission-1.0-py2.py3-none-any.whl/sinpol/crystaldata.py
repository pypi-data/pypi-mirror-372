"""Module to calculate crystal data."""
import sys
from fractions import Fraction as Fr
import numpy as np
from cctbx  import sgtbx
import periodictable as ptbl
from scipy import integrate
import scipy.misc
from elementy import PeriodicTable
from ase.spacegroup import Spacegroup
import diffpy.structure as atm
import re
# pylint: disable=line-too-long
#pylint: disable=C0103

def interlog(xtemp):
    """
    Parameters
    - xtemp: float
        Dimensionless parameter x = θ_D / T.
    
    Returns
    - D1: float
        D_1(x) = (1/x) ∫_0^x t / (e^t − 1) dt.
    
    LaTeX
    - D_1(x) = \\dfrac{1}{x} \\int_0^x \\dfrac{t}{e^t - 1}\\,dt.

    """
    xcal = lambda x: x / (np.exp(-x) - 1)
    xcal2 = integrate.quad(xcal, xtemp, 0)
    return xcal2[0] / xtemp
def bernoulli(n):
    """ Calculates Bernoulli number.
    Parameters
    - n: int
    
    Returns
    - A[0]: fractions.Fraction
        The Bernoulli number A[0].
    """
    A = [0] * (n + 1)
    for m in range(n + 1):
        A[m] = Fr(1, m + 1)
        for j in range(m, 0, -1):
            A[j - 1] = j * (A[j - 1] - A[j])
    return A[0]
def rfunc(x):
    """ Parameters
    - x: float
    
    Returns
    - rval: float
    
    Notes
    - Summation:
      r(x) ≈ Σ_{n=0}^{N-1} [ B_n x^{n-1} / (n! (n + 5/2)) ] + B_{22} x^{21} / (22! (22 + 5/2)).
    - LaTeX:
      r(x) \\approx \\sum_{n=0}^{N-1} \\frac{B_n x^{n-1}}{n!\\,(n + 5/2)} + \\frac{B_{22} x^{21}}{22!\\,(22 + 5/2)}. """
    term = 21
    rarr = np.ndarray(shape=(term, 1), dtype=float)
    for n in range(term):
        rarr[n] = (bernoulli(n) * np.power(x, (n - 1)) / (scipy.special.factorial(n) * (n + 5 / 2))) + bernoulli(
            22) * np.power(x, 21) / (scipy.special.factorial(22) * (22 + 5 / 2))
    rval = np.ndarray.sum(rarr)
    return rval


def cal_energy(wvls):
    """ Convert wsvelenghts into energy 
   Parameters
    - wvls: float or ndarray
        Wavelength(s) in Å.
    
    Returns
    - energ: float or ndarray
        Energy in meV using E = 81.804 / λ^2.
    
    LaTeX
    - E(\\text{meV}) = \\dfrac{81.804}{\\lambda^2(\\text{\\AA})}.
    """
    energ = .081820 / (wvls* wvls)
    return energ
class CrystalData:
    """
    Parameters
    - elm: str
        Either a path to a CIF file (ends with '.cif') or an element symbol (e.g., 'Fe').
    - a, b, c: float, default 3.61
        Lattice parameters in Å (used if not loading a CIF).
    - alpha, beta, gamma: float, default 90
        Lattice angles in degrees (used if not loading a CIF).
    - debye: float, default 345
        Debye temperature θ_D in K (used if not loading a CIF).
    - spg: str, default '229'
        Space group number or symbol (used if not loading a CIF).
    
    Attributes
    - latticearr: ndarray, shape (1, 6)
        [a, b, c, α, β, γ].
    - atmparr: ndarray, shape (Natoms, 3)
        Atomic positions (fractional).
    - neutronics: CrystalData.Neutronics
        Neutron-relevant parameters for the element.
    - nxs: CrystalData.NxsCalculate
        Cross-section calculator bound to neutronics.
    - spg_num: int
    Space group number.

    """
    
    
    def __init__(self, elm,a=3.61,b=3.61,c=3.61,alpha=90,beta=90,gamma=90, debye=345,spg='229'):
        """
        elm : path to cif file 
        """
        if sys.version_info[0] < 3:
            from diffpy.Structure.Parsers import getParser
        else:
            from diffpy.structure.parsers import getParser
        neutronics=np.zeros([9])
        latarr=np.zeros([1,6])
        atmarr=np.empty((0,3),float)
        spg_num=0
        if  ".cif" in elm:
            pty= PeriodicTable()
            self.p = getParser('cif')
            self.pf = self.p.parseFile(elm)
            debytmp=pty.elements[self.pf.element[0]]['debye_temperature']
            neutronics = self.Neutronics(self.pf.element[0],debytmp)
            latarr=np.array([[self.pf.lattice.a,self.pf.lattice.b,self.pf.lattice.c,self.pf.lattice.alpha,self.pf.lattice.beta,self.pf.lattice.gamma]])
            atmp=np.array([self.pf.x,self.pf.y,self.pf.z]).T
            atmarr=np.array([atmp[i] for i in range (len(atmp))])
            spg_num=self.p.spacegroup.number
        else:
            
            if spg.isdigit():
          
                spg_num=int(spg)
            else:
                spg_num=Spacegroup(spg).no
                  
     
            sgi =sgtbx.space_group_info(spg_num)
           
          
            sg=sgi.group()
            av=sgi.symbol_and_number()
            av=re.findall(r'\d+',av)
            aa=int(av[len(av)-1])
            sgt=Spacegroup(aa)
            atmarr=sgt.subtrans
            neutronics = self.Neutronics(elm,debye)
            latarr=np.array([[float(a),float(b),float(c),float(alpha),float(beta),float(gamma)]])
           
        self.latticearr=latarr
        self.atmparr=atmarr
        self.neutronics = neutronics
        self.nxs = self.NxsCalculate(neutronics)
        self.spg_num=spg_num
#     
   
    def latticeparm(self):
        """
        Return the lattice parameters.
    
        Returns
        - lat: ndarray, shape (1, 6)
            [a, b, c, α, β, γ].
        """
        return self.latticearr

    def atmposition(self):
        """
        Return the fractional atomic positions.
    
        Returns
        - pos: ndarray, shape (Natoms, 3)
            [x, y, z] fractional coordinates.
        """
        return self.atmparr
    def hklmaker(self,amax,cutval):
        """
       Generate allowed (h, k, l) triplets filtered by space-group absences and norm cutoff.
    
       Parameters
       - amax: int
           Generate indices in range [−amax, ..., +amax] for each of h, k, l.
       - cutval: float
           Keep triplets with h^2 + k^2 + l^2 <= cutval.
    
       Returns
       - hklnb: ndarray, shape (N, 3)
           Allowed reflections after filtering.
    
       Notes
       - Space-group systematic absences are tested via cctbx.sgtbx.
       """
        max_hkl=amax
        min_hkl=-1*max_hkl
        sgi =sgtbx.space_group_info(self.spg_num)
        sg=sgi.group()
        harr=[]
        karr=[]
        larr=[]
        for h in range(min_hkl,(max_hkl+1)):
            for k in range(min_hkl,(max_hkl+1)):
                for l in range(min_hkl,(max_hkl+1)):
                    if sg.is_sys_absent((h,k,l)) is not True:
                        if  h==0 and k==0 and l==0:
                            continue
                        harr.append(h)
                        karr.append(k)
                        larr.append(l)
        hkln=np.ndarray(shape=(len(harr),3), dtype=int)
        for j in range (len(harr)):
            hkln[j][0]=harr[j]
            hkln[j][1]=karr[j]
            hkln[j][2]=larr[j]
        hklnb=self.hklnbuilder(hkln,cutval)
        return hklnb
    def hklnbuilder(self,hkln,cutval):
        """
           Filter a list of hkl by Euclidean norm.
        
           Parameters
           - hkln: ndarray, shape (M, 3)
           - cutval: float
        
           Returns
           - hklf: ndarray, shape (N, 3)
               Rows with h^2 + k^2 + l^2 <= cutval.
        
           LaTeX
           - \\{(h,k,l) : h^2 + k^2 + l^2 \\le \\text{cutval}\\}.
           """
        hklnsum=np.zeros([len(hkln)])
        for j in range (len(hkln)):
            hklnsum[j]=(np.power(hkln[j,0],2)+np.power(hkln[j,1],2)+np.power(hkln[j,2],2))
        hklna= np.where(hklnsum<=cutval)
        return hkln[hklna[0]]
    def cstructure(self,amax,cutval):
        """
        Bundle lattice, atomic positions, and filtered hkl.
    
        Parameters
        - amax: int
        - cutval: float
    
        Returns
        - arr: object ndarray, shape (3,)
            [latticearr, atmparr, hklnb].
        """
        return np.array([self.latticeparm(),self.atmposition(),self.hklmaker(amax,cutval)],dtype=object)
    class Neutronics:
        """
           Neutronics parameters for a single element.
        
           Parameters
           - elem: str
               Chemical symbol (e.g., 'Fe').
           - tmp: float
               Debye temperature θ_D in K.
        
           Attributes
           - ns: periodictable neutron data object
           - abs: float
               Absorption cross-section (bound) in barns.
           - C1: float
               Absorption coefficient scaled with sqrt(0.0253 eV) (unit-consistent for use with meV).
           - inc, coh, xsbound, xsfree: float
               Incoherent, coherent, bound total, and free-atom cross-sections (barns).
           - b: float
               Coherent scattering length b_c in 1e-5 Å.
           - debye: float
               Debye temperature θ_D (K).
           - xtemp: float
               Dimensionless x = θ_D / T with T ≈ 293.15 K (ambient).
           - atnum, mass, density: float
               Atomic number, mass (g/mol), density (g/cm^3).
           - N_density: float
               Number density in Å^−3 (conversion used: 1e-24 cm^3/Å^3).
           - Bzero, Btemp, C2: float
               Debye–Waller related parameters.
        
           Notes
           - Btemp = 4 B0 D_1(x) / x, with D_1 from interlog().
           - Ensure unit consistency when combining with energies in meV.
           """
        def __init__(self, elem,tmp):
            """
            Returns the crystal neutronics information
            elm : path to cif file 
            """
            self.pty= PeriodicTable()
            self.ns = getattr(ptbl, elem).neutron # neutron scattering lengths, cross sections etc
            self.abs=self.ns.absorption*1e-8
            self.C1=self.abs*np.sqrt(.0253)
            self.inc=self.ns.incoherent*1e-8
            self.coh=self.ns.coherent*1e-8
            self.xsbound=self.inc+self.coh
            self.b=self.ns.b_c*1e-5
            self.debye=tmp #self.pty.elements[elem]['debye_temperature']
            self.xtemp=self.debye/293.15
            self.atnum=self.pty.elements[elem]['atomic_number']
            self.C2=np.round(4.27*np.exp(self.atnum/61))
            self.Bzero=float(2873.0/(self.atnum *self.debye))
            self.Btemp=4.0*self.Bzero*float(interlog(self.xtemp))/self.xtemp
            self.xsfree=np.power(self.atnum/(self.atnum +1),2)*self.xsbound
            self.mass=self.pty.elements[elem]['mass']
            self.density=self.pty.elements[elem]['density']
            self.N_density=1e-24*float(self.density) * 6.02E23 / self.mass
            self.dat=np.array([self.b,self.abs,self.coh,self.inc,self.xsbound,self.N_density,self.mass,self.debye,self.xtemp])
        
    class NxsCalculate:
        """
        Neutron cross-section calculators (single-phonon TDS, multi-phonon TDS, absorption).
    
        Parameters
        - ntni: CrystalData.Neutronics
            Neutronic parameters.
    
        Methods
        - nxs_tdssp(wvls): single-phonon TDS, meV-based, see Freund (1983).
        - nxs_tdsmp(wvls): multi-phonon TDS.
        - nxs_absorption(wvls): absorption cross-section, 1/√E dependence.
        """


        def __init__(self, ntni):
            """
            ntni : crystal neutronic object 
            """
            self.crysdat=ntni
        def nxs_tdssp(self,wvls):
            """
               Single-phonon thermal diffuse scattering cross section.
        
               Parameters
               - wvls: float or ndarray
                   Wavelength(s) in Å.
        
               Returns
               - xs: float or ndarray
                   Cross-section in barns.
        
               Formula
               - For x <= 6: r(x) = rfunc(x), else r(x) = 3.3 x^{−3.5}.
               - σ_TDS^(1) ∝ [σ_abs / (36 Z)] √θ_D / √E × r(x),
                 where E = 81.804 / λ^2 (meV).
        
               LaTeX
               - \\sigma^{(1)}_{\\mathrm{TDS}} \\propto
                 \\frac{\\sigma_{\\mathrm{abs}}}{36 Z} \\frac{\\sqrt{\\theta_D}}{\\sqrt{E}}\\, r(x).
               """
            if self.crysdat.xtemp <= 6:
                rre = rfunc(self.crysdat.xtemp)
            else:
                rre = 3.3 * np.power(self.crysdat.xtemp, -3.5)
            tdssph1 = (self.crysdat.abs / (36 * self.crysdat.atnum) * np.sqrt(self.crysdat.debye) / np.sqrt((cal_energy(wvls)))) * rre
            return tdssph1
        def nxs_tdsmp(self,wvls):
            """
            Multi-phonon thermal diffuse scattering cross section.
    
            Parameters
            - wvls: float or ndarray
                Wavelength(s) in Å.
    
            Returns
            - xs: float or ndarray
                Cross-section in barns.
    
            Formula
            - σ_TDS^(mp) = σ_free × [1 − exp(−(B0 + B_T) C2 E)],
              with E in meV.
    
            LaTeX
            - \\sigma^{(mp)}_{\\mathrm{TDS}} = \\sigma_{\\mathrm{free}}
              \\left[1 - e^{-(B_0 + B_T) C_2 E}\\right].
            """
            tdsm = self.crysdat.xsfree* (1 - np.exp(-1 * (self.crysdat.Bzero + self.crysdat.Btemp) * self.crysdat.C2 * cal_energy(wvls)))
            return tdsm
        def nxs_absorption(self,wvls):
            """
            Absorption cross section, 1/√E dependence.
    
            Parameters
            - wvls: float or ndarray
                Wavelength(s) in Å.
    
            Returns
            - xs: float or ndarray
                Cross-section in barns.
    
            Formula
            - σ_abs(E) = C1 / √E, with E in meV.
    
            LaTeX
            - \\sigma_{\\mathrm{abs}}(E) = \\dfrac{C_1}{\\sqrt{E}}.
            """
            val = self.crysdat.C1 / (np.sqrt(cal_energy(wvls)))
            return val
