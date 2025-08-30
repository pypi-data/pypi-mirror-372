# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 10:37:37 2024

@author: pkiefer
"""

import os
import pytest
import emzed
import numpy as np
from src.tadamz.calibration import calibrate as cal
from src.tadamz.in_out import load_config
from datetime import datetime
from collections import defaultdict
from src.tadamz.workflow import run_calibration

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def config():
    path = os.path.join(here, "data/test_calibrate_config.txt")
    return load_config(path)


@pytest.fixture
def t_conc():
    path = os.path.join(here, "data/concentration_table.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def t_sample():
    path = os.path.join(here, "data/sample_data_table.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def t_res():
    path = os.path.join(here, "data/result_table_test_cal.xlsx")
    return emzed.io.load_excel(path)


def test_extract_sample_type_0(t_res, t_sample, t_conc, config, regtest):
    t = cal.extract_sample_type(t_res, t_sample, t_conc, **config["calibrate"])
    print(t.to_pandas().to_string(), file=regtest)


def test_extract_sample_type_1(t_res, t_sample, t_conc, config):
    colnames = set(t_res.col_names)
    colnames.update(set(t_sample.col_names))
    colnames.update(set(t_conc.col_names))
    t = cal.extract_sample_type(t_res, t_sample, t_conc, **config["calibrate"])
    assert set(t.col_names).union(colnames) == set(t.col_names).intersection(colnames)


def test_unique_sample_files_0(t_res, t_sample, t_conc, config):
    t = cal.extract_sample_type(t_res, t_sample, t_conc, **config["calibrate"])
    is_ = cal.unique_sample_files(t, **config["calibrate"])
    assert is_ is None


def test_unique_sample_files_1(t_res, t_sample, t_conc, config):
    t = cal.extract_sample_type(t_res, t_sample, t_conc, **config["calibrate"])
    filename = t.filename.to_list()[0]
    t.replace_column_with_constant_value("filename", filename, str)
    with pytest.raises(AssertionError):
        cal.unique_sample_files(t, **config["calibrate"])


def test_calibrate_0(t_res, t_conc, t_sample, config, regtest):
    t = cal.build_calibration_table(t_res, t_conc, t_sample, config["calibrate"])
    t.drop_columns("calibration_date", "calibration_model")
    print(t.col_names)
    print(t.to_pandas().to_string(), file=regtest)


def test_calibrate_1(t_res, t_conc, t_sample, config):
    t = cal.build_calibration_table(t_res, t_conc, t_sample, config["calibrate"])
    is_ = t.calibration_date.unique_value()
    date = datetime.today().strftime("%Y-%m-%d")
    assert is_ == date


def test_calibrate_2(t_res, t_conc, t_sample, config):
    kwargs = config["calibrate"]
    kwargs["calibration_weight"] = "1/x"
    # kwargs["specific"]["ala"]["calibration_weight"] = "1/x"
    t = cal.build_calibration_table(t_res, t_conc, t_sample, kwargs)
    deltas = [abs(lod - 3 / 10 * loq) < 1e-10 for lod, loq in zip(t.LOD, t.LOQ)]
    assert all(deltas)


def test_calibrate_3(t_res, t_conc, t_sample, config):
    t_conc.replace_column(
        "calibration_weight",
        t_conc.calibration_weight.is_not_none().then_else("none", None),
        str,
    )
    # config["calibrate"]["specific"]["ala"]["calibration_weight"] = "none"
    t = cal.build_calibration_table(t_res, t_conc, t_sample, config["calibrate"])
    assert all(t.LOD.to_list())


def test_ca1librate_4(t_res, t_conc, t_sample, config, regtest):
    t = cal.build_calibration_table(t_res, t_conc, t_sample, config["calibrate"])
    t.drop_columns("calibration_date", "calibration_model")
    print(t.to_pandas().to_string(), file=regtest)
    spath = os.path.join(here, "data/test_save_t_cal.table")
    emzed.io.save_table(t, spath, overwrite=True)
    t1 = emzed.io.load_table(spath)
    print(t1.to_pandas().to_string(), file=regtest)


def test_calibrate_5(t_res, t_conc, t_sample, config, regtest):
    # test runs with minimal config
    kwargs = config["calibrate"]
    pop_keys = [key for key in kwargs.keys() if key.endswith("_col")]
    [kwargs.pop(key) for key in pop_keys]
    t = cal.build_calibration_table(t_res, t_conc, t_sample, kwargs)
    t.drop_columns("calibration_date", "calibration_model")
    print(t.to_pandas().to_string(), file=regtest)
    spath = os.path.join(here, "data/test_save_t_cal.table")
    t1 = emzed.io.load_table(spath)
    print(t1.to_pandas().to_string(), file=regtest)


# def test_prepare_calibration_table_evaluation_0(t_res, t_conc, t_sample, config):
#     t = cal.build_calibration_table(t_res, t_conc, t_sample, config["calibrate"])
#     assert "calibration_model" in t.col_names
#     cal.prepare_calibration_table_evaluation(
#         t, t_res, t_conc, t_sample, config["calibrate"]
#     )
#     assert set(t_conc.include) == {True}


def test_prepare_calibration_table_evaluation_1(t_res, t_conc, t_sample, config):
    t = cal.build_calibration_table(t_res, t_conc, t_sample, config["calibrate"])
    cal.prepare_calibration_table_evaluation(
        t, t_res, t_conc, t_sample, config["calibrate"]
    )
    t_res.add_column(
        "sample_type",
        t_res.filename.lookup(t_sample.filename, t_sample.sample_type),
        str,
    )
    t_res = t_res.filter(t_res.sample_type == "Sample", keep_view=True)
    d = defaultdict(set)
    for comp, value in zip(t_res.compound, t_res.normalized_area_chromatogram):
        d[comp].add(value)
    for comp, values in zip(t.compound, t.sample_normalized_area_chromatogram):
        expected = set(values)
        assert expected.intersection(d[comp]) == d[comp]


def test_prepare_calibration_table_evaluation_2(t_res, t_conc, t_sample, config):
    t = cal.build_calibration_table(t_res, t_conc, t_sample, config["calibrate"])
    cal.prepare_calibration_table_evaluation(
        t, t_res, t_conc, t_sample, config["calibrate"]
    )
    d = {}
    for comp, values, model in zip(
        t.compound, t.sample_normalized_area_chromatogram, t.calibration_model
    ):
        # model = cal.bcf.calibration_model_from_dict(mdict)
        concs = [model.get_amount(value).nominal_value for value in values]
        print(concs)
        d[comp] = set(concs)
    for comp, values in zip(t.compound, t.sample_amount):
        expected = set([v.nominal_value for v in values])
        assert expected.intersection(d[comp]) == d[comp]


def test_prepare_calibration_table_evaluation_3(t_res, t_conc, t_sample, config):
    t = cal.build_calibration_table(t_res, t_conc, t_sample, config["calibrate"])
    cal.prepare_calibration_table_evaluation(
        t, t_res, t_conc, t_sample, config["calibrate"]
    )
    d = {}
    for comp, values, model in zip(
        t.compound, t.sample_normalized_area_chromatogram, t.calibration_model
    ):
        concs = [model.get_amount(value).std_dev for value in values]
        print(concs)
        d[comp] = set(concs)
    for comp, values in zip(t.compound, t.sample_amount):
        expected = set([v.std_dev for v in values])
        assert expected.intersection(d[comp]) == d[comp]


@pytest.fixture
def config_is():
    path = os.path.join(here, "data/test_calibrate_config_is.txt")
    return load_config(path)


@pytest.fixture
def t_conc_is():
    path = os.path.join(here, "data/concentration_table_is.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def t_sample_is():
    path = os.path.join(here, "data/sample_data_table_istd.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def t_res_is():
    path = os.path.join(here, "data/result_table_test_cal_is.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def t_res_is_nones():
    path = os.path.join(here, "data/test_cal_is_only_nones.xlsx")
    return emzed.io.load_excel(path)


def test_extract_sample_type_is_0(t_res_is, t_sample_is, t_conc_is, config_is, regtest):
    t = cal.extract_sample_type(
        t_res_is, t_sample_is, t_conc_is, **config_is["calibrate"]
    )
    print(t.to_pandas().to_string(), file=regtest)


def test_extract_sample_type_is_1(t_res_is, t_sample_is, t_conc_is, config_is):
    colnames = set(t_res_is.col_names)
    colnames.update(set(t_sample_is.col_names))
    colnames.update(set(t_conc_is.col_names))
    t = cal.extract_sample_type(
        t_res_is, t_sample_is, t_conc_is, **config_is["calibrate"]
    )
    assert set(t.col_names).union(colnames) == set(t.col_names).intersection(colnames)


def test_calibrate_is_0(t_res_is, t_conc_is, t_sample_is, config_is, regtest):
    t = cal.build_calibration_table(
        t_res_is, t_conc_is, t_sample_is, config_is["calibrate"]
    )
    t.drop_columns("calibration_date", "calibration_model")
    print(t.to_pandas().to_string(), file=regtest)


def test_calibrate_is_1(t_res_is, t_conc_is, t_sample_is, config_is):
    t = cal.build_calibration_table(
        t_res_is, t_conc_is, t_sample_is, config_is["calibrate"]
    )
    is_ = t.calibration_date.unique_value()
    date = datetime.today().strftime("%Y-%m-%d")
    assert is_ == date


def test_calibrate_is_2(t_res_is, t_conc_is, t_sample_is, config_is):
    kwargs = config_is["calibrate"]
    kwargs["calibration_weight"] = "1/x"
    # kwargs["specific"]= {"ala":{"calibration_weight" : "1/x"}}
    t = cal.build_calibration_table(t_res_is, t_conc_is, t_sample_is, kwargs)
    # fit of VEGTAFVIFGIQDGEQR is mostly a horizontal line popt = [-1.47093838e-03  2.44904333e+00]
    t = t.filter((t.compound == "VEGTAFVIFGIQDGEQR") == False)
    deltas = [abs(lod - 3 / 10 * loq) < 1e-10 for lod, loq in zip(t.LOD, t.LOQ)]
    assert all(deltas)
    # assert set(t.LOD).pop() == set(t.LOQ).pop() == None


def test_calibrate_is_3(t_res_is, t_conc_is, t_sample_is, config_is):
    config_is["calibrate"]["calibration_weight"] = "none"
    t = cal.build_calibration_table(
        t_res_is, t_conc_is, t_sample_is, config_is["calibrate"]
    )
    t = t.filter((t.compound == "VEGTAFVIFGIQDGEQR") == False)
    print(t)
    print(t.calibration_model.to_list()[-2].popt)
    assert all(t.LOD.to_list())


def test_calibrate_is_4(t_res_is, t_conc_is, t_sample_is, config_is, regtest):
    t = cal.build_calibration_table(
        t_res_is, t_conc_is, t_sample_is, config_is["calibrate"]
    )
    t.drop_columns("calibration_date", "calibration_model")
    print(t.to_pandas().to_string(), file=regtest)
    spath = os.path.join(here, "data/test_save_t_cal_is.table")
    emzed.io.save_table(t, spath, overwrite=True)
    t1 = emzed.io.load_table(spath)
    print(t1.to_pandas().to_string(), file=regtest)


def test_calibrate_is_5(t_res_is_nones, t_conc_is, t_sample_is, config_is):
    # result table contains single compound with only none vallues
    t = cal.build_calibration_table(
        t_res_is_nones, t_conc_is, t_sample_is, config_is["calibrate"]
    )
    model = t.calibration_model.unique_value()
    print(model.params)
    is_ = model.get_amount(5.0)
    assert is_ is None


# def test_prepare_calibration_table_evaluation_is_0(
#     t_res_is, t_conc_is, t_sample_is, config_is
# ):
#     t = cal.build_calibration_table(
#         t_res_is, t_conc_is, t_sample_is, config_is["calibrate"]
#     )
#     cal.prepare_calibration_table_evaluation(
#         t, t_res_is, t_conc_is, t_sample_is, config_is["calibrate"]
#     )
#     assert set(t_conc_is.include) == {True}


def test_prepare_calibration_table_evaluation_is_1(
    t_res_is, t_conc_is, t_sample_is, config_is
):
    kwargs = config_is["calibrate"]
    t = cal.build_calibration_table(t_res_is, t_conc_is, t_sample_is, kwargs)
    cal.prepare_calibration_table_evaluation(
        t, t_res_is, t_conc_is, t_sample_is, kwargs
    )
    t_res_is.add_column(
        "sample_type",
        t_res_is.filename.lookup(t_sample_is.filename, t_sample_is.sample_type),
        str,
    )
    t_res = t_res_is.filter(
        (t_res_is.sample_type == "Sample") & t_res_is[kwargs["std_group_col"]].is_none()
    )
    t_res = cal._remove_duplicates(
        t_res, kwargs["compound_col"], kwargs["value_col"], kwargs["source_col"]
    )
    d = defaultdict(set)
    # print(t.to_pandas().to_string(), file=regtest)
    for comp, value in zip(t_res.compound, t_res.normalized_area_chromatogram):
        d[comp].add(value)
    print(list(zip(t.compound, t.sample_normalized_area_chromatogram)))
    # print(d)
    for comp, values in zip(t.compound, t.sample_normalized_area_chromatogram):
        # n = values.shape
        # values = values.reshape(m * n)
        expected = set(values)

        assert expected.intersection(d[comp]) == d[comp]


def test_prepare_calibration_table_evaluation_is_2(
    t_res_is, t_conc_is, t_sample_is, config_is
):
    kwargs = config_is["calibrate"]
    t = cal.build_calibration_table(t_res_is, t_conc_is, t_sample_is, kwargs)
    cal.prepare_calibration_table_evaluation(
        t, t_res_is, t_conc_is, t_sample_is, kwargs
    )
    d = {}
    for comp, values, model in zip(
        t.compound,
        t.sample_normalized_area_chromatogram,
        t.calibration_model,
    ):
        # model = cal.bcf.calibration_model_from_dict(mdict)
        concs = [model.get_amount(value).nominal_value for value in values]
        print(concs)
        d[comp] = set(concs)
    for comp, values in zip(t.compound, t.sample_amount):
        expected = set([v.nominal_value for v in values])
        assert expected.intersection(d[comp]) == d[comp]


def test_prepare_calibration_table_evaluation_is_3(
    t_res_is, t_conc_is, t_sample_is, config_is
):
    kwargs = config_is["calibrate"]
    t = cal.build_calibration_table(t_res_is, t_conc_is, t_sample_is, kwargs)
    cal.prepare_calibration_table_evaluation(
        t, t_res_is, t_conc_is, t_sample_is, kwargs
    )
    d = {}
    for comp, values, model in zip(
        t.compound,
        t.sample_normalized_area_chromatogram,
        t.calibration_model,
    ):
        # model = cal.bcf.calibration_model_from_dict(mdict)
        concs = [model.get_amount(value).std_dev for value in values]
        print(concs)
        d[comp] = set(concs)
    for comp, values in zip(t.compound, t.sample_amount):
        expected = set([v.std_dev for v in values])
        assert expected.intersection(d[comp]) == d[comp]


def test_prepare_calibration_table_evaluation_is_4(
    t_res_is, t_conc_is, t_sample_is, config_is
):
    t_res_is.replace_column(
        "normalized_area_chromatogram",
        (
            (t_res_is.filename == "210205_A1.mzML") & t_res_is.compound == "CQSWSSMTPHR"
        ).then_else(None, t_res_is.normalized_area_chromatogram),
        float,
    )
    kwargs = config_is["calibrate"]
    t = cal.build_calibration_table(t_res_is, t_conc_is, t_sample_is, kwargs)
    cal.prepare_calibration_table_evaluation(
        t, t_res_is, t_conc_is, t_sample_is, kwargs
    )
    d = {}
    for comp, values, model in zip(
        t.compound,
        t.sample_normalized_area_chromatogram,
        t.calibration_model,
    ):
        # model = cal.bcf.calibration_model_from_dict(mdict)
        concs = [model.get_amount(value).std_dev for value in values]
        print(concs)
        d[comp] = set(concs)
    for comp, values in zip(t.compound, t.sample_amount):
        expected = set([v.std_dev for v in values])
        assert expected.intersection(d[comp]) == d[comp]


def test_prepare_calibration_table_evaluation_is_5(
    t_res_is, t_conc_is, t_sample_is, config_is
):
    t_sample_is = t_sample_is.filter(t_sample_is.sample_type == "Standard")
    kwargs = config_is["calibrate"]
    t = cal.build_calibration_table(t_res_is, t_conc_is, t_sample_is, kwargs)
    cal.prepare_calibration_table_evaluation(
        t, t_res_is, t_conc_is, t_sample_is, kwargs
    )
    for values, concs in zip(t.sample_normalized_area_chromatogram, t.sample_amount):
        assert values.shape == concs.shape == (0,)


def test_run_calibration_is_0(t_res_is, t_conc_is, t_sample_is, config_is, regtest):
    t = run_calibration(t_res_is, t_conc_is, t_sample_is, config_is)
    t.drop_columns("calibration_date", "calibration_model")
    print(t.to_pandas().to_string(), file=regtest)


def test_run_calibration_is_1(t_res_is, t_conc_is, t_sample_is, config_is, regtest):
    kwargs = config_is["calibrate"]
    pop_keys = [key for key in kwargs.keys() if key.endswith("_col")]
    [kwargs.pop(key) for key in pop_keys]
    t = run_calibration(t_res_is, t_conc_is, t_sample_is, config_is)
    t.drop_columns("calibration_date", "calibration_model")
    print(t.to_pandas().to_string(), file=regtest)


@pytest.fixture
def t_res_ref():
    path = os.path.join(here, "data/result_table_ref.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def t_sample_ref():
    path = os.path.join(here, "data/sample_data_table_ref.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def t_conc_ref():
    path = os.path.join(here, "data/concentration_table_ref_msrev.xlsx")
    return emzed.io.load_excel(path)


def test_run_calibration_ref(t_res_ref, t_sample_ref, t_conc_ref, config_is, regtest):
    t = run_calibration(t_res_ref, t_conc_ref, t_sample_ref, config_is)
    model = t.calibration_model.to_list()[0]
    popt = np.array([v.nominal_value for v in model.params])
    expected = np.array([0.1097278, 0.00875458])
    assert np.all(np.abs(popt - expected) < 1e-8)
