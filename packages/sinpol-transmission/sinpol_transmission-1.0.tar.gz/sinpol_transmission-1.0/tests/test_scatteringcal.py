import sys
import pytest
import warnings
import numpy as np
from sinpol import sampledata as sd
from sinpol import crystaldata as cds
from sinpol import scatteringcal as sctt
from sinpol import  stressstrainmodels as ss
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
warnings.filterwarnings("ignore")

class TestScatteringCal():
    
    def test_singlecrystaldeg(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,86.5,42.7,'single','uniform',np.radians(.001))[0]
        w=np.arange(1,4.5,.001)
        xtal=cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        atp=xtal.cstructure(6,36)[1]
        hkl=xtal.cstructure(6,36)[2]
        cryn=xtal.neutronics.dat
        nxs=xtal.nxs
        absnxs=xtal.nxs.nxs_absorption(w)
        Tdsspnxs=xtal.nxs.nxs_tdssp(w)
        Tdsmpnxs=xtal.nxs.nxs_tdsmp(w)
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        stress=np.array([[0],[0],[0],[0],[0],[0]],dtype=np.float64)
        strain=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).voigt()
        trans=sctt.ScatteringCalc(tt,hkl,latt,atp,cryn,absnxs,Tdsspnxs,Tdsmpnxs,strain,w).transmission()
        exp = np.load('data/transsindeg.npy')
        assert np.isclose(trans, exp).all()
    def test_singlecrystalhkl(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystalhkl(np.array([0,0,1,1,0,0]),'single','uniform',.2)[0]
        w=np.arange(1,4.5,.0001)
        xtal=cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        atp=xtal.cstructure(6,36)[1]
        hkl=xtal.cstructure(6,36)[2]
        cryn=xtal.neutronics.dat
        nxs=xtal.nxs
        absnxs=xtal.nxs.nxs_absorption(w)
        Tdsspnxs=xtal.nxs.nxs_tdssp(w)
        Tdsmpnxs=xtal.nxs.nxs_tdsmp(w)
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        stress=np.array([[0],[0],[0],[0],[0],[0]],dtype=np.float64)
        strain=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).voigt()
        trans=sctt.ScatteringCalc(tt,hkl,latt,atp,cryn,absnxs,Tdsspnxs,Tdsmpnxs,strain,w).transmission()
        exp = np.load('data/transsinhkl.npy')
        assert np.isclose(trans, exp).all()
         
    def test_polycrystalrand(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))     
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('lognormal','uniform',5,.2,1)[0]
        w=np.arange(1,4.5,.01)
        xtal=cds.CrystalData('Cu.cif')
        latt=xtal.cstructure(6,36)[0]
        atp=xtal.cstructure(6,36)[1]
        hkl=xtal.cstructure(6,36)[2]
        cryn=xtal.neutronics.dat
        nxs=xtal.nxs
        absnxs=xtal.nxs.nxs_absorption(w)
        Tdsspnxs=xtal.nxs.nxs_tdssp(w)
        Tdsmpnxs=xtal.nxs.nxs_tdsmp(w)
        C11 = 262.41
        C12 = 191.42  
        C44 = 117.26
        stress=np.array([[0],[0],[0],[0],[0],[0]],dtype=np.float64)
        strain=ss.StressStrainModels(tt[0],hkl,latt,stress,C11,C12,C44).voigt()
        trans=sctt.ScatteringCalc(tt,hkl,latt,atp,cryn,absnxs,Tdsspnxs,Tdsmpnxs,strain,w).transmission()
        np.save('data/transpolyr.npy',trans)
        exp = np.load('data/transpolyr.npy')
        assert np.isclose(trans,exp).all()

   