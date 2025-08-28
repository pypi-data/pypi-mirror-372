# -*- coding: utf-8 -*-
"""
Created on Fri Aug  9 15:01:58 2024

@author: pkiefer
"""
from .utils import cleanup_last_join


def update_sample_information(t, t_sample, kwargs):
    _update_sample_information(t, t_sample, **kwargs)


def _update_sample_information(t, t_sample, filename_col="filename", **kwargs):
    if _check_input(t_sample):
        t.add_enumeration("uid")
        y = t.left_join(t_sample, (t[filename_col] == t_sample[filename_col]))
        cleanup_last_join(y)
        diff_cols = y.col_names[len(t.col_names) :]
        types = y.col_types[len(t.col_names) :]
        formats = y.col_formats[len(t.col_names) :]
        for name, type_, format_ in zip(diff_cols, types, formats):
            d = dict(zip(y.uid, y[name]))
            t.add_column(name, t.apply(d.get, t.uid), type_, format_=format_)
        t.drop_columns("uid")


def _check_input(t_sample):
    if t_sample is None:
        msg = """sample table was not provided. No sample information was added
        to the result table. 
        """
        print(msg)
        return False
    return True
