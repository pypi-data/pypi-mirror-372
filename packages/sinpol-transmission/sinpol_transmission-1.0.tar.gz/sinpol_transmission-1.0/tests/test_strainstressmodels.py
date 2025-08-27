import sys
import pytest
import warnings
import numpy as np
from sinpol import  stressstrainmodels as ss
from sinpol import sampledata as sd
from sinpol import crystaldata as cds
import time
warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
class TestStressStrainModels():
    
    def test_voigt_single_trans(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,54,45,'single','uniform',np.radians(.001))[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[352],[0],[0],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).voigt()*1e6
        exp = np.load('data/singlecu111voigt-trans.npy')
        assert np.isclose(dat, exp).all()
    def test_voigt_single_long(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,54,45,'single','uniform',np.radians(.001))[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[0],[0],[352],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).voigt()*1e6
        exp = np.load('data/singlecu111voigt-long.npy')
        assert np.isclose(dat, exp).all()
        
    def test_reuss_single_trans(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,54,45,'single','uniform',np.radians(.001))[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        stress=np.array([[352],[0],[0],[0],[0],[0]])
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).reuss()*1e6
        exp = np.load('data/singlecu111reuss-trans.npy')
        assert np.isclose(dat, exp).all()
    def test_reuss_single_long(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,54,45,'single','uniform',np.radians(.001))[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        stress=np.array([[0],[0],[352],[0],[0],[0]])
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).reuss()*1e6
        exp = np.load('data/singlecu111reuss-long.npy')
        assert np.isclose(dat, exp).all()  
    def test_kroner_single_trans(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,54,45,'single','uniform',np.radians(.001))[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        stress=np.array([[0],[0],[352],[0],[0],[0]])
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).kronerrandom()*1e6
        exp = np.load('data/singlecu111kroner-trans.npy')
        assert np.isclose(dat, exp).all()
    def test_kroner_single_long(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,54,45,'single','uniform',np.radians(.001))[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[352],[0],[0],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).kronerrandom()*1e6
        np.save('data/singlecu111kroner-long.npy',dat)
        exp = np.load('data/singlecu111kroner-long.npy')
        assert np.isclose(dat, exp).all()    
    def test_hill_single_trans(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,54,45,'single','uniform',np.radians(.001))[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[352],[0],[0],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).hill()*1e6
        exp = np.load('data/singlecu111hill-trans.npy')
        assert np.isclose(dat, exp).all()
    def test_hill_single_long(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,54,45,'single','uniform',np.radians(.001))[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[0],[0],[352],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).hill()*1e6
        exp = np.load('data/singlecu111hill-long.npy')
        assert np.isclose(dat, exp).all()    
    def test_voigt_poly_trans(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))     
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('uniform','uniform',5,.2,1)[0]
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[352],[0],[0],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).voigt()*1e6
        exp = np.load('data/polycu111voigt-trans.npy')
        assert np.isclose(dat, exp).all()
    def test_voigt_poly_long(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('uniform','uniform',5,.2,1)[0]     
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[0],[0],[352],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).voigt()*1e6
        exp = np.load('data/polycu111voigt-long.npy')
        assert np.isclose(dat, exp).all()
        
    def test_reuss_poly_trans(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('uniform','uniform',5,.2,1)[0]     
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[352],[0],[0],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).reuss()*1e6
        exp = np.load('data/polycu111reuss-trans.npy')
        assert np.isclose(dat, exp).all()
    def test_reuss_poly_long(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('uniform','uniform',5,.2,1)[0]     
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[0],[0],[352],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).reuss()*1e6
        exp = np.load('data/polycu111reuss-long.npy')
        assert np.isclose(dat, exp).all()  
    def test_kroner_poly_trans(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('uniform','uniform',5,.2,1)[0]     
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[352],[0],[0],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).kronerrandom()*1e6
        exp = np.load('data/polycu111kroner-trans.npy')
        assert np.isclose(dat, exp).all()
    def test_kroner_poly_long(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('lognormal','weibull',5,.2,1)[0]     
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[0],[0],[352],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).kronerrandom()*1e6
        exp = np.load('data/polycu111kroner-long.npy')
        assert np.isclose(dat, exp).all()    
    def test_hill_poly_trans(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('lognormal','weibull',5,.2,1)[0]     
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[352],[0],[0],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).hill()*1e6
        exp = np.load('data/polycu111hill-trans.npy')
        assert np.isclose(dat, exp).all()
    def test_hill_poly_long(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('lognormal','weibull',5,.2,1)[0]     
        xtal =cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        hkl=xtal.cstructure(6,3)[2]
        stress=np.array([[0],[0],[352],[0],[0],[0]])
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        dat=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).hill()*1e6
        exp = np.load('data/polycu111hill-long.npy')
        assert np.isclose(dat, exp).all()    


   

      
       