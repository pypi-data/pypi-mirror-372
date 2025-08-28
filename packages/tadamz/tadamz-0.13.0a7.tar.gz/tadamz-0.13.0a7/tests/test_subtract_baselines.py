# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 13:35:24 2024

@author: pkiefer
"""

import emzed
import os
import pytest
import pickle
import numpy as np
from emzed import MzType, RtType
from src.tadamz.emzed_fixes import subtract_baselines as sb
from emzed.ms_data.peak_map import Chromatogram, ChromatogramType, MSChromatogram

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


def gauss(x, area, mu, sigma):
    return area * np.exp(-((x - mu) ** 2) / (2.0 * sigma**2))


@pytest.fixture
def chromatogram():
    rts = np.arange(60, 120, 0.1)
    ints = gauss(rts, 1e6, 90.0, 3.0) + 1e4
    return Chromatogram(rts, ints)


@pytest.fixture
def zero_chromatogram():
    rts = np.arange(60, 120, 0.5)
    ints = np.zeros(len(rts))
    return Chromatogram(rts, ints)


@pytest.fixture
def ms1_chromatogram():
    type_ = ChromatogramType.SELECTED_ION_MONITORING_CHROMATOGRAM
    mz = 179.0172
    precursor_mz = None
    rts = np.arange(60, 120, 0.1)
    ints = gauss(rts, 1e6, 90.0, 3.0) + 1e4
    return MSChromatogram(mz, precursor_mz, rts, ints, type_)


@pytest.fixture
def ms2_chromatogram():
    type_ = ChromatogramType.SELECTED_REACTION_MONITORING_CHROMATOGRAM
    mz = 89.022
    precursor_mz = 179.0172
    rts = np.arange(60, 120, 0.1)
    ints = gauss(rts, 1e6, 90.0, 3.0) + 1e4
    return MSChromatogram(mz, precursor_mz, rts, ints, type_)


@pytest.fixture
def single_int_chrom():
    type_ = ChromatogramType.SELECTED_ION_MONITORING_CHROMATOGRAM
    mz = 179.0172
    precursor_mz = None
    rts = np.arange(60, 61.0, 0.2)
    ints = np.array([0.0, 0.0, 0.0, 1254.1, 0.0])
    return MSChromatogram(mz, precursor_mz, rts, ints, type_)


@pytest.fixture
def t_chrom(chromatogram):
    colnames = ["rtmin_chromatogram", "rtmax_chromatogram", "chromatogram"]
    types = [RtType, RtType, MSChromatogram]
    rows = [[60.0, 120.0, chromatogram]]
    return emzed.Table.create_table(colnames, types, rows=rows)


@pytest.fixture
def t_ms1chrom(ms1_chromatogram):
    colnames = [
        "mz_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
    ]
    types = [MzType, RtType, RtType, MSChromatogram]
    rows = [[259.0223, 60.0, 120.0, ms1_chromatogram]]
    return emzed.Table.create_table(colnames, types, rows=rows)


@pytest.fixture
def t_ms2chrom(ms2_chromatogram):
    colnames = [
        "precursor_mz_chromatogram",
        "mz_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
    ]
    types = [MzType, MzType, RtType, RtType, MSChromatogram]
    rows = [[259.0223, 89.0223, 60.0, 120.0, ms2_chromatogram]]
    return emzed.Table.create_table(colnames, types, rows=rows)


@pytest.fixture
def t_ms2none(ms2_chromatogram):
    colnames = [
        "precursor_mz_chromatogram",
        "mz_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
    ]
    types = [MzType, MzType, RtType, RtType, MSChromatogram]
    rows = [
        [259.0223, 89.0223, 60.0, 120.0, ms2_chromatogram],
        [259.0223, 89.0223, 60.0, 120.0, None],
    ]
    return emzed.Table.create_table(colnames, types, rows=rows)


@pytest.fixture
def measured_chromatogram():
    path = os.path.join(data_folder, "test_chromatogram.pickle")
    with open(path, "rb") as fp:
        chrom = pickle.load(fp)
    return chrom


def test__subtract_baselines_0(chromatogram):
    is_ = sb._subtract_baseline(chromatogram)
    exp = chromatogram.intensities - 1e4
    assert np.all(np.abs(is_.intensities - exp) < 1e-2)


def test__subtract_baselines_1(zero_chromatogram):
    is_ = sb._subtract_baseline(zero_chromatogram)
    assert np.all(is_.intensities == 0.0)


def test__subtract_baselines_2(ms1_chromatogram):
    is_ = sb._subtract_baseline(ms1_chromatogram)
    exp = ms1_chromatogram.intensities - 1e4
    deltas = np.abs(is_.intensities - exp)
    print(max(deltas))
    assert np.all(deltas < 1e-1)


def test__subtract_baselines_3(ms2_chromatogram):
    is_ = sb._subtract_baseline(ms2_chromatogram)
    exp = ms2_chromatogram.intensities - 1e4
    assert np.all(np.abs(is_.intensities - exp) < 1e-1)


def test__subtract_baselines_4():
    is_ = sb._subtract_baseline(None)
    assert is_ is None


def test__subtract_baseline_5(measured_chromatogram):
    is_ = sb._subtract_baseline(measured_chromatogram)
    assert all([i >= 0 for i in is_.intensities])


def test_subtract_baseline_0(t_chrom):
    sb.subtract_baselines(t_chrom, True)
    print(t_chrom.col_names)
    expected = (
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
        "rtmin_chromatogram__0",
        "rtmax_chromatogram__0",
        "chromatogram__0",
    )
    assert t_chrom.col_names == expected


def test_subtract_baseline_1(t_ms1chrom):
    sb.subtract_baselines(t_ms1chrom, True)
    print(t_ms1chrom.col_names)
    expected = (
        "mz_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
        "mz_chromatogram__0",
        "rtmin_chromatogram__0",
        "rtmax_chromatogram__0",
        "chromatogram__0",
    )
    assert t_ms1chrom.col_names == expected


def test_subtract_baseline_2(t_ms2chrom):
    sb.subtract_baselines(t_ms2chrom, True)
    print(t_ms2chrom.col_names)
    expected = (
        "precursor_mz_chromatogram",
        "mz_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
        "precursor_mz_chromatogram__0",
        "mz_chromatogram__0",
        "rtmin_chromatogram__0",
        "rtmax_chromatogram__0",
        "chromatogram__0",
    )
    assert t_ms2chrom.col_names == expected


def test_subtract_baseline_3(t_ms2chrom):
    sb.subtract_baselines(t_ms2chrom, True)
    print(t_ms2chrom.col_names)
    expected = (
        "precursor_mz_chromatogram",
        "mz_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
        "precursor_mz_chromatogram__0",
        "mz_chromatogram__0",
        "rtmin_chromatogram__0",
        "rtmax_chromatogram__0",
        "chromatogram__0",
    )
    assert t_ms2chrom.col_names == expected


def test_subtract_baseline_4(t_ms2none):
    sb.subtract_baselines(t_ms2none, True)
    is_ = [type(x) for x in t_ms2none.chromatogram__0.to_list()]
    expected = [MSChromatogram, type(None)]
    assert is_ == expected


def test__get_baseline_from_mixture_model(single_int_chrom):
    is_ = sb._get_baseline_from_mixture_model(single_int_chrom)
    expected = np.array([0.0] * 5)
    print(is_)
    assert np.all(is_ - expected < 1e-10)


def test_subtract_baseline_5(t_ms2chrom):
    sb.subtract_baselines(t_ms2chrom, True)
    t1 = emzed.quantification.integrate_chromatograms(t_ms2chrom, "linear")
    t2 = emzed.quantification.integrate_chromatograms(t_ms2chrom, "emg")
    model1 = t1.model_chromatogram.unique_value()
    model2 = t2.model_chromatogram.unique_value()
    rts, ints = model1.graph()
    rts2, ints2 = model2.graph()
    pos = np.logical_and(rts >= min(rts2), rts <= max(rts2))
    rts = rts[pos]
    ints = ints[pos]
    print(min(rts), max(rts))
    print(min(rts2), max(rts2))
    intsx = model2.apply(rts)
    rel_deltas = np.abs(intsx - ints) / max(ints)
    print(max(rel_deltas))
    assert np.all((rel_deltas) < 0.06)
