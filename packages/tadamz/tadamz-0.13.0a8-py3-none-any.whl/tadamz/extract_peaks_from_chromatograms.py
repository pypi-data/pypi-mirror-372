# -*- coding: utf-8 -*-
"""
Created on Thu Oct  5 15:47:18 2023

@author: pkiefer
"""
# from emzed import peak_picking
from .emzed_fixes.pick_ms_chromatogram_peaks import extract_ms_chromatograms

pstfx = "_chromatogram"


def add_chromatograms_to_peaks_table(peaks_table, peakmap, kwargs):
    t = extract_ms_chromatograms(peakmap)
    t = _combine_columns(peaks_table, t, **kwargs)
    _edit_sample(t, **kwargs)

    return t


def _combine_columns(
    peaks_table, t, precursor_mz_tol, mz_tol_abs=0, mz_tol_rel=0, **kwargs
):
    mz_tol_rel *= 1e-6
    expr1 = peaks_table.mz_chromatogram.approx_equal(
        t.mz_chromatogram, mz_tol_abs, mz_tol_rel
    )
    expr2a = (
        peaks_table.rtmin_chromatogram - peaks_table.rt_max_shift
    ) <= t.rtmax_chromatogram
    expr2b = (
        peaks_table.rtmax_chromatogram + peaks_table.rt_max_shift
    ) >= t.rtmin_chromatogram
    expr = expr1 & expr2a & expr2b
    expr3a = peaks_table.precursor_mz_chromatogram.approx_equal(
        t.precursor_mz_chromatogram, precursor_mz_tol, 0
    )
    expr3b = (
        peaks_table.precursor_mz_chromatogram.is_none()
        & t.precursor_mz_chromatogram.is_none()
    )
    expr = expr1 & expr2a & expr2b & (expr3a | expr3b)
    return peaks_table.left_join(t, expr)


def _edit_sample(t, **kwargs):
    t.drop_columns("id__0")
    colnames = ["rtmin", "rtmax", "precursor_mz", "mz"]
    colnames = [n + pstfx for n in colnames]
    columns = [n + "__0" for n in colnames if n in t.col_names]
    t.drop_columns(*columns)
    t.rename_postfixes(__0="")
