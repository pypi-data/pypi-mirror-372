# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 10:30:15 2023
columns
id, ms_level, peak_type, name, mf, precursor_mz, mz,  mzmin, mzmax, rt, rtmin, rtmax
@author: pkiefer
"""

from emzed import RtType, MzType


def setup_targets_table(t, ms_data_type, ms_experiment):
    pass


def build_ms1_table(table, ms_data_type):
    pass


def build_ms2_table(table, data_type):
    pass


def is_targets_table(pt, ms_data_type, ms_experiment):
    pass


def _get_specific_columns(data_type, ms_experiment):
    pass


def required_columns():
    #'mz', 'rt',
    pass
