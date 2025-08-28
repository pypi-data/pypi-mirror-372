# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 09:22:40 2023

@author: pkiefer
"""
import pytest
import os
import pickle
import numpy as np
import emzed
from emzed import Table, PeakMap, MzType, to_table
from src.tadamz import in_out

# import onnx

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


@pytest.fixture
def table():
    colnames = "a", "b", "c"
    types = float, float, float
    rows = [[1.1, 1.0, None], [None, 2.0, 3.0]]
    return Table.create_table(colnames, types, rows=rows)


@pytest.fixture
def _create():
    ext = ".pickle"
    filenames = ["classifier" + str(i) + ext for i in range(3)]
    for i in range(3):
        fname = "classifier" + str(i) + ext
        path = os.path.join(data_folder, fname)
        with open(path, "wb") as fp:
            pickle.dump(i, fp)


@pytest.fixture
def _paths():
    sf = emzed.io
    t = emzed.to_table("a", [0], int)
    name = "load_pt_table"
    paths = []
    exts = ".table", ".xlsx", ".csv"
    save_funs = sf.save_table, sf.save_excel, sf.save_csv
    for ext, save_fun in zip(exts, save_funs):
        fname = name + ext
        path = os.path.join(data_folder, fname)
        if not os.path.exists(path):
            save_fun(t, path)
        paths.append(path)
    return paths


@pytest.fixture
def _path():
    return os.path.join(data_folder, "targets_table_sim.xlsx")


@pytest.fixture
def sample_path():
    return os.path.join(data_folder, "ms_prm_data.mzml")


def test_get_sample_paths_from_folder_0(regtest):
    paths = in_out.get_sample_paths_from_folder(data_folder, pattern="mrm*")
    print(paths, file=regtest)


def test_get_sample_paths_from_folder_1():
    paths1 = in_out.get_sample_paths_from_folder(
        data_folder, pattern="mrm*", extension=".MZML"
    )
    paths2 = in_out.get_sample_paths_from_folder(
        data_folder, pattern="mrm*", extension=".mzml"
    )
    assert paths1 == paths2


def test_load_targets_table_0(_paths, regtest):
    for path in _paths:
        t = in_out.load_targets_table(path)
        print(t, file=regtest)


def test_load_targets_table_1(_path):
    t = in_out.load_targets_table(_path)
    is_ = dict(zip(t.col_names, t.col_types))
    assert is_["precursor_mz"] == MzType


def test__check_float(table):
    in_out._check_float(table)
    assert table.col_types == (float, int, int)


def test_save_load_config():
    config = {"a": "b"}
    path = os.path.join(data_folder, "test_config.txt")
    if os.path.exists(path):
        os.remove(path)
    in_out.save_config(config, path)
    is_ = in_out.load_config(path)
    assert is_ == config


def test_get_classifier_path(_create):
    prfx = "classifier"
    for i in range(3):
        classifier_name = prfx + str(i)
        x = in_out.get_classifier_path(
            classifier_name, ext=".pickle", path_to_folder=data_folder
        )
        name = os.path.basename(os.path.splitext(x)[0])
        assert name == classifier_name


def test_get_classifier_path_1():
    classifier_name = ""
    with pytest.raises(AssertionError):
        in_out.get_classifier_path(classifier_name)


def test_save_classifier_0():
    classifier_name = "classifier0"
    with pytest.raises(OSError):
        in_out.save_classifier_object(
            None, classifier_name, ext=".pickle", path_to_folder=data_folder
        )


def test_load_save_tadamz_table_0():
    import sys

    print(sys.path)
    path = os.path.join(data_folder, "calibration_table.table")
    t = in_out.load_tadamz_table(path)
    print(t.col_names)
    path1 = path = os.path.join(data_folder, "calibration_table1.table")
    in_out.save_tadamz_table(t, path1, overwrite=True)
    t = in_out.load_tadamz_table(path1)
    os.remove(path1)
    assert "calibration_model" in t.col_names


def test_load_peak_map_0(sample_path):
    is_ = in_out.load_peak_map(sample_path)
    assert is_.meta_data["acquisition_time"] == "0000-00-00 00:00:00"


def test_save_classifier_object_0():
    objs = [{}, 2.5, to_table("a", [1], int)]
    exts = [".json", ".pickle", ".table"]
    classifier_name = "clf_obj"
    for obj, ext in zip(objs, exts):
        in_out.save_classifier_object(
            obj, classifier_name, ext, path_to_folder=data_folder, overwrite=True
        )
        path = os.path.join(data_folder, classifier_name + ".json")
        assert os.path.exists(path)


def test_save_classifier_object_1():
    objs = [{}, 2.5, to_table("a", [1], int)]
    exts = [".json", ".pickle", ".table"]
    classifier_name = "clf_obj"
    for obj, ext in zip(objs, exts):
        with pytest.raises(OSError):
            in_out.save_classifier_object(
                obj, classifier_name, ext, path_to_folder=data_folder, overwrite=False
            )
