""" Module to calculate sample distirbution """
from math import log, floor, ceil, fmod
import random
from scipy.integrate import quad
from mpmath import erfinv
#import matlab.engine
import numpy as np
import matplotlib.pyplot as plt
import tempfile
from itertools import groupby, chain
#pylint: disable=C0103
#pylint: disable=C0200

# pylint: disable=line-too-long
def bunge(odf,tau):
    """
     Parameters
     - odf: ndarray, shape (N, 3)
    Euler angles per row as [phi1, Phi, phi2] in radians.
    Note: pass radians (use np.radians for degrees).
    - tau: float
    Azimuthal angle in the laboratory frame in degrees.

    Returns
    - bun: ndarray, shape (N, 3, 3)
    Rotation matrices R = R_z(phi2) R_x(Phi) R_z(phi1) R_z(tau).

    LaTeX
    - R = R_z(\\phi_2) R_x(\\Phi) R_z(\\phi_1) R_z(\\tau).

    """
    rho=odf[:,2]
    psi=odf[:,1]
    phi=odf[:,0]
    zerom=np.zeros((len(odf)))
    onem=np.ones((len(odf)))
    tau=np.radians(tau)
    rot_zpa=np.zeros([len(odf),3,3])
    rot_x=np.zeros([len(odf),3,3])
    rot_z=np.zeros([len(odf),3,3])
    bun=np.zeros([len(odf),3,3])
    rot_zpa[:,0,0]=np.cos(phi)
    rot_zpa[:,0,1]=np.sin(phi)
    rot_zpa[:,0,2]=zerom
    rot_zpa[:,1,0]=-np.sin(phi)
    rot_zpa[:,1,1]=np.cos(phi)
    rot_zpa[:,1,2]=zerom
    rot_zpa[:,2,0]=zerom
    rot_zpa[:,2,1]=zerom
    rot_zpa[:,2,2]=onem
    rot_z[:,0,0]=np.cos(rho)
    rot_z[:,0,1]=np.sin(rho)
    rot_z[:,0,2]=zerom
    rot_z[:,1,0]=-np.sin(rho)
    rot_z[:,1,1]=np.cos(rho)
    rot_z[:,1,2]=zerom
    rot_z[:,2,0]=zerom
    rot_z[:,2,1]=zerom
    rot_z[:,2,2]=onem
    rot_x[:,0,0]=onem
    rot_x[:,0,1]=zerom
    rot_x[:,0,2]=zerom
    rot_x[:,1,0]=zerom
    rot_x[:,1,1]=np.cos(psi)
    rot_x[:,1,2]=np.sin(psi)
    rot_x[:,2,0]=zerom
    rot_x[:,2,1]=-np.sin(psi)
    rot_x[:,2,2]=np.cos(psi)
    rot_s=np.array([[np.round(np.cos(tau),15),np.round(np.sin(tau),15),0],[-np.round(np.sin(tau),15),np.round(np.cos(tau),15),0],[0,0,1]])
    for i in range(len(odf)):
        bun[i]=np.dot(np.dot(np.dot(rot_z[i],rot_x[i]),rot_zpa[i]),rot_s)
    return bun
def indexomatirx(tr,tau):
    """
           Parameters
    - tr: array_like, shape (6,)
        [h, k, l, u, v, w].
    - tau: float
        Azimuthal lab z-rotation in degrees.
    
    Returns
    - orn: ndarray, shape (1, 3, 3)
        Orientation matrix.
    
    Notes
    - The constructed basis is right-handed and normalized.

    """
    tau=np.radians(tau)
    MM=(np.power(tr[0],2)+np.power(tr[1],2)+np.power(tr[2],2))
    M=np.sqrt(MM)
    NN=(np.power(tr[3],2)+np.power(tr[4],2)+np.power(tr[5],2))
    N=np.sqrt(NN)
    t11=tr[3]/N
    t12=(tr[1]*tr[5]-tr[2]*tr[4])/(M*N)
    t13=tr[0]/M
    t21=tr[4]/N
    t22=(tr[2]*tr[3]-tr[0]*tr[5])/(M*N)
    t23=tr[1]/M
    t31=tr[5]/N
    t32=(tr[0]*tr[4]-tr[1]*tr[3])/(M*N)
    t33=tr[2]/M
    tex=np.array([[t11,t12,t13],[t21,t22,t23],[t31,t32,t33]])
    rot_s=np.array([[np.round(np.cos(tau),15),np.round(np.sin(tau),15),0],[-np.round(np.sin(tau),15),np.round(np.cos(tau),15),0],[0,0,1]])
    orn=np.dot(tex,rot_s)
    orn=orn[np.newaxis,:,:]
    return orn
def section_file(file):
    """
    Parameters
    - file: str
        Path to file.
    
    Yields
    - section: list[str]
        One header line starting with '#' plus the data lines until the next header.
    """

    with open(file) as f:
            grps = groupby(f, key=lambda x: x.lstrip().startswith("#"))
            for k, v in grps:
                if k:
                    yield chain([next(v)], (next(grps)[1]))  

def createMatlab(crys,fn,num,mtexpath,matlabpath): 
    """
          Parameters
    - crys: list/ndarray of arrays
        Each entry is a pole-figure array per reflection/section.
    - fn: str
        Crystal symmetry tag ('fcc', 'bcc', ...).
    - num: int
        Number of orientations.
    - mtexpath: str
        Path to MTEX toolbox folder.
    - matlabpath: str
        Path to MATLAB scripts folder (with p3/p4).
    
    Returns
    - frame_data: any
        Variable 'FrameData' from MATLAB workspace.
    - name2: str
        Path to temporary text file containing Euler angles (produced by MATLAB).
    """
    try:
        import matlab.engine  # type: ignore
    except Exception as e:
        raise ImportError("MATLAB engine is required for createMatlab but is not available.") from e
    
    fna=[]
    name="tmp"
    for j in range (len(crys)):
        ftmp = tempfile.NamedTemporaryFile(delete=False)
        fnat = ftmp.name + ".txt"
        np.savetxt(fnat, crys[j])
        fna.append(fnat)
    name2=tempfile.NamedTemporaryFile(delete=False).name +".txt"
    eng = matlab.engine.start_matlab()
    eng.addpath(mtexpath,nargout=0)
    eng.startup_mtex(nargout=0)
    eng.addpath(matlabpath,nargout=0)
    eng.workspace['name']=name2
    eng.workspace['number']=num
    eng.workspace['fname'] = fna
    if fn=='fcc':
       eng.p3(nargout=0)
    if fn=='bcc':
       eng.p4(nargout=0)
    eng.evalc('C = who;')
    varnames = eng.workspace['C']
    mvars = {}
    for v in varnames:
        mvars[v] = eng.workspace[v]

#     os.remove(fna) 
    eng.quit()
    return mvars['FrameData'],name2

class SampleData:
    """constructor
    Parameters
    ----------

    - omg: float
        Vertical angle in degrees.
    - tau: float
        Azimuthal angle in degrees (lab z-rotation).
    - ptcm: float
        Plate thickness in cm (converted to Å).
    - grainsize: float
        Grain size in microns (converted to Å).
    - numg: int
        Number of grain orientations (Orn).
    - modev: float
        Base mosaic spread parameter (typ. degrees).
    """
    def __init__(self,omg,tau, ptcm,grainsize,numg,modev):
        
        self.plate=ptcm*1e8   # convert plate from centimeters  to Angstroms
        self.grainsize=grainsize*1e4 # convert grain size from microns to angstroms
        self.Orn=int(numg) # total number of orientation
        self.cols=int(np.ceil(self.Orn*self.grainsize/self.plate))#number of column to intergrate over
        self.tau=tau
        self.omg=omg
        self.gd=self.GrainSizeDistribution(self.plate,self.grainsize,self.Orn,self.cols)
        self.mos=self.MosaicDistribution(self.Orn,modev)
        self.odf=self.CreateDistribution(self.Orn)
    def singlecrystaldeg(self,phi1,Phi,phi2,name:str,name2:str,dev):
        
        """
        Compute orientation matrix from Euler angles given in degrees.
    
        Returns
        - robjt: object array [omb, omg_rad, grain_sizes, mosaic_radians, cols]
        - omb: ndarray, shape (1, 3, 3)
        """
        odf=np.array([[np.radians(phi1),np.radians(Phi),np.radians(phi2)]])
        omb=bunge(odf,self.tau)
        do=f"{name}"
        mo=f"{name2}"
        gs=getattr(self.gd, do)(0)
        nu=np.radians(getattr(self.mos, mo)(dev))
        robjt=np.array([omb,np.radians(self.omg),gs,nu,self.cols],dtype=object)
        return robjt,omb
    def singlecrystalhkl(self,tr,name:str,name2:str,dev):
        """
        Compute orientation matrix from input [h,k,l]/[u,v,w].
    
        Returns
        - robjt: object array [omb, omg_rad, grain_sizes, mosaic_radians, cols]
        - omb: ndarray, shape (1, 3, 3)
        """
        
      
       # odf=indexomatirx(tr,self.tau)
        omb=indexomatirx(tr,self.tau)#bunge(odf,self.tau)
        do=f"{name}"
        mo=f"{name2}"
        gs=getattr(self.gd, do)(0)
        nu=np.radians(getattr(self.mos, mo)(dev))
        robjt=np.array([omb,np.radians(self.omg),gs,nu,self.cols],dtype=object)
        return robjt,omb
    def polycrystalrand(self,name:str,name2:str,gdev,mdev,seed):
        """
        Generate random-texture polycrystal using Halton-based sampling.
    
        Returns
        - robjt: object array [omb, omg_rad, grain_sizes, mosaic_radians, cols]
        - eulers: ndarray, shape (Orn, 3) in radians
        """
        eulers=self.odf.random(seed)
        omb=bunge(self.odf.random(seed),self.tau)
        do=f"{name}"
        mo=f"{name2}"
        gs=getattr(self.gd, do)(gdev)
        nu=np.radians(getattr(self.mos, mo)(mdev))
        robjt=np.array([omb,np.radians(self.omg),gs,nu,self.cols],dtype=object)
        return robjt,eulers
    def polycrystalGauss(self,bv,tr,name:str,name2:str,gdev,mdev):
        """
        Generate textured polycrystal with Gaussian spread about [hkl]/[uvw].
    
        Returns
        - robjt: object array [omb, omg_rad, grain_sizes, mosaic_radians, cols]
        - eulers: ndarray, shape (Orn, 3) in radians
        """
        
        eulers=self.odf.texturegaussian(bv,tr)
        omb=bunge(self.odf.texturegaussian(bv,tr),self.tau)
        do=f"{name}"
        mo=f"{name2}"
        gs=getattr(self.gd, do)(gdev)
        nu=np.radians(getattr(self.mos, mo)(mdev))
        robjt=np.array([omb,np.radians(self.omg),gs,nu,self.cols],dtype=object)
        return robjt,eulers
    def polycrystalloadodf(self,name:str,name2:str,gdev,mdev,file='.txt'):
        """
        Load Euler angles (degrees) from ODF file and build orientation matrices.
    
        Returns
        - robjt: object array [omb, omg_rad, grain_sizes, mosaic_radians, cols]
        - odf_deg: ndarray, shape (Orn, 3) in degrees
        """
            
        
        odf=np.loadtxt(file)
        odf=odf[:self.Orn,:]
        omb=bunge(np.radians(odf),self.tau)
        do=f"{name}"
        mo=f"{name2}"
        gs=getattr(self.gd, do)(gdev)
        nu=np.radians(getattr(self.mos, mo)(mdev))
        robjt=np.array([omb,np.radians(self.omg),gs,nu,self.cols],dtype=object)
        return robjt,odf
    def polycrystalfrompolefigures(self,name:str,name2:str,gdev,mdev,crys,mtex,pamath,fi):
        """
        Compute orientation matrices from pole figures via MATLAB/MTEX.
    
        Returns
        - robjt: object array [omb, omg_rad, grain_sizes, mosaic_radians, cols]
        - odf_deg: ndarray, shape (Orn, 3) in degrees
        """
        secs=[]                 
        for sec in section_file(fi):
            secs.append(list(sec))
        
        secs=np.asanyarray(secs)
        secs=secs[:,1:]
        poles=np.zeros([secs.shape[0],secs.shape[1],3])
        for i in range(len(secs)):
            for j in range (len(secs[i])):
                a=np.fromstring(secs[i,j], sep='\t')
                poles[i,j]=a
        ipf,orie=createMatlab(poles,crys,self.Orn,mtex,pamath)
        
        odf=np.loadtxt(orie,skiprows=4)
        omb=bunge(np.radians(odf),self.tau)
        do=f"{name}"
        mo=f"{name2}"
        gs=getattr(self.gd, do)(gdev)
        nu=np.radians(getattr(self.mos, mo)(mdev))
        robjt=np.array([omb,np.radians(self.omg),gs,nu,self.cols],dtype=object)
        return robjt,odf
    class CreateDistribution:
        """Create orientation distributions (random, textured)."""
        def __init__(self, onumb):
            """constructor
            Parameters
            ----------
            onumb : number  of  crystal orientation"""
            self.onumb=onumb
        def halton(self,  dim ,loc):
            
            """
            Generate a Halton-like sequence.
    
            Parameters
            - dim: int
            - loc: int
    
            Returns
            - h: ndarray, shape (onumb, dim), values in [0, 1).
            """
            nbpts=int(self.onumb)
            h = np.empty(nbpts * dim)
            h.fill(np.nan)
            p = np.empty(nbpts)
            p.fill(np.nan)
            P = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 59, 61, 67, 71, 73, 79, 83, 89, 97]
            lognbpts = log(nbpts + 1)
            for i in range(dim):
                b = P[i]
                n = int(ceil(lognbpts / log(b)))
                for t in range(n):
                    p[t] = pow(b, -(t + loc))
                for j in range(nbpts):
                    d = j + 1
                    sum_ = fmod(d, b) * p[0]
                    for t in range(1, n):
                        d = floor(d / b)
                        sum_ += fmod(d, b) * p[t]
                    h[j * dim + i] = sum_
            return h.reshape(nbpts, dim)
        def random(self,x):
            """
            Create random Euler angles (radians) with uniform φ1, φ2 in [0, 2π] and cos Φ in [−1, 1].
    
            Returns
            - yss: ndarray, shape (onumb, 3), radians.
            """
            Onum=int(self.onumb)
            ys = np.array(self.halton(3, x))
            xx = (ys[:, 0] * 2 * np.pi)
            xx = np.reshape(xx, (Onum, 1))
            yy = np.arccos(2*ys[:, 1]-1)
            yy = np.reshape(yy, (Onum, 1))
            zz = (ys[:, 2] * 2 * np.pi)
            zz = np.reshape(zz, (Onum, 1))
            yss=np.hstack((xx,yy,zz))
            return yss

        def asympBessel(self,alp, s):
            """
            Asymptotic Bessel-like factor used for normalization.

            Returns
            - value: float
            value = exp(s) / sqrt(2 π s) × [1 − (4α^2 − 1)/(8s) + (4α^2 − 1)(4α^2 − 9)/(2·(8s)^2)− (4α^2 − 1)(4α^2 − 9)(4α^2 − 25)/(6·(8s)^3)].
        """
            value= (np.exp(s)/np.power(2*np.pi*s,.5))*(1-((4*np.power(alp,2)-1)/(8*s))+((4*np.power(alp,2)-1)*(4*np.power(alp,2)-9))/(2*np.power(8*s,2))-((4*np.power(alp,2)-1)*(4*np.power(alp,2)-9)*(4*np.power(alp,2)-25))/(6*np.power(8*s,3)))
            return value
        def matthies(self,z,bb):
            """
            Matthies texture kernel.
    
            Returns
            - val: float
              val = exp(−ln 2 · z^2) · z^2 / sqrt(1 − sin^2(b/4) · z^2).
            """
            b=bb
            val=np.exp(-np.log(2)*np.power(z,2))*np.power(z,2)/(np.power(1-np.power(np.sin(.25*b)*z,2),.5))
            return val
        def indexfinder(self,a,value):
            """
            Find indices i, i+1 s.t. a[i] <= value < a[i+1]. Clamped to array range.
    
            Parameters
            - a: array_like (monotonic increasing)
            - value: float
    
            Returns
            - i, j: int
            """
            b=a[a>value].min()
            c=a[a<value].max()
            minidx=np.where(a==c)
            maxidx=np.where(a==b)
            return minidx[0][0],maxidx[0][0]
        def texturegaussian(self,bv,tr):
            """
            Sample Euler angles (radians) from a Gaussian texture about [hkl]/[uvw].
    
            Parameters
            - bv: float
               Angular spread in degrees (FWHM-like).
            - tr: ndarray, shape (6,)
               [h, k, l, u, v, w].
    
            Returns
            - yss: ndarray, shape (onumb, 3)
               Euler angles [phi1, Phi, phi2] in radians.
    
            LaTeX
            - S = \\frac{\\ln 2}{2 \\sin^2(b/4)}, with b in radians.
           """
            orn=self.onumb
            b = np.radians(bv)
            S = np.log(2.0) / (2.0 * np.power(np.sin(b / 4.0), 2))
            wa=np.arange(0,181,.01)
            wr=wa/57.3
            wr=wr.reshape(len(wa),1)
            z=np.zeros([len(wr),1])
            z=np.sin(.5*wr)/np.sin(.25*b)
            warr=np.zeros([len(z),1])
            nms=1/(self.asympBessel(0, S)-self.asympBessel(1, S))
            for i in range(len(z)):
                intg,errint=quad(self.matthies,0,z[i],b)
                warr[i]=nms*np.exp(S)*np.power(2*np.sin(.25*b),3)*intg/(2*np.pi)
            MM=(np.power(tr[0],2)+np.power(tr[1],2)+np.power(tr[2],2))
            M=np.sqrt(MM)
            NN=(np.power(tr[3],2)+np.power(tr[4],2)+np.power(tr[5],2))
            N=np.sqrt(NN)
            t11=tr[3]/N
            t12=(tr[0]*tr[5]-tr[2]*tr[4])/(M*N)
            t13=tr[0]/M
            t21=tr[4]/N
            t22=(tr[2]*tr[3]-tr[0]*tr[5])/(M*N)
            t23=tr[1]/M
            t31=tr[5]/N
            t32=(tr[0]*tr[4]-tr[1]*tr[3])/(M*N)
            t33=tr[2]/M
            tex=np.array([[t11,t12,t13],[t21,t22,t23],[t31,t32,t33]])
            texrot=np.zeros([orn,3,3])
            for j in range (orn):
                xs=np.random.rand()
                minv,maxv=self.indexfinder(warr,xs)
                zx=z[minv]
                w=2*np.arcsin(zx*np.sin(b/4))
                qh=np.random.rand()
                qhe=np.random.rand()
                chi =np.arccos(2*qh-1)
                eta = qhe* 2.0 * np.pi
                a11=(1-np.cos(w))*np.power(np.sin(chi),2)*np.power(np.cos(eta),2)+np.cos(w)
                a12=(1-np.cos(w))*np.power(np.sin(chi),2)*np.cos(eta)*np.sin(eta)+np.sin(w)*np.cos(chi)
                a13=(1-np.cos(w))*np.sin(chi)*np.cos(chi)*np.cos(eta)-np.sin(w)*np.sin(chi)*np.sin(eta)
                a21=(1-np.cos(w))*np.power(np.sin(chi),2)*np.cos(eta)*np.sin(eta)-np.sin(w)*np.cos(chi)
                a22=(1-np.cos(w))*np.power(np.sin(chi),2)*np.power(np.sin(eta),2)+np.cos(w)
                a23=(1-np.cos(w))*np.sin(chi)*np.cos(chi)*np.sin(eta)+np.sin(w)*np.sin(chi)*np.cos(eta)
                a31=(1-np.cos(w))*np.sin(chi)*np.cos(chi)*np.cos(eta)+np.sin(w)*np.sin(chi)*np.sin(eta)
                a32=(1-np.cos(w))*np.sin(chi)*np.cos(chi)*np.sin(eta)-np.sin(w)*np.sin(chi)*np.cos(eta)
                a33=(1-np.cos(w))*np.power(np.cos(chi),2)+np.cos(w)
                rotma=np.array([[a11,a12,a13],[a21,a22,a23],[a31,a32,a33]])
                bmex=np.dot(tex,rotma[:,:,0])
                texrot[j,0,0]=bmex[0,0]
                texrot[j,0,1]=bmex[0,1]
                texrot[j,0,2]=bmex[0,2]
                texrot[j,1,0]=bmex[1,0]
                texrot[j,1,1]=bmex[1,1]
                texrot[j,1,2]=bmex[1,2]
                texrot[j,2,0]=bmex[2,0]
                texrot[j,2,1]=bmex[2,1]
                texrot[j,2,2]=bmex[2,2]
            phi1=np.arctan(-texrot[:,2,0]/texrot[:,2,1])
            phi2=np.arctan(texrot[:,0,2]/texrot[:,1,2])
            PHI=np.arctan(texrot[:,2,0]/(texrot[:,2,2]*np.sin(phi1)))
            PHI= np.reshape(PHI, (orn, 1))
            phi1= np.reshape(phi1, (orn, 1))
            phi2= np.reshape(phi2, (orn, 1))
            yss = np.zeros([orn, 3])
            yss=np.hstack((phi1,PHI,phi2))
            return yss
    class GrainSizeDistribution:
        """  Class to calculate grain size distributuion"""
        def __init__(self,ptcm,grainm,orn,cols):
            """
                ptcm  : plate thickness in  cm 
                grainm  : grain size in microns
                ncolumn : number of discretizes columns in the sample """
            self.plate=ptcm   # convert plate from centimeters  to Angstroms
            self.grainsize=grainm# convert grain size from microns to angstroms
            self.cols=cols
            self.Orn=orn # total number of orientation
        def single(self,b):
            " return  single crystal thickness"
            return np.array([self.plate])
        def uniform(self,b):
            " Create grain distribution of the same size"
            return np.ones([self.Orn])*self.grainsize
        def lognormal(self,b):
            """Create grain size distribution of base on a lognormal distribution
              :param b: std deviation 
              :type b: :class:`float`
              :returns: :1d array --  grain distribution"""
            orn=self.Orn
            pt=self.plate
            tv=self.grainsize
            y=np.random.uniform(0,1,orn)
            cv=b
            ys=2*y-1
            gg=np.zeros([orn])
            for f in range(orn):
                yss=ys[f]
                gg[f]= erfinv(yss)
            d=tv*np.power((1+cv),-1/6)*np.exp((np.sqrt(2*np.log(1+cv))/3.0)*gg)
            npt=np.sum(d)
            ptr=(pt/npt)*self.cols
            return d*ptr
    class MosaicDistribution:
        """ Class to calculate mosaic distribution """
        def __init__(self,orn,mu):
            """Constructor  mosaic distribution 
               orn: number of orientation.
              :type orn : :class:`int`
              :param mu:fwhm  of mosaic
              :type mu : :class:`float`"""
            self.orn=orn
            self.mu=mu
            self.mul=(self.mu)-.5*(self.mu)
            self.muh=(self.mu)+.5*(self.mu)
        def uniform(self,dev):
            """Create mosaic distribution of base on a uniform distribution
              :param dev: std deviation of.
              :type dev: :class:`float`
              :returns: :1d array --  mosaic distribution"""
            return np.ones([self.orn])*self.mu
        def random(self,dev):
            """Create mosaic distribution of base on a random distribution
              :param dev: std deviation of.
              :type dev: :class:`float`
              :returns: :1d array --  mosaic distribution"""
            return np.random.uniform(self.mul,self.muh,self.orn)
        def gaussian(self,dev):
            """Create mosaic distribution of base on a gausssian distribution
              :param dev: std deviation of.
              :type dev: :class:`float`
              :returns: :1d array --  mosaic distribution"""
            nums = []
            for i in range(self.orn):
                temp = random.gauss(self.mu, dev)
                nums.append(temp)
            return  np.array(nums)
        def weibull(self,dev):
            """Create mosaic distribution of base on a weibull distribution
              :param dev: std deviation of.
              :type dev: :class:`float`
              :returns: :1d array --  mosaic distribution"""
            nums = []
            for i in range(self.orn):
                temp = random.weibullvariate(self.mu, dev)
                nums.append(temp)
            return  np.array(nums)
        def lognormal(self,dev):
            """Create mosaic distribution of base on a lognormal distribution
              :param dev: std deviation of.
              :type dev: :class:`float`
              :returns: :1d array --  mosaic distribution """
            dist = np.random.lognormal(self.mu, dev, self.orn)
            count, bins, ignored = plt.hist(dist,density=True)
            bpts = np.linspace(min(bins),max(bins), self.orn)
            plt.show(block=False)
            return (np.exp(-(np.log(bpts) - self.mu)**2 / (2 * dev**2))/ (bpts * dev * np.sqrt(2 * np.pi)))
        
