# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 16:29:16 2023

@author: pkiefer
"""
import emzed
import os
import pytest
from src.tadamz import create_random_forest_peak_classifier as rfpc
from src.tadamz import extract_peaks as ep
from src.tadamz import in_out
from src.tadamz.scoring import peak_metrics as upm

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


# @pytest.fixture
# def cmpwf_config():
#     # shared example workflow config
#     path = os.path.join(data_folder, "test_complete_workflow_config.txt")
#     config = in_out.load_config(path)
#     config['classify_peaks']['scoring_model_params']['path_to_folder'] = data_folder
#     return config

# @pytest.fixture
# def cmpwf_pt():
#     path = os.path.join(data_folder, "compl_wf_target_table.xlsx")
#     return in_out.load_targets_table(path)


# @pytest.fixture
# def build_test_table(cmpwf_config, cmpwf_pt):
#     path = os.path.join(data_folder, 'kuebler_mzml', '210205_H*.mzML')
#     samples = emzed.io.load_peak_maps(path)
#     t = ep.extract_peaks(cmpwf_pt, samples, cmpwf_config['extract_peaks'])
#     upm.update_metrics(t)
#     spath = os.path.join(data_folder, 'test_crfp_input.table')
#     emzed.io.save_table(t, spath)
#     return t


@pytest.fixture
def _t():
    return emzed.to_table("x", [1, 2], int)


@pytest.fixture
def _path_to_table():
    return os.path.join(data_folder, "classification_table_chromatogram.table")


@pytest.fixture
def kwargs_chrom():
    d = {}
    d["classifier_name"] = "test_classifier"
    d["inspect"] = False
    d["path_to_table"] = os.path.join(data_folder, "test_crfp_input.table")
    d["path_to_folder"] = data_folder
    d["ms_data_type"] = "MS_Chromatogram"
    d["score_col"] = "peaks_quality_score"
    d["overwrite"] = True
    return d


# @pytest.fixture
# def kwargs_pm():
#     d = {}
#     d["classifier_name"] = "test_classifier"
#     d["inspect"] = False
#     d["path_to_table"] = os.path.join(data_folder, "classification_table_peakmap.table")
#     d["path_to_folder"] = data_folder
#     d["ms_data_type"] = "Spectra"
#     d["score_col"] = "peaks_quality_score"
#     d["overwrite"] = True
#     return d


def test__update_score_column_0(_t):
    rfpc._update_score_column(_t, "score")
    is_ = _t.score.to_list()
    assert is_ == [0, 0]


def test__update_score_column_1(_t):
    _t.add_enumeration("score")
    rfpc._update_score_column(_t, "score")
    is_ = _t.score.to_list()
    assert is_ == [0, 1]


def test__get_table_0():
    with pytest.raises(AssertionError):
        rfpc._get_table(None, None)


def test__get_table_1(_t, _path_to_table):
    with pytest.raises(AssertionError):
        rfpc._get_table(_path_to_table, _t)


def test__get_table_2(_t):
    is_ = rfpc._get_table(None, _t)
    assert is_ == _t


def test__get_table_3(_path_to_table):
    is_ = rfpc._get_table(_path_to_table, None)
    assert isinstance(is_, emzed.Table)


def test_generate_peak_classifier_0(kwargs_chrom):
    path = os.path.join(data_folder, "test_classifier.pickle")
    if os.path.exists(path):
        os.remove(path)
    rfpc.generate_peak_classifier(**kwargs_chrom)
    assert os.path.exists(path)
