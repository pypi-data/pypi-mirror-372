# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 16:04:35 2024

@author: pkiefer
"""
import os
import emzed
import pytest
from src.tadamz.emzed_fixes import pick_ms_chromatogram_peaks as pmc

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def pm_sim():
    path = os.path.join(here, "data", "sim_data.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def pm_mrm():
    path = os.path.join(here, "data", "mrm_data1.mzml")
    return emzed.io.load_peak_map(path)


def test_extract_ms_chromatograms_0(pm_sim):
    t = pmc.extract_ms_chromatograms(pm_sim)
    y = {id_: (x.precursor_mz, x.mz) for id_, x in zip(t.id, t.chromatogram)}
    t.add_column("expected", t.apply(y.get, t.id), object)
    for mz, precursor_mz, pair in zip(
        t.mz_chromatogram, t.precursor_mz_chromatogram, t.expected
    ):
        prec, mz_ = pair
        assert (prec == mz) and (precursor_mz is None) and (mz_ == 0.0)


def test_extract_chromatograms_1(pm_mrm):
    attributes = ["precursor_mz", "mz", "rts", "intensities", "type"]
    t = pmc.extract_ms_chromatograms(pm_mrm)
    sames = []
    for chrom_pair, attr in zip(
        zip(pm_mrm.ms_chromatograms[1:], t.chromatogram), attributes
    ):
        before, after = chrom_pair
        values = before.__getattribute__(attr) == after.__getattribute__(attr)
        if isinstance(values, bool):
            sames.append(values)
        else:
            sames.extend(values)
        print(sames)
    assert all(sames)
