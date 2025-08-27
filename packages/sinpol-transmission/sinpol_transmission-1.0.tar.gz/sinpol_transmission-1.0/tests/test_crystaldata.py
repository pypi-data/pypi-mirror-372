import sys
import pytest
import warnings
import numpy as np
from sinpol import crystaldata as cds

warnings.simplefilter(action='ignore', category=RuntimeWarning)
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)



class TestCrystalData():
    def test_crystaldatanruronic_cu(self):
        xtal=cds.CrystalData('Cu.cif')
        dat=xtal.neutronics
        exp = np.load('data/cuneutronics.npy')
        dta=np.array([dat.b,dat.abs,dat.coh,dat.inc,dat.xsbound])
        assert np.isclose(dta, exp).all()
    def test_latticeparm_cu(self):
        xtal=cds.CrystalData('Cu.cif')
        dat=xtal.latticeparm()
        exp = np.load('data/cupar.npy')
        assert np.isclose(dat, exp).all()
        with warnings.catch_warnings():
             warnings.simplefilter("ignore")
    def test_atmposition_cu(self):
        wvl=np.arange(1,5,.01)
        xtal=cds.CrystalData('Cu.cif')
        dat=xtal.atmposition()
        exp = np.load('data/cupos.npy')
        assert np.isclose(dat, exp).all()
    def test_hklmaker_cu(self):
        xtal=cds.CrystalData('Cu.cif')
        dat=xtal.hklmaker(6,24)
        exp = np.load('data/cuhklm.npy')
        assert np.isclose(dat, exp).all()
    def test_hklnbuilderr_cu(self):
        xtal=cds.CrystalData('Cu.cif')
        hklm=xtal.hklmaker(6,24)
        dat=xtal.hklnbuilder(hklm,12)
        exp = np.load('data/cuhklb.npy')
        assert np.isclose(dat, exp).all()
    def test_crystaldata_cu(self):
        xtal=cds.CrystalData('Cu.cif')
        dat=xtal.cstructure(6,24)
        exp = np.load('data/cucrystaldata.npy',allow_pickle=True)
        assert np.isclose(dat[0], exp[0]).all()
        assert np.isclose(dat[1], exp[1]).all()
        assert np.isclose(dat[2], exp[2]).all()
    def test_nxsTdssp_cu(self):
        wvl=np.arange(1,5,.01)
        xtal=cds.CrystalData('Cu.cif')
        nxs=xtal.nxs
        dat=nxs.nxs_tdssp(wvl)
        exp = np.load('data/cu_nxstdssp.npy')
        assert np.isclose(dat, exp).all()
    def test_nxsTdsmp_cu(self):
        wvl=np.arange(1,5,.01)
        xtal=cds.CrystalData('Cu.cif')
        nxs=xtal.nxs
        dat=nxs.nxs_tdsmp(wvl)
        exp = np.load('data/cu_nxstdsmp.npy')
        assert np.isclose(dat, exp).all()
    def test_nxsabs_cu(self):
        wvl=np.arange(1,5,.01)
        xtal=cds.CrystalData('Cu.cif')
        nxs=xtal.nxs
        dat=nxs.nxs_absorption(wvl)
        exp = np.load('data/cu_nxsabs.npy')
        assert np.isclose(dat, exp).all()      
          
