# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 09:22:40 2023

@author: pkiefer
"""
import pytest
import os
import numpy as np
import emzed
from emzed import Table, MzType, RtType, mass, quantification
from emzed.ms_data.peak_map import MSChromatogram, Chromatogram
from src.tadamz import normalize_peaks as normalize
from src.tadamz import std_free_normalization as sfree

here = os.path.abspath(os.path.dirname(__file__))


def generate_chromatogram(rtmin, rtmax, area, mu, sigma):
    rts = np.arange(rtmin, rtmax, 0.1)
    ints = gauss(rts, area, mu, sigma)
    return MSChromatogram(100, None, rts, ints, Chromatogram)


def gauss(x, area, mu, sigma):
    return area * np.exp(-((x - mu) ** 2) / (2.0 * sigma**2))


@pytest.fixture
def t0():
    # path = os.path.join(here, "data/mrm_data1.mzml")
    # pm = emzed.io.load_peak_map(path)
    columns = [
        "id",
        "std_id",
        "normalize_by_std_id",
        "area_chromatogram",
        "tic_area",
        "filename",
    ]
    types = [int, int, int, float, float, str]
    rows = [[1, None, None, 100, 1000, "s0"], [2, 2, None, 400, 1000, "s0"]]
    formats = ["%d", "%d", "%d", "%.2e", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t1():
    # path = os.path.join(here, 'data/mrm_data2.mzml')
    # pm = emzed.io.load_peak_map(path)
    columns = [
        "id",
        "std_id",
        "normalize_by_std_id",
        "area_chromatogram",
        "tic_area",
        "filename",
    ]
    types = [int, int, int, float, float, str]
    rows = [[1, None, 2, 200, 5000, "s1"], [2, 2, None, 100, 5000, "s1"]]
    formats = ["%d", "%d", "%d", "%.2e", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t2():
    # path = os.path.join(here, "data/mrm_data1.mzml")
    # pm = emzed.io.load_peak_map(path)
    columns = [
        "id",
        "std_id",
        "normalize_by_std_id",
        "area_chromatogram",
        "tic_area",
        "filename",
    ]
    types = [int, int, int, float, float, str]
    rows = [[2, None, 2, 100, 1000, "s0"], [2, None, 2, 400, 1000, "s0"]]
    formats = ["%d", "%d", "%d", "%.2e", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t3():
    # path = os.path.join(here, "data/mrm_data1.mzml")
    # pm = emzed.io.load_peak_map(path)
    columns = [
        "id",
        "std_id",
        "normalize_by_std_id",
        "area_chromatogram",
        "tic_area",
        "filename",
    ]
    types = [int, int, int, float, float, str]
    rows = [
        [2, None, 2, 100, 1000, "s0"],
        [2, 2, None, 400, 1000, "s0"],
        [2, None, 2, 400, 1000, "s1"],
        [2, None, None, 500, 1000, "s1"],
        [2, 2, None, 400, 1000, "s1"],
    ]
    formats = ["%d", "%d", "%d", "%.2e", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t4():
    # path = os.path.join(here, "data/mrm_data1.mzml")
    # pm = emzed.io.load_peak_map(path)
    columns = [
        "id",
        "std_id",
        "normalize_by_std_id",
        "area_chromatogram",
        "tic_area",
        "filename",
    ]
    types = [int, float, float, float, float, str]
    rows = [
        [2, None, 2, 100, 1000, "s0"],
        [2, 2, None, 400, 1000, "s0"],
        [2, None, 2, 400, 1000, "s1"],
        [2, None, None, 500, 1000, "s1"],
        [2, 2, None, 400, 1000, "s1"],
    ]
    formats = ["%d", "%.1f", "%.1f", "%.2e", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t5():
    # path = os.path.join(here, "data/mrm_data1.mzml")
    # pm = emzed.io.load_peak_map(path)
    columns = [
        "id",
        "std_id",
        "normalize_by_std_id",
        "area_chromatogram",
        "tic_area",
        "filename",
    ]
    types = [int, str, str, float, float, str]
    rows = [
        [2, None, "a", 100, 1000, "s0"],
        [2, "a", None, 400, 1000, "s0"],
        [2, None, "a", 400, 1000, "s1"],
        [2, None, None, 500, 1000, "s1"],
        [2, "a", None, 400, 1000, "s1"],
    ]
    formats = ["%d", "%s", "%s", "%.2e", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t6():
    # path = os.path.join(here, "data/mrm_data1.mzml")
    # pm = emzed.io.load_peak_map(path)
    columns = [
        "id",
        "std_id",
        "normalize_by_std_id",
        "area_chromatogram",
        "tic_area",
        "filename",
    ]
    types = [int, str, str, float, float, str]
    rows = [
        [2, None, "a", 100, 1000, "s0"],
        [2, "a", None, 400, 1000, "s0"],
        [1, None, None, 400, 1000, "s1"],
        [1, None, None, 500, 1000, "s1"],
        [3, None, None, 400, 1000, "s1"],
    ]
    formats = ["%d", "%s", "%s", "%.2e", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t_isotop():
    columns = [
        "pid",
        "mi",
        "std_id",
        "normalize_by_std_id",
        "area_chromatogram",
        "filename",
    ]
    types = [int, int, int, int, float, str]
    rows = [
        [1, 0, 0, 0, 70, "s0"],
        [1, 1, 0, 0, 20, "s0"],
        [1, 2, 0, 0, 10, "s0"],
        [1, 0, 0, 0, 80, "s1"],
        [1, 1, 0, 0, 20, "s1"],
    ]
    formats = ["%d", "%d", "%d", "%d", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t_is():
    columns = ["id", "std_id", "normalize_by_std_id", "area_chromatogram", "filename"]
    types = [int, int, int, float, str]
    rows = [
        [2, None, 2, 100, "s0"],
        [2, 2, None, 400, "s0"],
        [2, None, None, 400, "s0"],
        [3, None, 2, 200, "s0"],
        [4, None, 2, 400, "s0"],
    ]
    formats = ["%d", "%d", "%d", "%.2e", "%s"]
    return Table.create_table(columns, types, formats, rows=rows)


@pytest.fixture
def t_idms_corr():
    columns = [
        "compound",
        "mf",
        "std_id",
        "normalize_by_std_id",
        "chromatogram",
        "filename",
    ]
    types = [str, str, int, int, MSChromatogram, str]
    rows = [
        ["x", "C7H3N3O3", None, 1, generate_chromatogram(50, 100, 1e6, 75, 5), "a"],
        [
            "x",
            "[13]CC6H3N3O3",
            1,
            None,
            generate_chromatogram(50, 100, 1e6, 75, 5),
            "a",
        ],
        [
            "glc",
            "C6H12O6",
            None,
            2,
            generate_chromatogram(150, 180, 1e6, 165, 2.5),
            "a",
        ],
        [
            "glc",
            "[13]C6H12O6",
            2,
            None,
            generate_chromatogram(150, 180, 1e6, 165, 2.5),
            "a",
        ],
        ["y", "C5H9N3O4", None, 1, generate_chromatogram(50, 100, 1e6, 75, 5), "a"],
        ["x", "C7H3N3O3", None, 1, generate_chromatogram(50, 100, 1e6, 75, 5), "b"],
        [
            "x",
            "[13]CC6H3N3O3",
            1,
            None,
            generate_chromatogram(50, 100, 1e5, 75, 5),
            "b",
        ],
        [
            "glc",
            "C6H12O6",
            None,
            2,
            generate_chromatogram(150, 180, 1e6, 165, 2.5),
            "b",
        ],
        [
            "glc",
            "[13]C6H12O6",
            2,
            None,
            generate_chromatogram(150, 180, 1e6, 165, 2.5),
            "b",
        ],
        ["y", "C5H9N3O4", None, 1, generate_chromatogram(50, 100, 1e6, 75, 5), "b"],
        ["gp", "C6H13O9P", None, 3, generate_chromatogram(200, 250, 1e10, 225, 5), "b"],
        [
            "gp",
            "[13]CC5H13O9P",
            3,
            None,
            generate_chromatogram(200, 250, 1e4, 225, 5),
            "b",
        ],
        ["gp", "C6H13O9P", None, 3, generate_chromatogram(200, 250, 1e9, 225, 5), "c"],
        [
            "gp",
            "[13]CC5H13O9P",
            3,
            None,
            generate_chromatogram(200, 250, 1e7, 225, 5),
            "c",
        ],
        [
            "gp",
            "[13]C6H13O9P",
            3,
            None,
            generate_chromatogram(200, 250, 1e7, 225, 5),
            "c",
        ],
    ]
    t = Table.create_table(columns, types, rows=rows)
    t.add_enumeration()
    t.add_column_with_constant_value("adduct_name", "M+H", str)
    t.add_column("mz", t.apply(mass.of, t.mf) + mass.p, MzType)
    t.add_column_with_constant_value("z", 1, int)
    t.add_column(
        "rtmax_chromatogram",
        t.apply(lambda v: max(v.rts), t.chromatogram),
        RtType,
        insert_after="chromatogram",
    )
    t.add_column(
        "rtmin_chromatogram",
        t.apply(lambda v: min(v.rts), t.chromatogram),
        RtType,
        insert_after="chromatogram",
    )
    quantification.integrate_chromatograms(t, "linear", in_place=True)
    return t


@pytest.fixture
def t_pqn():
    columns = "id", "area_chromatogram", "sample_type", "filename"
    types = int, float, float, str
    rows = [
        [0, 1, "sample", "S1"],
        [1, 2, "sample", "S1"],
        [2, 3, "sample", "S1"],
        [0, 2, "QC", "Q0"],
        [1, 4, "QC", "Q0"],
        [2, 4, "QC", "Q0"],
        [0, 2.5, "QC", "Q1"],
        [1, 4, "QC", "Q1"],
        [2, 6, "QC", "Q1"],
        [0, 2.5, "QC", "Q2"],
        [1, 4, "QC", "Q2"],
        [2, 6, "QC", "Q2"],
    ]
    return Table.create_table(columns, types, rows=rows)


def test_normalize_by_tic_0(t0, regtest):
    kwargs = {"sample_wise": False, "value_col": "area_chromatogram"}
    sfree.tic_normalize_peaks(t0, kwargs)
    print(t0, file=regtest)


def test_normalize_by_tic_1(t0):
    t0.drop_columns("filename")
    kwargs = {"sample_wise": True, "value_col": "area_chromatogram"}
    with pytest.raises(AssertionError):
        sfree.tic_normalize_peaks(t0, kwargs)


def test__normalize_0(t0):
    normalize._normalize(
        t0, peak_group_col="id", sample_wise=False, value_col="area_chromatogram"
    )
    print(t0.normalized_area_chromatogram.to_list())
    assert t0.normalized_area_chromatogram.to_list() == [100, None]
    # print(t0, file=regtest)


# sample wise test


def test__normalize_1(t0, t1):
    t = emzed.Table.stack_tables([t0, t1])
    normalize._normalize(t0, peak_group_col="id", value_col="area_chromatogram")
    normalize._normalize(t1, peak_group_col="id", value_col="area_chromatogram")
    normalize._normalize(t, peak_group_col="id", value_col="area_chromatogram")
    res = Table.stack_tables([t0, t1])
    comp = t.join(res, (t.id == res.id) & (t.filename == res.filename))
    print(comp.col_names)
    comp = comp.filter(comp.normalized_area_chromatogram.is_not_none())

    colnames = [
        "id_area_chromatogram",
        "normalization_area_chromatogram",
        "normalized_area_chromatogram",
    ]
    print(comp.extract_columns(*colnames))
    print(comp.extract_columns(*[c + "__0" for c in colnames]))
    for name in colnames:
        deltas = np.abs(
            np.array(comp[name].to_list(), dtype=float)
            - np.array(comp[name + "__0"].to_list()),
            dtype=float,
        )
        assert all(deltas < 1e-10)


def test_normalize_2(t2):
    normalize._normalize(t2, peak_group_col="id", value_col="area_chromatogram")
    is_ = t2.normalized_area_chromatogram.to_list()
    expected = [None, None]
    print(t2)
    assert is_ == expected


def test_normalize_3(t3):
    normalize._normalize(t3, peak_group_col="id", value_col="area_chromatogram")
    is_ = t3.normalized_area_chromatogram.to_list()
    print(t3)
    expected = [0.25, None, 1.0, None, None]
    assert is_ == expected


def test_normalize_4(t3):
    normalize._normalize(
        t3, peak_group_col="id", sample_wise=False, value_col="area_chromatogram"
    )
    is_ = t3.normalized_area_chromatogram.to_list()
    print(t3)
    expected = [0.625, None, 0.625, None, None]
    assert is_ == expected


def test_normalize_5(t_isotop):
    normalize._normalize(
        t_isotop,
        peak_group_col="pid",
        isotopologue_col="mi",
        value_col="area_chromatogram",
    )
    is_ = t_isotop.normalized_area_chromatogram.to_list()
    print(t_isotop)
    expected = [0.7, 0.2, 0.1, 0.8, 0.2]
    assert is_ == expected


def test_normalize_6(t_is):
    normalize._normalize(t_is, peak_group_col="id", value_col="area_chromatogram")
    is_ = t_is.normalized_area_chromatogram.to_list()
    print(t_is)
    expected = [0.25, None, None, 0.5, 1.0]
    assert is_ == expected


def test_normalize_7(t_isotop):
    t_isotop.drop_columns("std_id", "normalize_by_std_id")
    normalize._normalize(
        t_isotop,
        peak_group_col="pid",
        std_group_col="pid",
        norm_id_col="pid",
        isotopologue_col="mi",
        value_col="area_chromatogram",
    )
    is_ = t_isotop.normalized_area_chromatogram.to_list()
    print(t_isotop)
    expected = [0.7, 0.2, 0.1, 0.8, 0.2]
    assert is_ == expected


def test_normalize_9(t4):
    normalize._normalize(t4, peak_group_col="id", value_col="area_chromatogram")
    is_ = t4.normalized_area_chromatogram.to_list()
    print(t4)
    expected = [0.25, None, 1.0, None, None]
    assert is_ == expected


def test_normalize_10(t4):
    normalize._normalize(
        t4, peak_group_col="id", sample_wise=False, value_col="area_chromatogram"
    )
    is_ = t4.normalized_area_chromatogram.to_list()
    print(t4)
    expected = [0.625, None, 0.625, None, None]
    assert is_ == expected


def test_normalize_11(t5):
    normalize._normalize(t5, peak_group_col="id", value_col="area_chromatogram")
    is_ = t5.normalized_area_chromatogram.to_list()
    print(t5)
    expected = [0.25, None, 1.0, None, None]
    assert is_ == expected


def test_normalize_12(t5):
    normalize._normalize(
        t5, peak_group_col="id", sample_wise=False, value_col="area_chromatogram"
    )
    is_ = t5.normalized_area_chromatogram.to_list()
    print(t5)
    expected = [0.625, None, 0.625, None, None]
    assert is_ == expected


def test_normalize_15(t6):
    normalize._normalize(t6, peak_group_col="id")
    is_ = t6.normalized_area_chromatogram.to_list()
    print(t6)
    expected = [0.25, None, 900, 900, 400]
    assert is_ == expected


def _comp(v1, v2):
    if v1 is None and v2 is None:
        return True
    try:
        return abs(v1 - v2) < 1e-6
    except:
        return False


def test_pq_normalize_0(t_pqn):
    sfree._normalize_by_pq(t_pqn, value_col="area_chromatogram")
    x = t_pqn.filter(t_pqn.filename == "S1")
    is_ = dict(zip(x.id, x.pqn_area_chromatogram))
    expected = {0: 2, 1: 4, 2: 6}
    assert all([is_[key] == expected[key] for key in is_.keys()])
