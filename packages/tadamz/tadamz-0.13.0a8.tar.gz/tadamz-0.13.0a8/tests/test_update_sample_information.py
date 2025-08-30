# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:57:53 2024

@author: pkiefer
"""

import emzed
import pytest
import os
from src.tadamz import update_sample_information as usi

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def t_result():
    pm = emzed.io.load_peak_map(os.path.join(here, "data", "mrm_data1.mzml"))
    colnames = "id", "filename", "peakmap"
    types = int, str, emzed.PeakMap
    rows = [[1, "A", pm], [2, "A", pm], [1, "B", pm], [2, "B", pm]]
    return emzed.Table.create_table(colnames, types, rows=rows)


@pytest.fixture
def t_sample():
    colnames = "filename", "sample_name"
    types = str, str
    rows = [["A", "abc"], ["B", "def"]]
    return emzed.Table.create_table(colnames, types, rows=rows)


def test__update_sample_information_0(t_result, t_sample):
    usi._update_sample_information(t_result, t_sample)
    is_ = ["abc", "abc", "def", "def"]
    print(t_result)
    assert t_result.sample_name.to_list() == is_


def test__update_sample_information_1(t_result):
    uid = t_result.unique_id
    usi._update_sample_information(t_result, None)
    assert t_result.unique_id == uid
