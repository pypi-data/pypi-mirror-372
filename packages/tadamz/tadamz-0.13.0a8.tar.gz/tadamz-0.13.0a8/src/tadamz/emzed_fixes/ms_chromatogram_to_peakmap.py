# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 12:33:24 2023

@author: pkiefer
"""
from emzed import Spectrum, PeakMap, Table, MzType
from emzed.utils.sqlite import Connection
from emzed.ms_data.peak_map import create_table
import numpy as np

supported_types = [
    "SELECTED_ION_MONITORING_CHROMATOGRAM",
    "SELECTED_REACTION_MONITORING_CHROMATOGRAM",
]


def ms2_peakmap_table_from_chromatograms(pm, **kwargs):
    source = pm.meta_data["source"]
    polarity = pm.polarities().pop() if len(pm.polarities()) == 1 else None
    colnames = ["precursor_mz", "peakmap"]
    coltypes = [MzType, PeakMap]
    rows = []

    for chrom in pm.ms_chromatograms:
        if chrom.type == supported_types[1]:
            precursor_mz = chrom.precursor_mz
            sub = chromatogram2peakmap(chrom, polarity, source)
            row = [precursor_mz, sub]
            rows.append(row)
    return Table.create_table(colnames, coltypes, rows=rows)


def chromatogram2peakmap(ms_chromatogram, polarity=None, source=""):
    """
    converts SRM and SIM ms_chromatogram to peakmap

    Parameters
    ----------
    ms_chromatogram : MSChromatogram
        peakmap ms_chromatogram of types 'SELECTED_ION_MONITORING_CHROMATOGRAM' and
        'SELECTED_REACTION_MONITORING_CHROMATOGRAM'. Other types will be ignored
    polarity : TYPE, optional
        DESCRIPTION. The default is None.

    Returns
    -------
    PeakMap
        Returns a peakmap with single EIC
    """
    if ms_chromatogram.type in supported_types:
        ms_level = 1 if ms_chromatogram.type == supported_types[0] else 2
        spectra = _build_spectra(ms_chromatogram, ms_level, polarity)
        mzs = [ms_chromatogram.mz - 0.5, ms_chromatogram.mz + 0.5]
        return _create_peakmap(
            spectra, ms_level, polarity, mzs, ms_chromatogram.rts, source
        )
    msg = (
        f"converting MS_Chromatogram of type {ms_chromatogram.type} to PeakMap "
        "is not supported"
    )
    print(msg)


def chromatograms2peakmap(ms_chromatograms, polarity=None, source=""):
    spectra = []
    mzs = []
    rt_limits = []
    for ms_chromatogram in ms_chromatograms:
        if ms_chromatogram.type in supported_types:
            ms_level = 1 if ms_chromatogram.type == supported_types[0] else 2
            _build_spectra(ms_chromatogram, ms_level, polarity, spectra)
            mzs.append(ms_chromatogram.mz)
            rt_limits.extend([min(ms_chromatogram.rts), max(ms_chromatogram.rts)])
        else:
            msg = (
                f"converting MS_Chromatogram of type {ms_chromatogram.type} to PeakMap "
                "is not supported"
            )
            print(msg)
    # return spectra
    return _create_peakmap(spectra, ms_level, polarity, mzs, rt_limits, source)


def _build_spectra(chrom, ms_level, polarity, spectra=None):
    if spectra is None:
        spectra = []
    rts, ints = correct_baseline(chrom)
    pairs = zip(rts, ints)
    current = len(spectra)
    for i, pair in enumerate(pairs):
        i += current
        rt, intensity = pair
        precursor_mz = [(chrom.precursor_mz, 0, 0)] if ms_level == 2 else None
        peaks = np.array(
            [
                [chrom.mz, intensity],
            ]
        )
        spec = Spectrum(i, float(rt), ms_level, polarity, precursor_mz, peaks)
        spectra.append(spec)
    return spectra


def _create_peakmap(spectra, ms_level, polarity, mzs, rt_limits, source):
    conn = Connection(None)
    conn, access_name = create_table(conn=conn)
    info = {
        "rt_ranges": {
            ms_level: (min(rt_limits), max(rt_limits)),
            None: (min(rt_limits), max(rt_limits)),
        },
        "mz_ranges": {ms_level: (min(mzs), max(mzs)), None: (min(mzs), max(mzs))},
        "ms_levels": {ms_level},
        "polarities": {polarity},
    }
    meta_data = {"full_source": "", "source": source}
    pm = PeakMap(conn, access_name, meta_data, info)
    with pm.spectra_for_modification() as sp:
        [sp.add_spectrum(spec) for spec in spectra]
    return pm


def correct_baseline(chroms):
    rts, ints = chroms.rts, chroms.intensities
    apx = np.where(ints == max(ints))[0][0]
    lmin = np.where(ints[: apx + 1] == min(ints[: apx + 1]))[0][0]
    lmax = np.where(ints[apx:] == min(ints[apx:]))[0][0] + apx
    m = (ints[lmax] - ints[lmin]) / (rts[lmax] - rts[lmin])
    b = ints[lmin] - m * rts[lmin]
    deltas = m * rts + b
    deltas[: lmin + 1] = ints[lmin]
    deltas[lmax:] = ints[lmax]
    # return rts, deltas
    ints_corr = ints - deltas
    ints_corr[ints_corr < 0] = 0
    pos = np.where(ints_corr > 0)
    rts = rts[pos].reshape(len(pos[0]))
    ints_corr = ints_corr[pos].reshape(len(pos[0]))
    return rts, ints_corr
