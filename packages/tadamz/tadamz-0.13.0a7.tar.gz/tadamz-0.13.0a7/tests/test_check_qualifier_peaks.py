# -*- coding: utf-8 -*-
"""
Created on Fri Apr  4 08:36:10 2025

@author: pkiefer
"""
import pytest
from src.tadamz import check_qualifier_peaks as cqp
from emzed import Table


@pytest.fixture
def qtable0():
    colnames = [
        "compound",
        "area_chromatogram",
        "filename",
        "is_qualifier",
        "qualifier_ratio_min",
        "qualifier_ratio_max",
    ]
    types = [str, float, str, bool, float, float]
    rows = [
        ["ala", 1e5, "s1", False, None, None],
        ["ala", 5e4, "s1", True, 1.9, 2.1],
        ["ala", 1e5, "s1", True, 0.7, 0.9],
        ["ala", 6e6, "s2", None, None, None],
    ]
    t = Table.create_table(colnames, types, rows=rows)
    t.add_enumeration()
    return t


@pytest.fixture
def qtable1():
    colnames = [
        "compound",
        "area_chromatogram",
        "filename",
        "is_qualifier",
        "qualifier_ratio_min",
        "qualifier_ratio_max",
    ]
    types = [str, float, str, bool, float, float]
    rows = [
        ["ala", 1e5, "s1", False, None, None],
        ["ala", 5e4, "s1", False, None, None],
        ["ala", 1e5, "s1", True, 0.7, 0.9],
        ["ala", 6e6, "s2", None, None, None],
    ]
    t = Table.create_table(colnames, types, rows=rows)
    t.add_enumeration()
    return t


def test_check_qualifier_peaks_0(qtable0):
    kwargs = {}
    t = cqp.check_qualifier_peaks(qtable0, kwargs)
    is_ = dict(zip(t.id, t.qualifier_quality_check))
    exp = {0: None, 1: "passed", 2: "failed", 3: None}
    assert all([is_[key] == exp[key] for key in exp.keys()])


def test_check_qualifier_peaks_1(qtable1):
    with pytest.raises(AssertionError):
        cqp.check_qualifier_peaks(qtable1, {})


def test_check_qualifier_peaks_2(qtable0):
    t = qtable0[:0].consolidate()
    cqp.check_qualifier_peaks(t, {})
    expected_columns = {"qualifier_quality_check", "qualifier_ratio", "color"}
    assert expected_columns - set(t.col_names) == set([])


def test_check_qualifier_peaks_3(qtable0):
    kwargs = {}

    def _fun(item):
        if isinstance(item, dict):
            return item.pop("qualifier_quality_check")

    t = cqp.check_qualifier_peaks(qtable0, kwargs)
    is_ = dict(zip(t.id, t.color))
    is_ = {key: _fun(value) for key, value in is_.items()}
    exp = {0: None, 1: "#00FF00", 2: "#FF0000", 3: None}
    assert all([is_[key] == exp[key] for key in exp.keys()])
