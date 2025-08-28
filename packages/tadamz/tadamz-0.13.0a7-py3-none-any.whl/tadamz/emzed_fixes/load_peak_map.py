# -*- coding: utf-8 -*-
"""
Created on Mon Jun 30 13:49:53 2025

@author: pkiefer
"""
import os
import sys

# import pyopenms
import pathlib
import pickle
import pyopenms

here = os.path.abspath(os.path.dirname(__file__))
pyopenms.load_optimizations(os.path.join(here, "optimizations.py"))
from .optimizations import encode
from emzed import PeakMap


def load_peak_map(path, *, target_db_file=None, overwrite=False):
    # open-ms returns empty peakmap if file does not exists, so we check ourselves:

    assert isinstance(
        path, (str, pathlib.Path)
    ), "must be string or pathlib.Path object"

    path = os.path.abspath(path)
    if not os.path.exists(path):
        raise OSError(f"file {path} does not exist")
    if not os.path.isfile(path):
        raise OSError(f"{path} is not a file")

    if target_db_file == path:
        raise ValueError(
            "you must not use the same path for 'path' and 'target_db_file'"
        )

    if target_db_file is not None and os.path.exists(target_db_file):
        if overwrite:
            os.unlink(target_db_file)
        else:
            raise ValueError(f"{target_db_file} already exists")

    if sys.platform == "win32":
        path = path.replace("/", "\\")  # needed for network shares
    spectra, chromatograms, source, acq_time = pyopenms.load_experiment_detailed(
        encode(path)
    )
    meta_data = {"acquisition_time": acq_time}
    return PeakMap._from_iter(
        pickle.loads(spectra),
        pickle.loads(chromatograms),
        target_db_file,
        source,
        meta_data,
    )
