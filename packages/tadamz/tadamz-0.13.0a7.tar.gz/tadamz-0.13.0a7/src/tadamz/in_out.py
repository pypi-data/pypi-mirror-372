# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 09:31:24 2023

@author: pkiefer
"""
import yaml
import os
from glob import glob
import inspect
from emzed import MzType, RtType
import json
import pickle
from .emzed_fixes.load_peak_map import load_peak_map
from emzed.io import load_table, load_excel, load_csv, save_table, save_excel, save_csv

# import onnx
from .calibration.calibration_model import CalibrationModel

# import onnxruntime as ort

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


def load_targets_table(path):
    """
    load peaks table. supported data formats .table, .xls(x), .csv

    Parameters
    ----------
    path : str
        DESCRIPTION.

    Returns
    -------
    Table
        returns peaks table

    """
    load_fun = _get_load_fun(path)
    t = load_fun(path)
    _check_float(t)
    _handle_column_types(t)
    return t


def _get_load_fun(path):
    ext = os.path.splitext(path)[-1]
    return _ext2io_fun(ext, "load")


def _ext2io_fun(key, mode):
    e2f = {
        "load": {
            ".table": load_table,
            ".csv": load_csv,
            ".xls": load_excel,
            ".xlsx": load_excel,
            ".pickle": _load_pickle,
            ".json": _load_json,
        },
        "save": {
            ".table": save_table,
            ".csv": save_csv,
            ".xls": save_excel,
            ".xlsx": load_excel,
            ".pickle": _save_pickle,
            ".json": _save_json,
        },
    }
    return e2f[mode][key]


def _check_float(t):
    for name, type_ in zip(t.col_names, t.col_types):
        if type_ == float:
            if _all_int(t, name):
                t.replace_column(
                    name,
                    t[name]
                    .is_not_none()
                    .then_else(t.apply(lambda v: int(v), t[name]), None),
                    int,
                )


def _all_int(t, name):
    values = set(t[name])
    return all(_check(v) for v in values)


def _check(v):
    if v is None:
        return True
    return v == int(v)


def _handle_column_types(t):
    default2type = {
        "precursor_mz": MzType,
        "mz": MzType,
        "rt_max_shift": RtType,
        "rt": RtType,
        "rtmin": RtType,
        "rtmax": RtType,
        "rt_window_size": RtType,
    }

    for col, type_ in zip(t.col_names, t.col_types):
        if col in default2type.keys():
            if col != default2type[col]:
                t.replace_column(col, t[col].to_list(), default2type[col])


def load_samples_from_folder(
    sample_dir, pattern=None, ignore_blanks=True, extension=".mzml"
):
    paths = get_sample_paths_from_folder(sample_dir, pattern, ignore_blanks, extension)

    return load_samples(paths)


def get_sample_paths_from_folder(
    sample_dir, pattern=None, ignore_blanks=True, extension=".mzml"
):
    pattern = "*" if pattern is None else pattern
    # pattern = _update_extension(pattern, extension)
    path = os.path.join(sample_dir, pattern)
    paths = glob(path)
    return [p for p in paths if _extension_ok(p, extension)]


def _extension_ok(path, ext):
    return os.path.splitext(path)[-1].lower() == ext.lower()


def load_samples(paths):
    return [load_peak_map(path) for path in paths]


def load_config(path):
    with open(path, "r") as fp:
        data = fp.read()
    return yaml.safe_load(data)


def save_config(config, path):
    data = yaml.safe_dump(config)
    with open(path, "w") as fp:
        fp.write(data)


def load_classifier_object(classifier_name, ext, path_to_folder=None):
    path_to_folder = data_folder if path_to_folder is None else path_to_folder
    path = os.path.join(path_to_folder, classifier_name + ext)
    return _ext2io_fun(ext, "load")(path)


def save_classifier_data(
    clf, meta_data, t_data, classifier_name, path_to_folder=None, overwrite=False
):
    save_classifier_object(clf, classifier_name, ".pickle", path_to_folder, overwrite)
    save_classifier_object(t_data, classifier_name, ".table", path_to_folder, overwrite)
    save_classifier_object(
        meta_data, classifier_name, ".json", path_to_folder, overwrite
    )


def save_classifier_object(
    obj, classifier_name, ext, path_to_folder=None, overwrite=False
):
    path_to_folder = data_folder if path_to_folder is None else path_to_folder
    path = os.path.join(path_to_folder, classifier_name + ext)
    return _ext2io_fun(ext, "save")(obj, path, overwrite=overwrite)


def _get_save_path(classifier_name, ext, path_to_folder, overwrite):
    path = os.path.join(path_to_folder, classifier_name + ext)
    if os.path.exists(path) and not overwrite:
        msg = f""" Classifier with name {classifier_name} exists already in {path_to_folder}.
        Please choose a different name or folder
        """
        assert False, msg
    return path


def get_classifier_path(classifier_name, ext=".pickle", path_to_folder=None):
    if path_to_folder is None:
        path_to_folder = data_folder
    name2path = _get_existing_classifier(ext, path_to_folder)
    _classifier_exists(name2path, classifier_name)
    return name2path[classifier_name]


def _get_existing_classifier(ext, path_to_folder):
    fname = "*" + ext
    print(fname)
    path = os.path.join(path_to_folder, fname)
    print(path)
    paths = glob(path)
    print(paths)
    return {os.path.splitext(os.path.basename(p))[0]: p for p in paths}


def _classifier_exists(name2path, name):
    msg = f""" classifier {name} is not provided!
    Please check the spelling or use a different classifier. 
    """
    assert name2path.get(name), msg


def load_tadamz_table(path):
    t = load_table(path)
    if "calibration_model_dict" in t.col_names:
        t.add_column(
            "calibration_model",
            t.apply(dict_to_model, t.calibration_model_dict, ignore_nones=False),
            object,
            format_=None,
            insert_after="calibration_model_dict",
        )
        t.drop_columns("calibration_model_dict")
    return t


def save_tadamz_table(t, path, overwrite=False):
    path = _update_table_path(path)
    if "calibration_model" in t.col_names:
        model_dicts = [model_to_dict(model) for model in t.calibration_model]
        t.add_or_replace_column(
            "calibration_model_dict",
            model_dicts,
            object,
            format_=None,
            insert_after="calibration_model",
        )
        t.drop_columns("calibration_model")
    save_table(t, path, overwrite=overwrite)
    t.add_column(
        "calibration_model",
        t.apply(dict_to_model, t.calibration_model_dict, ignore_nones=False),
        object,
        format_=None,
        insert_after="calibration_model_dict",
    )
    t.drop_columns("calibration_model_dict")


def _load_json(path):
    with open(path, "r") as fp:
        k2v = json.load(fp)
    return k2v


def _save_json(d, path, overwrite):
    _save_possible(path, overwrite)
    with open(path, "w") as fp:
        json.dump(d, fp)


def _load_pickle(path):
    with open(path, "rb") as fp:
        obj = pickle.load(fp)
    return obj


def _save_pickle(obj, path, overwrite=False):
    _save_possible(path, overwrite)
    with open(path, "wb") as fp:
        pickle.dump(obj, fp)


def _update_table_path(path):
    path, _ = os.path.splitext(path)
    return path + ".table"


def _save_possible(path, overwrite):
    if not overwrite and os.path.exists(path):
        # msg = f"""
        # Path {path} exists already! please choose a different path or
        # set `overwrite` to `True`
        # """
        raise OSError


def model_to_dict(model):
    keys = [
        key
        for key in inspect.signature(model.__init__).parameters.keys()
        if key != "kwargs"
    ]
    return {key: model.__dict__[key] for key in keys}


def dict_to_model(model_dict):
    if isinstance(model_dict, dict):
        return CalibrationModel(**model_dict)
