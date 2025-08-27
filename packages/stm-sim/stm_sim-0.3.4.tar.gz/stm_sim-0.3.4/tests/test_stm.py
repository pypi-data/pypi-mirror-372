import pytest
from stm_sim.stm import STM

class TestSTM:
    def setup_method(self):
        pass

    def test_constant_current(self):
        parchg_file = "parchg_files/Fe28C12_101_17_PARCHG"
        stm = STM(bias=(-0.1, 0.1))
        stm.read_parchg(parchg_file)
        x, y, z = stm.scan(scan_mode='constant_current',
                           repeat=(2, 2),
                           plot=True,
                           )
        dh = stm.delta_h(repeat=(1, 1),plot=True)
        dI_dz = stm.dI_dz()
        print("Done")

    def test_set_current(self):
        parchg_file = "parchg_files/Fe28C12_101_17_PARCHG"
        stm = STM(bias=(-0.1, 0.1))
        stm.read_parchg(parchg_file)
        x, y, z = stm.scan(scan_mode='constant_current',
                           repeat=(2, 2),
                           plot=True,
                           current=0.01,
                           )
        dh = stm.delta_h(repeat=(1, 1),plot=True)
        dI_dz = stm.dI_dz()
        print("Done")

    def test_constant_height(self):
        parchg_file = "parchg_files/Fe28C12_101_17_PARCHG"
        stm = STM(bias=(-0.1, 0.1))
        stm.read_parchg(parchg_file)
        x, y, z = stm.scan(scan_mode='constant_height',
                           height =2.5,
                           repeat=(2, 2),
                           plot=True,
                           )
        dI_dz = stm.dI_dz()
        print("Done")