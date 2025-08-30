# -*- coding: utf-8 -*-
"""
Created on Fri Sep 27 15:35:23 2024

@author: pkiefer
"""

import pytest
import emzed
from src.tadamz import run_workflow as rwf
from src.tadamz import run_calibration as rcal
from src.tadamz import postprocess_result_table as pprt
from src.tadamz import in_out
from glob import glob
import os

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


@pytest.fixture
def pt_srm():
    path = os.path.join(data_folder, "targets_table_srm.xlsx")
    return in_out.load_targets_table(path)


@pytest.fixture
def pt_prm():
    path = os.path.join(data_folder, "targets_prm_pos.xlsx")
    return in_out.load_targets_table(path)


@pytest.fixture
def exwf_pt():
    path = os.path.join(data_folder, "exwf_target_table.xlsx")
    return in_out.load_targets_table(path)


@pytest.fixture
def cmpwf_pt():
    path = os.path.join(data_folder, "compl_wf_target_table.xlsx")
    return in_out.load_targets_table(path)


@pytest.fixture
def samples_srm():
    path = os.path.join(data_folder, "mrm_data*.mzml")
    return glob(path)


@pytest.fixture
def samples_prm():
    path = os.path.join(data_folder, "test_wf_prm*.mzML")
    return glob(path)


@pytest.fixture
def exwf_samples():
    path = os.path.join(data_folder, "kuebler_mzml", "*.mzML")
    return glob(path)


@pytest.fixture
def config_srm():
    path = os.path.join(data_folder, "test_mrm_config.txt")
    config = in_out.load_config(path)
    config["classify_peaks"]["scoring_model_params"]["path_to_folder"] = data_folder
    return config


@pytest.fixture
def minimal_config_srm():
    path = os.path.join(data_folder, "test_mrm_minimal_config.txt")
    config = in_out.load_config(path)
    config["classify_peaks"]["scoring_model_params"]["path_to_folder"] = data_folder
    return config


@pytest.fixture
def exwf_config():
    # shared example workflow config
    path = os.path.join(data_folder, "test_example_workflow_config.txt")
    config = in_out.load_config(path)
    config["classify_peaks"]["scoring_model_params"]["path_to_folder"] = data_folder
    return config


@pytest.fixture
def cmpwf_config():
    # shared example workflow config
    path = os.path.join(data_folder, "test_complete_workflow_config.txt")
    config = in_out.load_config(path)
    config["classify_peaks"]["scoring_model_params"]["path_to_folder"] = data_folder
    return config


@pytest.fixture
def config_prm():
    path = os.path.join(data_folder, "test_config_prm.txt")
    config = in_out.load_config(path)
    config["classify_peaks"]["scoring_model_params"]["path_to_folder"] = data_folder
    return config


@pytest.fixture
def cal_data_srm():
    path = os.path.join(data_folder, "test_calibration_data_mrm.table")
    return in_out.load_tadamz_table(path)


@pytest.fixture
def config_srm_pp(config_srm):
    config_srm["pq_normalize_peaks"] = {}
    config_srm["postprocessing1"].append("pq_normalize_peaks")
    return config_srm


@pytest.fixture
def cal_data_prm():
    path = os.path.join(data_folder, "test_calibration_data_prm_pos.table")
    return in_out.load_tadamz_table(path)


@pytest.fixture
def exwf_cal_table():
    path = os.path.join(data_folder, "exwf_calibration_table.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def cmpwf_cal_table():
    path = os.path.join(data_folder, "cmpwf_calibration_table.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def exwf_sample_table():
    path = os.path.join(data_folder, "exwf_sample_table.xlsx")
    return emzed.io.load_excel(path)


@pytest.fixture
def result():
    path = os.path.join(data_folder, "test_processing_steps_changed_rows.table")
    return in_out.load_tadamz_table(path)


def test_run_workflow_0(pt_srm, samples_srm, config_srm, cal_data_srm, regtest):
    print(cal_data_srm.col_names)
    t = rwf(pt_srm, samples_srm, config_srm, calibration_table=cal_data_srm)
    print(t.meta_data)
    print(t, file=regtest)


def test_run_workflow_1(pt_srm, samples_srm, config_srm, cal_data_srm):
    print(cal_data_srm.col_names)
    t = rwf(pt_srm, samples_srm, config_srm, calibration_table=cal_data_srm)
    name2format = dict(zip(t.col_names, t.col_formats))
    names = "area_chromatogram", "rmse_chromatogram"
    expected = [name2format[n] == "%.2e" for n in names]
    assert all(expected)


def test_run_workflow_2(pt_srm, samples_srm, minimal_config_srm, cal_data_srm, regtest):
    t = rwf(pt_srm, samples_srm, minimal_config_srm, calibration_table=cal_data_srm)
    print(t, file=regtest)


def test_run_workflow_3(pt_prm, samples_prm, config_prm, cal_data_prm, regtest):
    t = rwf(pt_prm, samples_prm, config_prm, calibration_table=cal_data_prm)
    print(t, file=regtest)


def test_postprocess_result_table_0(result, config_srm):
    t = pprt(result, config_srm)
    print(result.col_names)
    t1 = pprt(result, config_srm, process_only_tracked_changes=True)
    is_ = dict(zip(t1.row_id, t1.normalized_area_chromatogram))
    exp = dict(zip(t.row_id, t.normalized_area_chromatogram))

    def _comp(v1, v2):
        if v1 is None and v2 is None:
            return True
        return abs(v1 - v2) / v2 < 1e-16

    assert all([_comp(is_[key], exp[key]) for key in exp.keys()])


def test_postprocess_result_table_1(result, config_srm_pp):
    print(config_srm_pp)
    with pytest.raises(AssertionError):
        pprt(result, config_srm_pp, process_only_tracked_changes=True)


def test_run_complete_workflow(
    cmpwf_pt, exwf_samples, cmpwf_config, cmpwf_cal_table, exwf_sample_table, regtest
):
    t = rwf(cmpwf_pt, exwf_samples, cmpwf_config, sample_table=exwf_sample_table)
    t_cal = rcal(t, cmpwf_cal_table, exwf_sample_table, cmpwf_config)
    t = pprt(t, cmpwf_config, calibration_table=t_cal)
    t = t[:25].consolidate()
    # in_out.save_twf_table(
    #     t, r"C:\temp_data\test_targeted_wf\test_run_complete_wf.table", overwrite=True
    # )
    print(t, file=regtest)
