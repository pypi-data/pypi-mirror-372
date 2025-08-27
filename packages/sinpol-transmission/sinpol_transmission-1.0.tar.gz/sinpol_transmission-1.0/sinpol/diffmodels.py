"""Module to calculate different diffraction and transmission intensity."""

import numpy as np
from numba import float64
from numba.experimental import jitclass

#pylint: disable=R0913
def coth(x):
    """Calculates hyperbolic cotangent.
    Parameters
    - x: array_like
        Real input values.
    
    Returns
    - y: ndarray
        y = coth(x) = 1 / tanh(x) = cosh(x) / sinh(x), element-wise.
    
    Notes
    - Definition in LaTeX:
      coth(x) = \\frac{\\cosh(x)}{\\sinh(x)} = \\frac{1}{\\tanh(x)}.
    - Numerical considerations:
      - At x = 0, the function diverges (division by zero); numpy will return inf with a warning.
      - For very small |x|, coth(x) is large; if desired, clip or handle small arguments explicitly.
    """
    return 1. / np.tanh(x)
scdata=[('r',float64[:]),('q',float64[:]),('p',float64[:]),('s',float64[:]),('b',float64[:])]
@jitclass(scdata)
class DiffModels:
    """This jitclass stores auxiliary parameters r, q, p, s, b (all 1D float64 arrays
of the same length N) and provides methods to compute reflected/transmitted
intensities for the Laue and Bragg cases as in Sears (1997).

Parameters
- r: float64[:]
    Auxiliary dimensionless parameter (Laue/Bragg model).
- q: float64[:]
    Auxiliary dimensionless parameter (Laue/Bragg model).
- p: float64[:]
    Auxiliary dimensionless attenuation-like parameter.
- s: float64[:]
    Auxiliary dimensionless parameter appearing in cosh/sinh terms.
- b: float64[:]
    Prefactor for Bragg-case intensities.

Attributes
- r, q, p, s, b: float64[:]
    Stored arrays, length N (must all have equal length).

Notes
- All methods return 1D arrays of length N.
- This is a Numba jitclass; inputs must be 1D float64 arrays to avoid typing issues.
- The implemented formulas follow Sears (1997) as coded below; see method docstrings.
"""
    
    
    
    
    def __init__(self,r,q,p,s,b):
        """
    Initialize with per-sample arrays.

    Parameters
    - r, q, p, s, b: float64[:]
        1D float64 arrays of equal length N.
    """
        self.r=r
        self.q=q
        self.p=p
        self.s=s
        self.b=b
    def sears_lr(self):
        """Calculates the reflected intensity for the Laue case using the Sears models, 
        see reference V. Sears, Acta Crystallogr., Sect. A: Found. Crystallogr. 53, 35 (1997).
       Returns
       - t: float64[:], shape (N,)
            Element-wise reflected intensity.

        Formula
        - In LaTeX:
            t = \\frac{r\\,e^{-q}}{r\\,\\cosh(r) + p\\,\\sinh(r)}.

       
    """
        t=self.r*np.exp(-self.q)/(self.r*np.cosh(self.r)+self.p*np.sinh(self.r))
        return t
    def sears_lt(self):
        """Calculates the transmitted intensity for the Laue case using the Sears models, 
        see reference V. Sears, Acta Crystallogr., Sect. A: Found. Crystallogr. 53, 35 (1997).
        Returns
    - t: float64[:], shape (N,)
        Element-wise transmitted intensity.

    Formula
    - In LaTeX:
      t = e^{-p}\\,\\Big(\\cosh(s) - \\frac{q}{s}\\,\\sinh(s)\\Big).

   
        
       
        """
        t=np.exp(-self.p)*(np.cosh(self.s)-(self.q/self.s)*np.sinh(self.s))
        return t
    def sears_br(self):
        """Calculates the reflection intensity for the Bragg case using the Sears models, 
        see reference V. Sears, Acta Crystallogr., Sect. A: Found. Crystallogr. 53, 35 (1997).
       
        Returns
   - rr: float64[:], shape (N,)
       Element-wise reflected intensity.

   Formula
   - In LaTeX:
     rr = \\frac{b}{\\dfrac{r}{\\tanh(r)} + p}
         = \\frac{b}{r\\,\\coth(r) + p}. 
       
        """
        rr=self.b/(self.r/np.tanh(self.r)+self.p)
        return rr
    def sears_bt(self):
        """Calculates the transmitted intensity for the Bragg case using the Sears models, 
         see reference V. Sears, Acta Crystallogr., Sect. A: Found. Crystallogr. 53, 35 (1997).
        
        Returns
    - rr: float64[:], shape (N,)
        Element-wise transmitted intensity.

    Formula
    - In LaTeX:
      rr = e^{-p}\\, b\\, \\frac{\\sinh(s)}{s}.
        
        """
        rr=np.exp(-self.p)*self.b*np.sinh(self.s)/self.s
        return rr
    