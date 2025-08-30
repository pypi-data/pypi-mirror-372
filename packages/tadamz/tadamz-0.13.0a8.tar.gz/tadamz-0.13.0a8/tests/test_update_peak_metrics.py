# -*- coding: utf-8 -*-
"""
Created on Mon Dec 11 17:36:03 2023

@author: pkiefer
"""

from src.tadamz.scoring import peak_metrics as upm
import os
import emzed
import pytest

here = os.path.abspath(os.path.dirname(__file__))


class Model:
    def __init__(self, model_name, rts, ints):
        self.model_name = "no_integration"
        self.rts = rts
        self.intensities = ints

    def graph(self):
        return self.rts, self.intensities


@pytest.fixture
def table():
    spath = os.path.join(here, "data", "t_metrics.table")
    t = emzed.io.load_table(spath)
    return t


def test_update_metrics_0(table):
    # 1.  zero peak
    t = table[:1].consolidate()
    upm.update_metrics(t)
    colnames = (
        "zigzag_index",
        "gaussian_similarity",
        "max_apex_boundery_ratio",
        "sharpness",
        "tpsar",
        "no_spectra",
    )
    is_ = [t[col].to_list()[0] for col in colnames]
    expected = [None, None, None, None, None, 0]
    assert is_ == expected


def test_update_metrics_1(table, regtest):
    upm.update_metrics(table)
    print(table, file=regtest)


@pytest.fixture
def model():
    return Model("no_integration", [], [])


def test_count_spectra(model):
    assert upm.count_spectra(model) == 0
