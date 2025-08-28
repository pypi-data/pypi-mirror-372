# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 08:58:37 2023

@author: pkiefer
"""

import os
import pytest
import emzed
from src.tadamz import extract_peaks_from_chromatograms as epc
from src.tadamz import extract_peaks as ep

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def config_srm():
    config = {
        "integration_algorithm": "linear",
        "chromatogram_boundery_factor": 3.0,
        "precursor_column": "precursor_mz",
        "precursor_mz_tol": 0.5,
        "mz_tol_abs": 0.5,
        "mz_tol_rel": 0.0,
        "ms_data_type": "MS_Chromatogram",
        "peak_width_col": None,
    }
    return config


@pytest.fixture
def srm():
    path = os.path.join(here, "data/mrm_data_large.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def pt_srm():
    path = os.path.join(here, "data/peptide_table.xlsx")
    pt = emzed.io.load_excel(path)
    kwargs = {"ms_data_type": "MS_Chromatogram", "peak_width_col": None}
    pt = ep._update_postfixes(pt, kwargs)
    return pt


def test_extract_peaks_from_chromatogram_0(pt_srm, srm, config_srm, regtest):
    print(pt_srm.col_names)
    t = epc.add_chromatograms_to_peaks_table(pt_srm, srm, config_srm)
    print(t, file=regtest)


def test_extract_peaks_from_chromatogram_1(pt_srm, srm, config_srm, regtest):
    t = epc.add_chromatograms_to_peaks_table(pt_srm, srm, config_srm)
    assert len(set(t.id)) == len(t.id.to_list())


def test_extract_peaks_from_chromatogram_2(pt_srm, srm, config_srm, regtest):
    t = epc.add_chromatograms_to_peaks_table(pt_srm, srm, config_srm)
    assert len(t) == len(pt_srm)
