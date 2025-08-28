# -*- coding: utf-8 -*-
"""
Created on Thu Feb 20 13:13:37 2025

@author: pkiefer
"""


def fix_integrate_chromatogram_formats(t):
    for name in "area_chromatogram", "rmse_chromatogram":
        t.set_col_format(name, "%.2e")
