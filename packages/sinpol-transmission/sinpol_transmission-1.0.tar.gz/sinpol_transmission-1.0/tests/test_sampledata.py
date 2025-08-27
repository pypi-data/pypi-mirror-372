import sys
import pytest
import warnings
import numpy as np
from sinpol import sampledata as sd

warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)
warnings.filterwarnings("ignore")

class TestSampleData():
    
    def test_singlecrystaldeg(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystaldeg(0,86.5,42.7,'single','uniform',np.radians(.001))
      
        tarr=np.zeros([1,3,3])
        tarr2=np.zeros([1,1])
        tarr3=np.zeros([1])
        tarr4=np.zeros([1,3,3])
        assert tt[0][0].shape ==tarr.shape
        assert tt[0][1]==0.0
        assert tt[0][2].shape==tarr3.shape
        assert tt[0][3].shape==tarr3.shape
        assert tt[0][4]==orn
        assert tt[1].shape ==tarr4.shape
    def test_singlecrystalhkl(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        col=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).singlecrystalhkl(np.array([-1,1,0,0,0,1]),'single','weibull',.2)
        tarr=np.zeros([1,3,3])
        tarr2=np.zeros([1,1])
        tarr3=np.zeros([1])
        tarr4=np.zeros([1,3,3])
        assert tt[0][0].shape ==tarr.shape
        assert tt[0][1]==0.0
        assert tt[0][2].shape==tarr3.shape
        assert tt[0][3].shape==tarr3.shape
        assert tt[0][4]==orn
        assert tt[1].shape ==tarr4.shape
         
    def test_polycrystalrand(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))     
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalrand('lognormal','weibull',5,.2,1)
        tarr=np.zeros([10000,3,3])
        tarr3=np.zeros([10000])
        tarr4=np.zeros([10000,3])
        assert tt[0][0].shape ==tarr.shape
        assert tt[0][1]==0.0
        assert tt[0][2].shape==tarr3.shape
        assert tt[0][3].shape==tarr3.shape
        assert tt[0][4]==cols
        assert tt[1].shape ==tarr4.shape

    def test_polycrystalGauss(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).polycrystalGauss(10,np.array([-1,1,0,0,0,1]),'lognormal','weibull',5,.2)
        tarr=np.zeros([10000,3,3])
        tarr3=np.zeros([10000])
        tarr4=np.zeros([10000,3])
        assert tt[0][0].shape ==tarr.shape
        assert tt[0][1]==0.0
        assert tt[0][2].shape==tarr3.shape
        assert tt[0][3].shape==tarr3.shape
        assert tt[0][4]==cols
        assert tt[1].shape ==tarr4.shape 
    def test_singlecrystal(self):
        ptcm=1 # in cm
        grainsize=1e4 # in microns
        orn=1
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).gd.single(1)
        # gsd.GrainSizeDistribution(1,1,1).singlecrystal()
        assert tt==1e8

    def test_grainuniform(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).gd.uniform(1)
        assert np.isclose(tt, np.ones([10000,1])*1e4).all()
    def test_grainlognormal(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).gd.lognormal(0)
        assert np.isclose(tt, np.ones([10000])*1e4).all()

    def test_halton(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).odf.halton(3,1)
        tarr=np.zeros([10000,3])

        assert tt.shape ==tarr.shape

    def test_random(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).odf.random(1)
        tarr=np.zeros([10000,3,])
        assert tt.shape ==tarr.shape
    def test_texturegaussian(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).odf.texturegaussian(10,np.array([1,0,0,0,0,1]))
        tarr=np.zeros([10000,3])
        assert tt.shape ==tarr.shape
    def test_AsympBessel(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).odf.AsympBessel(0,182.15300579866454)
        assert tt==3.793464520668295e+77
    def test_Matthies(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).odf.Matthies(8.77944168127861,0.17453292519943295)
        assert tt==5.228795326561545e-22
    def test_Indexfinder(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        tt=sd.SampleData(0,0,ptcm,grainsize,orn,.2).odf.Indexfinder(np.load('data/index.npy'),0.6401538315412594)
        assert tt[0]==762
        assert tt[1] ==763             
      
    def test_orientmatrixsingle(self):
        odf=np.array(np.radians([[0,54,45]]))
        tarr=np.zeros([1,3,3])
        bmat=sd.bunge(odf,0)
       
        assert bmat.shape ==tarr.shape
    def test_orientmatricespoly(self):
        ptcm=1 # in cm
        grainsize=1 # in microns
        orn=10000
        cols=int(np.ceil(orn*grainsize/(ptcm*1e8)))
        odf=sd.SampleData(0,0,ptcm,grainsize,orn,.2).odf.random(1) 
        tarr=np.zeros([10000,3,3])
        bmat=sd.bunge(odf,0)
        assert bmat.shape ==tarr.shape
