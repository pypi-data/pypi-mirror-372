# -*- coding: utf-8 -*-
"""
Created on Thu Jan 11 16:45:31 2024

@author: pkiefer
"""

from re import T
import pytest
import emzed
from emzed import MSChromatogram, RtType, MzType, Table
import os
import numpy as np

# from src.targeted_wf import extract_peaks as ep
from src.tadamz import adapt_retention_time as art


@pytest.fixture
def t0():
    type_ = "SELECTED_REACTION_MONITORING_CHROMATOGRAM"
    columns = (
        "name",
        "is_coelution_reference_peak",
        "precursor_mz_chromatogra,",
        "mz_chromatogram",
        "rt_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
        "filename",
        "peak_coelutes",
    )
    types = str, bool, MzType, MzType, RtType, RtType, RtType, MSChromatogram, str, str
    rts = np.arange(120, 180, 0.2)
    ints1a = gauss(rts, 3.0, 140) * 1e5
    ints1b = gauss(rts, 3.0, 160) * 1.5e5
    ints1c = gauss(rts, 3.0, 153) * 1.5e5
    ints1 = ints1a + ints1b
    ints2 = ints1a + ints1c
    ints_ref = gauss(rts, 3.0, 140) * 3e5
    chrom1 = MSChromatogram(259, 97, rts, ints1, type_)
    chromr1 = MSChromatogram(265, 97, rts, ints_ref, type_)
    chrom2 = MSChromatogram(259, 97, rts, ints2, type_)
    chromr2 = MSChromatogram(265, 97, rts, ints_ref, type_)
    rows = [
        ["c1", False, 259, 97, 160, 150, 170, chrom1, "s1", "bad"],
        ["c1", True, 265, 97, 140, 130, 150, chromr1, "s1", "ok"],
        ["c1", False, 259, 97, 153, 147, 160, chrom2, "s2", "bad"],
        ["c1", True, 265, 97, 140, 130, 150, chromr2, "s2", "ok"],
    ]
    t = Table.create_table(columns, types, rows=rows)
    emzed.quantification.integrate_chromatograms(t, "linear", in_place=True)
    return t


@pytest.fixture
def t1():
    type_ = "SELECTED_REACTION_MONITORING_CHROMATOGRAM"
    columns = (
        "name",
        "is_coelution_reference_peak",
        "precursor_mz_chromatogra,",
        "mz_chromatogram",
        "rt_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
        "filename",
        "peak_coelutes",
    )
    types = str, bool, MzType, MzType, RtType, RtType, RtType, MSChromatogram, str, str
    rts = np.arange(120, 180, 0.2)
    ints1a = gauss(rts, 3.0, 140) * 1e5
    ints1c = gauss(rts, 3.0, 153) * 1.5e5
    ints2 = ints1a + ints1c
    ints_ref = gauss(rts, 3.0, 140) * 3e5
    chrom2 = MSChromatogram(259, 97, rts, ints2, type_)
    chromr2 = MSChromatogram(265, 97, rts, ints_ref, type_)
    rows = [
        ["c1", False, 259, 97, 153, 144, 160, chrom2, "s2", "bad"],
        ["c1", True, 265, 97, 140, 130, 150, chromr2, "s2", "ok"],
    ]
    t = Table.create_table(columns, types, rows=rows)
    emzed.quantification.integrate_chromatograms(t, "linear", in_place=True)
    return t


@pytest.fixture
def t2():
    type_ = "SELECTED_REACTION_MONITORING_CHROMATOGRAM"
    columns = (
        "name",
        "is_coelution_reference_peak",
        "precursor_mz_chromatogra,",
        "mz_chromatogram",
        "rt_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
        "filename",
        "peak_coelutes",
    )
    types = str, bool, MzType, MzType, RtType, RtType, RtType, MSChromatogram, str, str
    rts = np.arange(120, 180, 0.2)
    ints1 = np.zeros(len(rts))
    ints_ref = gauss(rts, 3.0, 140) * 3e5
    chrom1 = MSChromatogram(259, 97, rts, ints1, type_)
    chromr2 = MSChromatogram(265, 97, rts, ints_ref, type_)
    rows = [
        ["c1", False, 259, 97, 153, 144, 160, chrom1, "s2", "bad"],
        ["c1", True, 265, 97, 140, 130, 150, chromr2, "s2", "ok"],
    ]
    t = Table.create_table(columns, types, rows=rows)
    emzed.quantification.integrate_chromatograms(t, "linear", in_place=True)
    return t


@pytest.fixture
def t_empty():
    type_ = "SELECTED_REACTION_MONITORING_CHROMATOGRAM"
    columns = (
        "name",
        "is_coelution_reference_peak",
        "precursor_mz_chromatogra,",
        "mz_chromatogram",
        "rt_chromatogram",
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "chromatogram",
        "filename",
        "peak_coelutes",
    )
    types = str, bool, MzType, MzType, RtType, RtType, RtType, MSChromatogram, str, str
    chrom1 = MSChromatogram(259, 97, np.array([]), np.array([]), type_)

    rows = [
        ["c1", False, 259, 97, 153, 144, 160, chrom1, "s2", "bad"],
    ]
    t = Table.create_table(columns, types, rows=rows)
    emzed.quantification.integrate_chromatograms(t, "linear", in_place=True)
    return t


def test_adapt_rt_by_coeluting_peaks_0(t0):
    # peaks are shifted to reference peak
    t = art.adapt_rt_by_coeluting_peaks(t0, "name", "is_coelution_reference_peak")
    assert all([abs(rt - 140) < 1e-5 for rt in t.rt_chromatogram])


def test_adapt_rt_by_coeluting_peaks_1(t1):
    # peaks are shifted to reference peak, right window limit is at the local minimum of
    # the overlapping peaks
    t = art.adapt_rt_by_coeluting_peaks(t1, "name", "is_coelution_reference_peak")
    sub = t.filter(t.is_coelution_reference_peak == False)
    assert abs(sub.rtmax_chromatogram.unique_value() - 146.2) < 0.1


def test_adapt_rt_by_coeluting_peaks_2(t2):
    # missing peak: rt value is defined as middle of the integration window
    t = art.adapt_rt_by_coeluting_peaks(t2, "name", "is_coelution_reference_peak")
    sub = sub = t.filter(t.is_coelution_reference_peak == False)
    r = sub.rows[0]
    assert (
        abs(r.rt_chromatogram - (r.rtmin_chromatogram + r.rtmax_chromatogram) / 2)
        <= 0.2
    )


def test_adapt_rt_by_coeluting_peaks_3(t0):
    # multiple integration algorithms.
    t0.add_enumeration()
    algos = ["linear", "emg", "sgolay", "linear"]
    t0.replace_column("peak_shape_model_chromatogram", algos, str)
    id2algo = dict(zip(t0.id, t0.peak_shape_model_chromatogram))
    t = art.adapt_rt_by_coeluting_peaks(t0, "name", "is_coelution_reference_peak")
    d = dict(zip(t.id, t.peak_shape_model_chromatogram))
    for key in d.keys():
        assert d[key] == id2algo[key]


def gauss(rts, sigma, rt):
    return (
        1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-((rts - rt) ** 2) / (2 * sigma**2))
    )


def test_local_adjust_0(t0):
    # we shift all peaks by 5 seconds
    t0.add_enumeration("rid")
    t0.add_column_with_constant_value("rt_max_shift", 8.0, RtType)
    rid2rt = dict(zip(t0.rid, t0.rt_chromatogram))
    columns = ["rt_chromatogram", "rtmin_chromatogram", "rtmax_chromatogram"]
    for col in columns:
        t0.replace_column(col, t0[col] + 5.0, RtType)
    art.local_adjust(t0, 2.0)
    d = dict(zip(t0.rid, t0.rt_chromatogram))
    for key in d.keys():
        assert np.abs(rid2rt[key] - d[key]) < 0.1


def test_local_adjust_1(t0):
    # we shift all peaks by 5 seconds
    t0.add_enumeration("rid")
    t0.add_column_with_constant_value("rt_max_shift", 8.0, RtType)
    rid2rt = dict(zip(t0.rid, t0.rt_chromatogram))
    columns = ["rt_chromatogram", "rtmin_chromatogram", "rtmax_chromatogram"]
    for col in columns:
        t0.replace_column(col, t0[col] - 8.0, RtType)
    art.local_adjust(t0, 2.0)
    d = dict(zip(t0.rid, t0.rt_chromatogram))
    for key in d.keys():
        assert np.abs(rid2rt[key] - d[key]) < 0.1


def test_local_adjust_2(t_empty):
    # we shift all peaks by 5 seconds
    t_empty.add_enumeration("rid")
    t_empty.add_column_with_constant_value("rt_max_shift", 8.0, RtType)
    rid2rt = dict(zip(t_empty.rid, t_empty.rt_chromatogram))
    columns = ["rt_chromatogram", "rtmin_chromatogram", "rtmax_chromatogram"]
    for col in columns:
        t_empty.replace_column(col, t_empty[col] - 8.0, RtType)
    art.local_adjust(t_empty, 2.0)
    d = dict(zip(t_empty.rid, t_empty.rt_chromatogram))
    for key in d.keys():
        assert np.abs(rid2rt[key] - d[key]) - 8 < 0.1
