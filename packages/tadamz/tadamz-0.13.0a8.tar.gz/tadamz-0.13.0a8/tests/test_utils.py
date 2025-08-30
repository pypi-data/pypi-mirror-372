# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 16:34:45 2024

@author: pkiefer
"""

from src.tadamz import utils as ut
from emzed.ms_data.peak_map import MSChromatogram, Chromatogram, PeakMap
import pickle
import os
import emzed
import pytest

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


def test_color_column_by_value_0():
    v2c = {2: None}
    t = emzed.to_table("a", [0, 1], int)
    ut.color_column_by_value(t, "a", v2c)
    assert all([d.get("a") == "#FFFFF" for d in t.color])


def test_color_column_by_value_1():
    v2c = {0: "#FF0000", 1: "#FFFF00"}
    t = emzed.to_table("a", [0, 1], int)
    ut.color_column_by_value(t, "a", v2c)
    is_ = dict(zip(t.a, [d.get("a") for d in t.color]))
    assert all([is_[key] == v2c[key] for key in v2c.keys()])


def test_color_column_by_value_2():
    v2c = {0: "#FF0000", 1: "#FFFF00"}
    t = emzed.to_table("a", [0, 1], int)
    t.add_column("b", [1, 0], int)
    ut.color_column_by_value(t, "b", v2c)
    assert all([set(d.keys()) - set(["a", "b"]) == set([]) for d in t.color])


def test_color_column_by_value_3():
    v2c = {2: None}
    t = emzed.to_table("a", [0, 1], int)
    ut.color_column_by_value(t, "a", v2c)
    col2format = dict(zip(t.col_names, t.col_formats))
    assert col2format["color"] is None


@pytest.fixture
def table():
    columns = "a", "b", "c"
    types = int, int, int
    rows = [[0, 0, 0], [1, 2, 3]]
    t1 = emzed.Table.create_table(columns, types, rows=rows)
    t2 = t1.copy()
    t2.add_column("d", [4, 5], int)
    t2.replace_column("b", [1, 2], int)
    return t1.join(t2, (t1.a == t2.a))


@pytest.fixture
def table_1():
    columns = "a", "b", "c"
    types = int, int, int
    rows = [[0, 0, 0], [1, 2, 3]]
    t1 = emzed.Table.create_table(columns, types, rows=rows)
    t2 = t1.copy()
    t = t1.join(t2, (t1.a == t2.a))
    t3 = t1.copy()
    t3.add_column("d", [4, 5], int)
    t3.replace_column("b", [1, 2], int)
    return t.join(t3, (t.a == t3.a))


@pytest.fixture
def chromatogram():
    path = os.path.join(data_folder, "test_chromatogram.pickle")
    with open(path, "rb") as fp:
        chrom = pickle.load(fp)
    return chrom


@pytest.fixture
def mschromatogram():
    path = os.path.join(data_folder, "test_mschromatogram.pickle")
    with open(path, "rb") as fp:
        chrom = pickle.load(fp)
    return chrom


@pytest.fixture
def pm():
    path = os.path.join(data_folder, "mrm_data_large.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def table_2(chromatogram, mschromatogram, pm):
    columns = "a", "b", "c", "chromatogram", "mschromatogram"
    types = int, int, int, MSChromatogram, MSChromatogram
    rows = [[0, 0, 0, chromatogram, mschromatogram], [1, 2, 3, None, None]]
    t1 = emzed.Table.create_table(columns, types, rows=rows)
    t2 = t1.copy()
    t1.add_column_with_constant_value("peakmap", pm, PeakMap)
    t2.add_column_with_constant_value("peakmap", pm, PeakMap)
    t2.add_column("d", [4, 5], int)
    t2.replace_column("b", [1, 2], int)
    return t1.join(t2, (t1.a == t2.a))


def test_cleanup_join_0(table):
    ut.cleanup_join(table)
    expected = set(["a", "b", "c", "b__0", "d"])
    assert set(table.col_names) - expected == expected - set(table.col_names)


def test_cleanup_last_join_0(table):
    ut.cleanup_last_join(table)
    expected = set(["a", "b", "c", "b__0", "d"])
    assert set(table.col_names) - expected == expected - set(table.col_names)


def test_cleanup_last_join_1(table_1):
    ut.cleanup_last_join(table_1)
    expected = set(["a", "b", "c", "a__0", "b__0", "c__0", "b__1", "d"])
    assert set(table_1.col_names) - expected == expected - set(table_1.col_names)


def test_cleanup_last_join_2(table_2):
    ut.cleanup_last_join(table_2)
    expected = expected = set(
        ["a", "b", "c", "chromatogram", "mschromatogram", "peakmap", "b__0", "d"]
    )
    assert set(table_2.col_names) - expected == expected - set(table_2.col_names)
