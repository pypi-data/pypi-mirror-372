# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:37:37 2024

@author: pkiefer
"""

import os
import pytest
import emzed
import numpy as np
from src.tadamz.in_out import load_tadamz_table
from src.tadamz import quantify as qu
from src.tadamz.in_out import dict_to_model

# from src.targeted_wf import in_out
from src.tadamz.workflow import postprocess_result_table

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def config():
    config = {
        "quantify": {
            "sample_id_col": "sample_name",
            "compound_col": "compound",
            "amount_col": "concentration",
            "value_col": "normalized_area_chromatogram",
            "unit_col": "unit",
            "source_col": "filename",
            "sample_type_col": "sample_type",
        },
        "postprocessing1": ["quantify"],
        "postprocessings": ["postprocessing1"],
    }
    return config


@pytest.fixture
def t_cal():
    path = os.path.join(here, "data/calibration_table.table")
    return load_tadamz_table(path)


@pytest.fixture
def t_res():
    path = os.path.join(here, "data/result_table_test_cal.xlsx")
    return emzed.io.load_excel(path)


def test_quantify_0(t_res, t_cal, config, regtest):
    model = t_cal.calibration_model.to_list()[0]
    print(model.get_amount(2.5))
    t = qu.quantify(t_res, config["quantify"], t_cal)
    t.drop_columns("calibration_model")
    print(t.to_pandas().to_string(), file=regtest)


def test_quantify_1(t_res, t_cal, config, regtest):
    with pytest.raises(AssertionError):
        qu.quantify(t_res, config["quantify"])


def test_quantify_2(t_res, t_cal, config):
    t = postprocess_result_table(t_res, config, 0, t_cal)
    print(t.col_names)
    assert "concentration_nominal" in t.col_names


def test_quantify_3(t_res, t_cal, config):
    t_cal = t_cal.filter(t_cal.compound == "lysine")
    t = qu.quantify(t_res, config["quantify"], t_cal)
    t = t.filter(t.compound == "proline")
    is_ = t.calibration_model.to_list()[0].__dict__
    print(is_)
    expected = {
        "model_name": "linear",
        "popt": [None, None],
        "perr": [None, None],
        "compound": "proline",
        "xvalues": np.array([], dtype=float),
        "yvalues": np.array([[]], dtype=float),
        "unit": "uM",
        "lod": None,
        "loq": None,
    }
    comps = []
    for key in expected.keys():
        if isinstance(expected[key], np.ndarray):
            comps.append(np.all(is_[key] == expected[key]))
        else:
            comps.append(is_[key] == expected[key])
    assert all(comps)


def test_quantify_5(t_res, t_cal, config, regtest):
    for column in ["calibration_model"]:
        t_res.add_column(
            column, t_res.compound.lookup(t_cal.compound, t_cal[column]), object
        )
    t = qu.quantify(t_res, config["quantify"])
    t.drop_columns("calibration_model")
    print(t.to_pandas().to_string(), file=regtest)


def test__get_amount(capsys):
    d = {
        "model_name": "quadratic",
        "sample_names": np.array([["a", "b", "c", "d"]]).T,
        "compound": "proline",
        "calibration_weight": "none",
        "xvalues": np.array([2.0, 3.0, 4.0, 5.0]),
        "yvalues": np.array([[8.0, 14.0, 22.0, 32.0]]).T,
        "unit": "uM",
    }
    model = dict_to_model(d)
    x = qu._get_amount(0.5, model)
    out, error = capsys.readouterr()
    assert out == f"model results no real value for {model.compound}\n"
