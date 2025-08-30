# -*- coding: utf-8 -*-
"""
Created on Tue Dec  3 15:37:44 2024

@author: pkiefer
"""
from emzed import MzType

# from emzed.ms_data.peak_map import MSChromatogram, ChromatogramType
from emzed.peak_picking import extract_ms_chromatograms as emc


def extract_ms_chromatograms(peakmap):
    t = emc(peakmap)
    return _edit(t)


def _edit(t):
    t = t.filter((t.type == "TOTAL_ION_CURRENT_CHROMATOGRAM") == False)
    t.add_column(
        "temp_mz",
        (t.mz_chromatogram == 0.0).then_else(
            t.precursor_mz_chromatogram, t.mz_chromatogram
        ),
        MzType,
    )
    t.replace_column(
        "precursor_mz_chromatogram",
        (t.mz_chromatogram == 0.0).then_else(None, t.precursor_mz_chromatogram),
        MzType,
    )
    t.replace_column("mz_chromatogram", t.temp_mz, MzType)
    t.drop_columns("temp_mz", "peakmap")
    return t
