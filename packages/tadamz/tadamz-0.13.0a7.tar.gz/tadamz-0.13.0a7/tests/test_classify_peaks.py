# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 09:22:40 2023

@author: pkiefer
"""
import pytest
import emzed
import pickle
import os
import numpy as np
from emzed import MzType, RtType

# from src.targeted_wf import extract_peaks as ep
from src.tadamz import classify_peaks as cp
from src.tadamz.scoring import random_forest_peak_classification as rfc
from src.tadamz.extract_peaks import extract_peaks
from sklearn.ensemble import RandomForestClassifier

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


@pytest.fixture
def kwargs():
    kwargs = {
        "scoring_model": "random_forest_classification",
        "scoring_model_params": {
            "classifier_name": "test_peak_classifier",
            "path_to_folder": data_folder,
            "ms_data_type": "MS_Chromatogram",
        },
    }
    return kwargs


@pytest.fixture
def table():
    spath = os.path.join(here, "data", "classification_table_chromatogram.table")
    t = emzed.io.load_table(spath)
    return t


# @pytest.fixture
# def table():
#     tt = emzed.io.load_excel(os.path.join(data_folder, 'targets_table_srm.xlsx'))
#     pms = [emzed.io.load_peak_map(os.path.join(data_folder, 'mrm_data_large.mzml'))]
#     kwargs = {
#         'ms_level': 2,
#         'mz_tol_abs': 0.3,
#         'mz_tol_rel': 0.0,
#         'precursor_mz_tol': 0.3,
#     'peak_width_col': 'rt_window_size',
#     'subtract_baseline' : True,
#     'integration_algorithm': 'linear',
#     'ms_data_type': 'MS_Chromatogram'}
# t = extract_peaks(tt, pms, kwargs)
# spath = os.path.join(here, "data", "classification_table_chromatogram.table")
# emzed.io.save_table(t, spath, overwrite=True)
# return t


@pytest.fixture
def table1():
    spath = os.path.join(here, "data", "classification_table_ms1.table")
    t = emzed.io.load_table(spath)
    return t


# @pytest.fixture
# def pt_ms1():
#     columns = (
#         "precursor_mz",
#         "mz",
#         "mzmin",
#         "mzmax",
#         "rt",
#         "rtmin",
#         "rtmax",
#         "rt_max_shift",
#     )
#     types = [MzType, MzType, MzType, MzType, RtType, RtType, RtType, float]
#     rows = [
#         [None, 175.11895, 175.11495, 175.12295, 332.4, 330.0, 339.0, 5.0],
#         [None, 148.06043, 148.0564, 148.0644, 296.4, 291.530574, 298.62465, 5.0],
#         [None, 134.0448, 134.0408, 134.0488, 316.2, 312.287562, 323.322864, 5.0],
#     ]
#     t = emzed.Table.create_table(columns, types, rows=rows)
#     t.add_enumeration()
#     return t

# @pytest.fixture
# def table1(pt_ms1):
#     pms = [emzed.io.load_peak_map(os.path.join(data_folder, "ms1_data.mzml"))]
#     kwargs = {
#         "integration_algorithm": "linear",
#         "chromatogram_boundary_factor": 3.0,
#         "precursor_column": "pecursor_mz",
#         "precursor_mz_tol": None,
#         "mz_tol_abs": 0.005,
#         "mz_tol_rel": 0.0,
#         "subtract_baseline": False,
#         "ms_data_type": "Spectra",
#         "peak_width_col": None,
#     }
#     t = extract_peaks(pt_ms1, pms, kwargs)
#     spath = os.path.join(here, "data", "classification_table_ms1.table")
#     emzed.io.save_table(t, spath, overwrite=True)
#     return t


@pytest.fixture
def kwargs1():
    kwargs = {
        "scoring_model": "random_forest_classification",
        "scoring_model_params": {
            "classifier_name": "uplc_MS1_QEx_peak_classifier",
            "ext": ".pickle",
            "path_to_folder": os.path.abspath(os.path.join(here, "data")),
        },
    }
    return kwargs


# @pytest.fixture
# def table2():
#     spath = os.path.join(here, "data", "score_table1.table")
#     t = emzed.io.load_table(spath)
#     return t


@pytest.fixture
def tm():
    columns = [
        "linear_model",
        "zigzag_index",
        "gaussian_similarity",
        "max_apex_boundery_ratio",
        "sharpness",
        "tpsar",
    ]
    rows = [[PModel(1e4), 3e40, 0, 1e-50, -2, -2e40]]
    types = [object, float, float, float, float, float]
    return emzed.Table.create_table(columns, types, rows=rows)


@pytest.fixture
def classifier():
    path = os.path.join(data_folder, "test_peak_classifier.pickle")
    with open(path, "rb") as fp:
        clf = pickle.load(fp)
    return clf


def test_classify_peaks_0(table, kwargs, regtest):
    t = cp.classify_peaks(table, kwargs)
    t = t.extract_columns("id", "peak_quality_score").to_pandas()
    print(t.to_string(), file=regtest)


def test_classify_peaks_1(table1, kwargs1, regtest):
    t = cp.classify_peaks(table1, kwargs1)
    t = t.extract_columns("id", "peak_quality_score").to_pandas()
    print(t.to_string(), file=regtest)


def test__extract_classification_data(tm):
    data = rfc._extract_classification_data(tm)[0]
    expected = np.array([1e4, 1.0e38, 0, 0, -2, -1.0e38], dtype=np.float32)
    is_ = abs(data - expected)
    print(is_)
    print(data)
    print(expected)
    assert np.all(is_ < 1e-30)


def test_get_classifier_0():
    classifier_name = "test_peak_classifier"
    is_ = cp.get_classifier(classifier_name, data_folder)
    print(type(is_))
    assert isinstance(is_, RandomForestClassifier)


def test___evaluate_classifier_env_0(classifier):
    classifier_name = ""
    meta_data = {"sklearn": "5.0.6", "numpy": "1.26.3"}
    is_ = cp._evaluate_classifier_env(classifier, classifier_name, meta_data)
    assert is_ == False


def test___evaluate_classifier_env_1(classifier):
    classifier_name = ""
    meta_data = rfc._get_meta_data()
    is_ = cp._evaluate_classifier_env(classifier, classifier_name, meta_data)
    assert is_


# def test__evaluate_


class PModel:
    def __init__(self, area):
        self.area = area
