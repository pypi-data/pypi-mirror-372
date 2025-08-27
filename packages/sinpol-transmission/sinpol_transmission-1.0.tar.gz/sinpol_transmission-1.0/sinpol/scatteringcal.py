"""Module to calculate Neutran transmission intensity."""
import math as ma
import threading
from numba import numba as nb, jit,njit, float64,int64
from numba import cfunc
from numba.types import intc, CPointer
from NumbaQuadpack import quadpack_sig, dqags
from scipy import LowLevelCallable
import numpy as np
from sinpol.diffmodels import DiffModels as dm
import matplotlib.pyplot as plt
# pylint: disable=line-too-long

#pylint: disable=E1133
@jit(nopython=True)
def volume(a, b, c, alp, bet, gam):
    """Calculates Volume.
    Parameters
    ------------
    - a, b, c: float
    Lattice constants in Å.
    - alp, bet, gam: float
    Unit-cell angles in degrees (α, β, γ respectively).

    Returns
    ----------
    - vol: float
    Unit cell volume in Å^3.
    
    Notes
    ---------------
    - The formula used is:
    V = a b c sqrt(1 - cos^2 α - cos^2 β - cos^2 γ + 2 cos α cos β cos γ).
    All cosines are evaluated with angles in radians.

    """
    thetsqrtv = ma.pow(ma.cos(ma.radians(alp)), 2) + ma.pow(ma.cos(ma.radians(bet)), 2) + ma.pow(
        ma.cos(ma.radians(gam)), 2) - 2 * ma.cos(ma.radians(alp)) * ma.cos(ma.radians(bet)) * ma.cos(ma.radians(gam))
    vol = a * b * c * ma.sqrt(1 - thetsqrtv)
    return vol
def jit_integrand_function(integrand_function):
    
    """ Calculate integrand

    Parameters
    ---------
    - integrand_function: callable
     A function with signature f(x0, x1) -> float that is JIT-compilable in nopython mode.

    Returns
    --------
    - llc: scipy.LowLevelCallable
    A low-level callable suitable for SciPy Quadpack interfaces.

    Notes
    ---------
    - The wrapper expects the integrand to read two doubles from the array x and return a double.
    - This helper is useful for multidimensional integrals driven by low-level quadrature kernels.
    
    """
    jitted_function = nb.jit(integrand_function, nopython=True)

    @cfunc(float64(intc, CPointer(float64)))
    def wrapped(n,x):
        """ Calculate integrand"""
        return jitted_function(x[0],x[1])
    return LowLevelCallable(wrapped.ctypes)
@nb.cfunc(quadpack_sig)
def integrand(x,*arg):
    """ Calculate integrand
    Parameters
    ----------
    - x: float
    Integration variable (Numba C callback signature).
    - *arg: tuple
    Unused; present for signature compatibility.

    Returns
    ----------
    - float
    Value of x / (exp(-x) - 1).

    Notes
    ----------
    - This implements f(x) = x / (e^{-x} - 1), a standard Bose-Einstein integral kernel.
    
    """
    return x / (np.exp(-x) - 1)
xc1= integrand.address
@njit
def interlog(xtemp):
    """ Calculate integrand
    Parameters
    -----------
    - xtemp: float
        Upper limit of the integration.
    
    Returns
    - float
        interlog(xtemp) = I(xtemp) / xtemp, where I(xtemp) is dqags(integrand, 0, xtemp)[0].
    
    Notes
    ----------
    - integrand is defined above as x / (exp(-x) - 1).
    - This structure commonly appears in Debye model thermodynamic integrals.
    """
    

    xcal2=dqags(xc1,xtemp,0)
    return xcal2[0] / xtemp
@jit(nopython=True)
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
def nb_multithread(func, numthreads):
    """
    Run the given function inside *numthreads* threads, splitting its
    arguments into equal-sized chunks.
    
    Parameters
    ----------
    - func: callable
        Function to execute as func(result_chunk, *chunked_args). It must write into result_chunk.
    - numthreads: int
        Number of threads.
    
    Returns
    ----------
    - func_nb: callable
        Function that accepts arrays as its first positional argument, partitions the inputs into
        numthreads chunks, and returns a result array of the same length.
    
    Notes
    ----------
    - This uses Python threading to parallelize over chunks at a coarse level. Inside each thread,
      Numba JIT can parallelize further (e.g., with prange) independently.
    - The first argument is assumed to be a 1D array-like whose length defines the chunking.
    - The wrapper allocates result and passes it as the first argument into func.
    """
    def func_nb(*args):
        """
        Run the given function inside *numthreads* threads, splitting its
        arguments into equal-sized chunks.
        """
        length = len(args[0])
        result = np.empty(length, dtype=np.float64)
        args = (result,) + args
        chunklen = (length + numthreads - 1) // numthreads
        # Create argument tuples for each input chunk
        chunks = [[arg[i * chunklen:(i + 1) * chunklen] for arg in args]
                  for i in range(numthreads)]
        # Spawn one thread per chunk
        threads = [threading.Thread(target=func, args=chunk)
                   for chunk in chunks]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        return result
    return func_nb

@jit(nopython=True)
def gaussian(x, mu, s):
    """  Calculate gaussian distribution
    Parameters
    ----------
    - x: array_like
        Points at which to evaluate.
    - mu: array_like or float
        Mean.
    - s: array_like or float
        Standard deviation (must be positive).
    
    Returns
    ----------
    - gs: ndarray
        Values of the Gaussian  at x.
    
    Notes
    ----------
    - The Gaussian is:
      g(x) = (1 / sqrt(2 \\pi s^2)) \\exp\\left( -\\frac{(x - \\mu)^2}{2 s^2} \\right).
    """
    gs = 1 / np.power((2 * np.pi * np.power(s, 2)),.5) * np.exp(-np.power(x - mu, 2) / (2 * np.power(s, 2)))
#     print x
    return gs
@jit(nopython=True)
def q_cal(lamb, fs, nc, gangle):
    """ Calculate Q value 
    Parameters
    ----------
    - lamb: array_like
        Wavelength(s) in Å.
    - fs: array_like
        Structure factor squared (|F|^2) in appropriate units.
    - nc: float
        Number density or normalization constant (context-dependent).
    - gangle: array_like
        Bragg angle θ in radians.
    
    Returns
    ----------
    - Q: ndarray
        Pre-factor with proportionality Q ∝ λ^3 |F|^2 n_c^2 / sin(2θ).
    
    Notes
    ----------
    - The implemented expression is:
      Q = (λ^3 fs n_c^2) / sin(2 θ).
    - Inputs are broadcast as needed.
    """
    den = np.sin(2 * gangle)
    aval=np.power(lamb, 3) * fs * np.power(nc, 2)
    val=aval/den
    return val
@jit(nopython=True)
def fsquare(h, k, l, atp, atpossize, w, b_coh):
    """ Calculate square of strucutre factor
    Parameters
    ----------
    - h, k, l: array_like
        Miller indices for reflections (same shape).
    - atp: ndarray, shape (Natoms, 3)
        Fractional atomic positions in the unit cell.
    - atpossize: int
        Number of atoms Natoms; should equal len(atp).
    - w: array_like
        Debye–Waller exponent per reflection (same shape as h/k/l).
    - b_coh: float
        Coherent scattering length in fm (or compatible units).
    
    Returns
    ----------
    - fsq: ndarray
        |F_{hkl}|^2 for each reflection, same shape as h/k/l.
    
    Notes
    ----------
    - The structure factor is:
      F_{hkl} = b_coh \\sum_{j=1}^{N} \\exp\\left(2\\pi i (h x_j + k y_j + l z_j)\\right) \\exp(-W_{hkl})
      and we return |F_{hkl}|^2.
    """
    debw = np.exp(-2 * w)
    fsq=np.empty((len(l)))
    for i in nb.prange(len(l)):
        cos_exp = 0
        sin_exp = 0
        for atm in range(atpossize):
            exp = 2.0 * np.pi * (h[i]  * atp[atm][0] + k[i]  * atp[atm][1] + l[i] * atp[atm][2])
            cos_exp += np.cos(exp)
            sin_exp += np.sin(exp)
            fsq[i] = (np.power(cos_exp, 2) + np.power(sin_exp, 2)) * np.power(b_coh, 2)*debw[i]
    return fsq
@njit('(float64[:,:,:], float64[:,:])',parallel=True,fastmath=True)
def tintense(I,b):
    """ Calculate transmission intensity in area of low to no absorption
    Parameters
    ----------
    - I: ndarray, shape (Ngrains, Nlambda, Nhkl)
        Per-grain, per-ray, per-reflection transmission contributions in [0, 1].
    - b: ndarray, shape (Ngrains, Nlambda)
        Background attenuation factor per grain and ray, typically exp(-mu * pathlength).
    
    Returns
    ----------
    - rintense: ndarray, shape (Ngrains, Nrays)
        Combined transmission per grain and ray.
    
    Notes
    ----------
    - For each grain i and ray j:
      1) Replace I[i, j, k] by I[i, j, k] / b[i, j] where I != 1 (i.e., nontrivial reflection loss).
      2) Convert to loss ib = 1 - I_corr and sum over reflections.
      3) Normalize as 1 / (1 + sum(losses)).
      This is a heuristic aggregation that avoids double counting and caps the transmission.
    """
    r,c,t=I.shape
    l,n=b.shape
    rintense=np.empty((r,c), dtype=np.float64)
    for i in range(l):
        for j in range(n):
            bj=b[i,j]
        
            iA=I[i,j,:]
            mnone=(iA!=1)
            ciA=np.where(mnone, iA / bj, iA)
            ib=1.0-ciA
            isum=np.sum(ib)
            ic=isum+1.0
            ifinal=1.0/ic
            rintense[i,j]=ifinal
    return rintense
@njit('(float64[:], float64[:,:])', parallel=True,fastmath=True)
def calsin(w,l):
    """ Calculate theta Bragg
    Parameters
    ----------
    - w: ndarray, shape (Nλ,)
        Wavelength grid in Å.
    - l: ndarray, shape (Nrefl, Ngrains)
        Interplanar spacings d_{hkl} in Å.
    
    Returns
    ----------
    - data: ndarray, shape (Nrefl, Nλ, Ngrains)
        θ_{hkl}(λ) = arcsin(λ / (2 d_{hkl})) in radians.
    
    Notes
    ----------
    - This computes θ, not 2θ.
    - Results are clipped implicitly by arcsin domain; ensure λ ≤ 2 d_{hkl}.
    """
    
    o,hh=l.shape
    e=len(w)
    # print(w.shape,l.shape)
    data = np.empty((e, o, hh))
    for i in nb.prange(e):
        for j in range(o):
            for k  in range(hh):
                data[i,j,k]=ma.asin(w[i]/(2.0*l[j,k]))
                # print( data[i,j,k])
    data=np.swapaxes(data,0,1)
    return data
@njit('(float64[:,:], float64[:,:])',parallel=True,fastmath=True)
def sampcal(s,h):
    """ Calculate diffraction cosine angle
    Parameters
    ----------
    - s: ndarray, shape (Nrefl, Ngrains)
    - h: ndarray, shape (Nrefl, Ngrains)
    
    Returns
    ----------
    - dat: ndarray, shape (Nrefl, Ngrains)
        Element-wise s[i, j] / h[i, j].
    """

    su,hu=s.shape
    dat=np.empty((su,hu))
    for i in nb.prange(su):
        for j in range (hu):
            dat[i,j]=s[i,j]/h[i,j]
    return dat
@njit('(float64[:,:],int64[:,:])',fastmath=True,parallel=True)
def backgrd(bm,hk):
#     print(bm.shape,hk.shape)
    """Distribute background over all grains   
    Parameters
    ----------
    - bm: ndarray, shape (Nrays, Ngrains)
        Background per ray and grain.
    - hk: ndarray, shape (Nrefl, 3)
        hkl array; only its length is used.
    
    Returns
    ----------
    - br: ndarray, shape (Nrays, Ngrains, Nrefl)
        Background repeated across reflections.
    """
    bm=np.swapaxes(bm,0,1)
#     print(bm.shape,hk.shape)
    t,l=bm.shape
    hm,klm=hk.shape
    br=np.empty((t,l,hm))
    for i in nb.prange(t):
        for j in range (l):
            for q in range(hm):
                br[i,j,q]=bm[i,j]
    br=np.swapaxes(br,0,1)
    return  br
@njit(fastmath=True,parallel=True)
def gamasin(gam):
    """ Calculate theta Bragg
    Parameters
    ----------
    - gam: ndarray, shape (Nrefl, Ngrains)
    
    Returns
    ----------
    - br: ndarray, shape (Nrefl, Ngrains)
        arcsin(gam) in radians.
    
    Notes
    ----------
    - Ensure inputs are in [-1, 1].
    """
    t,l=gam.shape
    br=np.empty((t,l))
    for j in nb.prange(t):
        for k in range(l):
            br[j,k]=np.arcsin(gam[j,k])
    return  br
@nb.njit('(float64[:,:,:],float64[:,:,:],float64[:,:,:])',fastmath=True,parallel=True)
def findidx(tmin,tcal,tmax):
    """ Find the indices necessary needed to carry  diffraction and transmission calculation
    Parameters
    - tmin, tcal, tmax: ndarray, shape (Nrefl, Nλ, Ngrains)
        Lower bound, trial value, and upper bound arrays.
    
    Returns
    - qb: ndarray, shape (N, 3), dtype int64
        Rows of indices (i_reflection, j_lambda, k_grain) that satisfy the condition.
    """
    qa=np.where(np.logical_and(tmin<=tcal,tcal<tmax))
    qb=np.empty((len(qa[0]),3),dtype=int64)
    for i in nb.prange (len(qa[0])):
        qb[i,0]=qa[0][i]
        qb[i,1]=qa[1][i]
        qb[i,2]=qa[2][i]
    return qb
@njit('(int64[:,:],float64[:,:,:])',fastmath=True)
def numba_dot(A, B):
    """ dot product  in numba 
    Parameters
    ----------
    - A: ndarray, shape (m, n)
    - B: ndarray, shape (n, u, p)
    
    Returns
    ----------
    - C: ndarray, shape (m, u, p)
        C[i, g, k] = sum_j A[i, j] * B[j, g, k].
    """
    m, n = A.shape
    u,t,p = B.shape
    C = np.zeros((m,u,p))
    for i in range(m):
        for g in range(u):
            for j in range(n):
                for k in range(p):
                    C[i, k] += A[i, j] * B[j,g, k]
    return C
@njit(fastmath=True,parallel=True)
def numba_dot2(A, B):
    """ dot product  in numba
    Parameters
    ----------
    - A: ndarray, shape (m, n)
    - B: ndarray, shape (n, t, p)
    
    Returns
    ----------
    - C: ndarray, shape (n, t, p)
        For each i in [0, t), C[:, i, :] = A @ B[:, i, :].
    """
    
  
    m, n = A.shape
    u,t,p = B.shape
    C = np.zeros((u,t,p))
    for i in range(t):
        C[:,i,:]=np.dot(A,B[:,i,:])
    return C
@njit('(float64[:],int64)',fastmath=True,parallel=True)
def mrepeat(mos,hk):
    """Repeat mosaic distribitution across hkl matrix, for calculation
    Parameters
    ----------
    - mos: ndarray, shape (Ngrains,)
        Mosaic standard deviations (radians) per grain.
    - hk: int
        Number of reflections Nrefl.
    
    Returns
    ----------
    - br: ndarray, shape (Ngrains, Nrefl)
        Tiled mosaic spreads.
    """
    br=np.empty((len(mos),hk))
    for i in nb.prange(len(mos)):
        for j in nb.prange (hk):
            br[i,j]=mos[i]
    return  br
@njit('(int64,float64[:])',fastmath=True,parallel=True)
def lrepeat(b,lat):
    """   Repeat lattice spacing across grain  distribution calculation
    Parameters
    ----------
    - b: int
        Number of grains.
    - lat: ndarray, shape (Nrefl,)
        d_{hkl} values.
    
    Returns
    ----------
    - br: ndarray, shape (Ngrains, Nrefl)
        Tiled d-spacings.
    """
    br=np.empty((b,len(lat)))
    for i in nb.prange(b):
        for j in range (len(lat)):
            br[i,j]=lat[j]
    return  br
@nb.njit('(float64[:,:],int64)',fastmath=True,parallel=True)
def trepeat(theta,l):
    """ Rewrite as  3d array dependent on number of grains, length of wavelength bin,  and number of lattice planes 
    Parameters
    ----------
    - theta: ndarray, shape (Nrefl, Ngrains)
        Base angles (e.g., θ_min or θ_max).
    - l: int
        Number of wavelength bins Nλ.
    
    Returns
    ----------
    - br: ndarray, shape (Nrefl, Nλ, Ngrains)
        θ repeated along the wavelength axis.
   """
    a,b=theta.shape
    br=np.empty((a,l,b))
    for i in nb.prange(a):
        for j in nb.prange (l):
            for k in nb.prange (b):
                br[i,j,k]=theta[i,k]
    return  br
@nb.njit(fastmath=True,parallel=True)
def newlamb(lam,lmin):
    """  Set the minimum value for lambda to be used in transmission calculation
    Parameters
    ----------
    - lam: ndarray, shape (Nrefl, Ngrains)
        Wavelengths.
    - lmin: float
        Minimum allowed wavelength.
    
    Returns
    ----------
    - br: ndarray, shape (Nrefl, Ngrains)
        Element-wise max(lam, lmin).
    """
    
    a,b=lam.shape
    br=np.empty((a,b))
    for i in nb.prange(a):
        for j in nb.prange (b):
            if lam[i,j]>lmin:
                br[i,j]=lam[i,j]
            else:
                br[i,j]=lmin
    return  br
#@njit(('float64[:,:],float64,float64[:],float64[:],int64[:,:],float64[:],float64[:,:],float64[:],float64[:],float64[:]'))
def scatvar(bunge,omg,gs,mosaic,hkl,lattice,atp,xtal,strain, wvltg):
    """ Calculate all parameters needed to calculate transmission and diffraction intensities
    Parameters
    ----------
    - bunge: ndarray, shape (Ngrains, 3, 3)
        Orientation matrix per grain (Bunge/Euler rotation or equivalent).
    - omg: float
        Sample rotation angle around y-axis in radians (beam rotation matrix uses this).
    - gs: ndarray, shape (Ngrains,)
        Path length or geometric scale per grain used for attenuation.
    - mosaic: ndarray, shape (Ngrains,)
        Mosaic spread (radians) per grain (Gaussian σ).
    - hkl: ndarray, shape (Nrefl, 3)
        Miller indices.
    - lattice: ndarray, shape (1, 6)
        [a, b, c, α, β, γ], with angles in degrees.
    - atp: ndarray, shape (Natoms, 3)
        Fractional atomic positions.
    - xtal: ndarray
        Material constants; indices used elsewhere: xtal[0], xtal[5], xtal[6], xtal[7], xtal[8].
        See _transmission for context.
    - strain: ndarray, shape (Ngrains,)
        Optional strain per grain (currently not applied; code has a placeholder).
    - wvltg: ndarray, shape (Nλ,)
        Wavelength grid in Å.
    
    Returns
    ----------
    - mosaica: ndarray, shape (Nrefl, Ngrains)
        Mosaic spread tiled over reflections.
    - gammazero: float
        cos(ω), used as a normalization constant.
    - lmbda: ndarray, shape (Nrefl, Ngrains)
        Effective wavelengths for each reflection/grain (clipped to min(wvltg)).
    - thetahkl: ndarray, shape (Nrefl, Ngrains)
        Bragg half-angles θ_{hkl} = arcsin(γ).
    - thetai: ndarray, shape (Nrefl, Nλ, Ngrains)
        θ(λ) computed from d_{hkl} via arcsin(λ / (2 d)).
    - qa: ndarray, shape (N, 3)
        Integer indices where θ_min ≤ θ(λ) < θ_max.
    - sampz: ndarray, shape (Nrefl, Ngrains)
        Dimensionless geometric factor = samplec[:, :, 2] / |G|, where |G| ∝ 1/d.
    
    Notes
    ----------
    - Builds the beam rotation matrix around y-axis:
      R_y(ω) = [[cos ω, 0, -sin ω], [0, 1, 0], [sin ω, 0, cos ω]].
    - d_{hkl} is computed from dhkl() and tiled across grains.
    - θ_min/max = θ_{hkl} ± 5 σ_mosaic.
    """
        
    
    samplec=np.empty((len(hkl),bunge.shape[0],bunge.shape[1]))
    stbm=np.zeros((len(hkl),bunge.shape[0],bunge.shape[1]))
    mosaica=mrepeat(mosaic, len(hkl))
    beammatrix=np.empty((3,3))
    samplec=np.dot(hkl,bunge)
    lathkl=dhkl(lattice[0,0],lattice[0,1],lattice[0,2],lattice[0,3],lattice[0,4],lattice[0,5],hkl[:,0],hkl[:,1],hkl[:,2],volume(lattice[0,0],lattice[0,1],lattice[0,2],lattice[0,3],lattice[0,4],lattice[0,5]))
    lathkl=lrepeat(len(bunge),lathkl)
    hklmag=float(lattice[0,2])/lathkl
    hklmag=np.reshape(hklmag,(len(hkl),len(bunge)))
    beammatrix[0,0]=np.cos(omg)
    beammatrix[0,1]=0
    beammatrix[0,2]=-np.sin(omg)
    beammatrix[1,0]=0
    beammatrix[1,1]=1
    beammatrix[1,2]=0
    beammatrix[2,0]=np.sin(omg)
    beammatrix[2,1]=0
    beammatrix[2,2]=np.cos(omg)
    gammazero=np.cos(omg)
    stbm=np.dot(samplec,beammatrix)
    gamma=stbm[:,:,2].T*lathkl/lattice[0,2]
    lathkln=lathkl#*strain+lathkl
    lmbda= 2.0*lathkln*gamma
    thetahkl=gamasin(gamma)
    thetamax=thetahkl+5*mosaica
    thetamin=thetahkl-5*mosaica
    lmbda=newlamb(lmbda,wvltg.min())
    thetai=calsin(wvltg,lathkln)
    sampz=sampcal(samplec[:,:,2],hklmag)
    sampz=np.swapaxes(sampz,0,1)
    qa=findidx(trepeat(thetamin,len(wvltg)), thetai, trepeat(thetamax,len(wvltg)))
    bankdec=np.sin (2.0*omg)*(np.power(samplec[:,:,0]/hklmag ,2)-np.power(samplec[:,:,2]/hklmag ,2))-2.0*np.cos(2.0*omg)*samplec[:,:,0]/hklmag *samplec[:,:,2]/hklmag
    detecV=np.abs((samplec[:,:,1].T/hklmag[:,0])*np.sin(thetahkl))  # Vertical length of detector
    detecH=np.cos(2.0*thetahkl)  # horizontal lenght of detector
    return mosaica,gammazero,lmbda,thetahkl,thetai,qa,sampz
#@njit(('float64[:,:,:],float64[:,:],float64[:,:],float64,int64[:,:],float64[:],float64[:,:],float64[:],float64[:],float64[:],float64[:],float64[:,:],float64[:]'),fastmath=True)
def _transmission(b,gs,mosaic,omg,hkl,lattice,atp,xtal,nxsa,nxsts,nxstm,strain,wvltg ):
    
    """ Calculate  neutron transmission intensity over a plate
    Parameters
    ----------
    - b: list of ndarrays
        Partitioned orientation arrays; each element has shape (Ngrains_j, 3, 3).
    - gs: list of ndarrays
        Partitioned per-grain path lengths; gs[j] shape (Ngrains_j,).
    - mosaic: list of ndarrays
        Partitioned per-grain mosaic spreads (radians); shape (Ngrains_j,).
    - omg: float
        Sample rotation angle ω in radians.
    - hkl: ndarray, shape (Nrefl, 3)
        Miller indices.
    - lattice: ndarray, shape (1, 6)
        [a, b, c, α, β, γ] with angles in degrees.
    - atp: ndarray, shape (Natoms, 3)
        Fractional atomic positions.
    - xtal: ndarray
        Material constants used as:
          - xtal[0]: coherent scattering length b_coh (units consistent with fsquare()).
          - xtal[5]: linear attenuation coefficient per (nxsa + nxsts + nxstm) unit.
          - xtal[6], xtal[7], xtal[8]: constants used in Debye–Waller evaluation (see wval).
        Ensure physical consistency with the units of h, kb, and neutron mass used below.
    - nxsa, nxsts, nxstm: float
        Multiplicative factors for absorption/scattering (application-specific).
    - strain: list of ndarrays
        Partitioned per-grain strain values (currently not applied; placeholder).
    - wvltg: ndarray, shape (Nλ,)
        Wavelength grid in Å.
    
    Returns
    ----------
    - trans_mean: ndarray, shape (Nλ,)
        Mean transmission over partitions and grains.
    
    Algorithm sketch
    - For each partition j:
      - Compute mosaica, gammazero, λ_{eff}, θ_{hkl}, θ(λ), valid indices qa, and geometry via scatvar().
      - Compute Debye–Waller factor parameter wval via:
        wval ∝ (sin^2 θ / λ^2) [interlog(xtal[8]) + 0.25]
        with a prefactor 9e36 * (6 h^2 / (xtal[7] kb xtal[6] m_n c^2)), using h in eV·s and kb in eV/K.
      - Compute |F|^2 with fsquare(), then Q via Q_cal().
      - Compute Gaussian mosaic weights at θ(λ) relative to θ_{hkl}.
      - Compute effective path factors and use sears_lr/lt branches from sinpol.diffmodels to get
        per-reflection transmissions transtemp.
      - Aggregate with tintense() and include background attenuation backmu.
    - Average over partitions.
    
    Important
    ----------
    - Ensure ω, θ are in radians.
    - Make sure array shapes align:
      - gs[j] has length Ngrains_j and is indexed by qa[:, 0].
      - θ_{hkl}, λ_{eff} are indexed by (qa[:, 0], qa[:, 2]).
    - Handle potential divisions carefully: clamp gamhkl to avoid zero divisions.
    
    References
    ----------
    - Sears, V.F., Neutron scattering lengths and cross sections  Acta Crystallogr., Sect. A: Found. Crystallogr. 53, 35 (1997).
    - Debye model integrals for thermal motion and DW factors.
    """ 
    
    
    
    trans=np.ones((len(b),len(wvltg)))
    hplanck = 4.135E-15 # evslsvi
    kb = 8.617E-5
    for j in range(len(b)):
    
        mosaica,gammazero,lmbda,thetahkl,thetai,qa,sampz=scatvar(b[j],omg,gs[j],mosaic[j],hkl,lattice,atp,xtal,strain[j], wvltg)
        mu=xtal[5]*(nxsa+nxsts+nxstm)*float(len(b[j]))
        transtemp=np.ones((len(b[j]),len(wvltg),len(hkl)))
        Trans=np.ones(shape=(len(b[j]),len(wvltg)), dtype=float)
        backmu=np.exp(-mu*gs[j][:,np.newaxis])

        wval=9.0e36 *(6.0 * np.power(float(hplanck), 2) / ( float(xtal[7]) * float(kb) * float(xtal[6])* 939.565 * 1E6 )) * np.power(np.sin(thetahkl[qa[:,0],qa[:,2]]), 2)/(np.power(lmbda[qa[:,0],qa[:,2]], 2)) * (float(interlog(xtal[8])) + 0.25)
        fsq=fsquare(hkl[qa[:,2],0],hkl[qa[:,2],1],hkl[qa[:,2],2],atp,len(atp),wval,xtal[0])
        Q=q_cal(lmbda[qa[:,0],qa[:,2]], fsq,1.0/volume(lattice[0,0],lattice[0,1],lattice[0,2],lattice[0,3],lattice[0,4],lattice[0,5]),thetahkl[qa[:,0],qa[:,2]])
        mos=gaussian(thetai[qa[:,0],qa[:,1],qa[:,2]],thetahkl[qa[:,0],qa[:,2]],mosaica[qa[:,0],qa[:,2]])
        gamhkl=np.cos(omg)-2.0*np.sin(thetahkl[qa[:,0],qa[:,2]])*sampz[qa[:,0],qa[:,2]]
        gamhkl[np.abs(gamhkl)<.1]=.1
        sigma=Q*mos
        bn1=sigma*gs[j][qa[:,0]]
        bnn1=bn1/gammazero
        cn1=np.array(np.abs(gammazero/gamhkl))
        an1=mu[qa[:,1]]*gs[j][qa[:,0]]
        pn1=(an1+bn1)*(1+cn1)*.5
        qn1=(an1+bn1)*(1-cn1)*.5
        rn1=np.sqrt(np.power(pn1,2)-cn1*np.power(bn1,2))
        sn1=np.sqrt(np.power(qn1,2)+cn1*np.power(bn1,2))
        ta=np.where(gamhkl<=0)
        tb=np.where(gamhkl>0)
        
        
        transtemp[qa[ta[0],0],qa[ta[0],1],qa[ta[0],2]]=dm(rn1[ta[0]],qn1[ta[0]], pn1[ta[0]],sn1[ta[0]],bnn1[ta[0]]).sears_lr()
        transtemp[qa[tb[0],0],qa[tb[0],1],qa[tb[0],2]]=dm(rn1[tb[0]],qn1[tb[0]], pn1[tb[0]],sn1[tb[0]],bnn1[tb[0]]).sears_lt()

        transrt=tintense(transtemp,backmu)
    
        trans[j]=np.prod(transrt,axis=0)*np.mean(backmu,axis=0)
    return np.mean(trans,axis=0)
class ScatteringCalc:
    """ Calculate scattering and transmission intensities 
    
    Parameters
    ----------
    - samp: tuple-like
        Packed sample inputs:
          - samp[0]: bunge, ndarray (Ngrains, 3, 3) orientation matrices.
          - samp[1]: omg, float (radians) sample rotation about y.
          - samp[2]: gs, ndarray (Ngrains,) path lengths per grain.
          - samp[3]: mosaic, ndarray (Ngrains,) mosaic spreads (radians).
          - samp[4]: int, number of partitions to split bunge/gs/mosaic into for memory/perf.
    - hkl: ndarray, shape (Nrefl, 3)
        Miller indices.
    - lattice: ndarray, shape (1, 6)
        [a, b, c, α, β, γ].
    - atp: ndarray, shape (Natoms, 3)
        Fractional atomic positions.
    - xtal: ndarray
        Material constants; usage defined in _transmission docstring.
    - nxsa, nxsts, nxstm: float
        Multipliers for absorption/scattering contributions.
    - strain: ndarray, shape (Ngrains,)
        Per-grain strain (currently not applied; placeholder).
    - wvltg: ndarray, shape (Nλ,)
        Wavelength grid in Å.
    
    Methods
    ----------
    - transmission() -> ndarray (Nλ,)
        Compute mean transmission across grains and partitions.
    - diffraction(detect, dsp)
        Placeholder; not yet implemented.
    """
    def __init__(self,samp,hkl,lattice,atp,xtal,nxsa,nxsts,nxstm,strain, wvltg):
        self.samp=samp
        self.hkl=hkl
        self.atp=atp
        self.lattice=lattice
        self.xtal=xtal
        self.nxsa=nxsa
        self.nxsts=nxsts
        self.nxstm=nxstm
        self.strain=strain
        self.wvltg=wvltg
        
    def transmission(self):
        """
        Compute the mean neutron transmission over the wavelength grid.
    
        Returns
        ----------
        - trans_mean: ndarray, shape (Nλ,)
            Mean transmission.
    
        Notes
        ----------
        - Partitions the grain-level inputs into samp[4] chunks to control memory usage and to
          enable batched processing in _transmission.
        """

        bunge_b=np.array_split(self.samp[0],self.samp[4])
        gs_b=np.array_split(self.samp[2],self.samp[4])
       
        mosaic_b=np.array_split(self.samp[3],self.samp[4])
        strain_b=np.array_split(self.strain,self.samp[4])
        return _transmission(bunge_b,gs_b,mosaic_b,self.samp[1],self.hkl,self.lattice,self.atp,self.xtal,self.nxsa,self.nxsts,self.nxstm,strain_b,self.wvltg)
    def diffraction(self,detect,dsp):
        """"
        Placeholder for future diffraction intensity computation.
    
        Parameters
        ----------
        - detect: ...
        - dsp: ...
    
        Returns
        - None
    
        Status
        - Not implemented.
        """
        
