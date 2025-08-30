# -*- coding: utf-8 -*-
"""
Created on Mon Feb 27 12:48:16 2023

@author: pkiefer
"""
import os
import numpy as np
from collections import defaultdict
from emzed import Table, PeakMap, MzType, RtType
from emzed import peak_picking as pp
from emzed.quantification import integrate_chromatograms, peak_shape_models
from emzed.ms_data.peak_map import Chromatogram, MSChromatogram
from .utils import get_smoothed
from .emzed_fixes.subtract_baselines import subtract_baselines
from .emzed_fixes._empty_peakmap import create_empty_peak_map
from .adapt_retention_time import local_adjust
from .extract_peaks_from_chromatograms import add_chromatograms_to_peaks_table
from .in_out import load_peak_map


def extract_peaks(peaks_table, samples, kwargs):
    _mz_tolerance_set(**kwargs)
    _update_precursor_column(peaks_table)
    peaks_table = _update_postfixes(peaks_table, kwargs)
    tables = []
    for sample in samples:
        sample = _get_sample(sample)
        t = add_sample_to_peaks_table(peaks_table, sample, kwargs)
        subtract_baselines(t, **kwargs)
        _extract(t, **kwargs)
        tables.append(t)
    t = Table.stack_tables(tables)
    _edit(t)
    return t


def _mz_tolerance_set(mz_tol_abs=0, mz_tol_rel=0, **kwargs):
    msg = """At least one of the two tolerances `mz_tol_abs`
    and `mz_tol_rel` mast be >0. Please correct your configuration
    file accordingly!"""
    assert any([mz_tol_abs, mz_tol_rel]), msg


def _extract(t, integration_algorithm, min_fwhm=2.0, **kwargs):
    print("extracting peaks ...")
    local_adjust(t, min_fwhm)
    print(f"length of table: {len(t)}")
    integrate_chromatograms(t, integration_algorithm, in_place=True)
    _fall_back_integration(t)
    print(f"length of table: {len(t)}")
    print("Done.")


def _fall_back_integration(t):
    """
    applies linear integration model to all rows whith column
    valid_model_chromatogram == False

    Parameters
    ----------
    t : Table
        integrated tabe.

    Returns
    -------
    Table
        Table whith reintegrated rows linear model of rows with unvalid model.

    """
    models = []
    for ntuple in zip(
        t.valid_model_chromatogram,
        t.model_chromatogram,
        t.rtmin_chromatogram,
        t.rtmax_chromatogram,
        t.chromatogram,
    ):
        is_valid, model = ntuple[:2]
        params = ntuple[2:]
        if is_valid == False:
            models.append(_update_linear_model(*params))
        else:
            models.append(model)

    t.replace_column("model_chromatogram", models, object)
    t.replace_column(
        "peak_shape_model_chromatogram",
        t.apply(lambda v: v.model_name, t.model_chromatogram),
        str,
    )
    # property cannot be added directly
    id2colname2value = _collect_properties(t)
    t.replace_column(
        "area_chromatogram",
        t.apply(lambda v, w, x: v[w][x], id2colname2value, t.id, "area_chromatogram"),
        float,
        format_="%.2e",
    )
    t.replace_column(
        "rmse_chromatogram",
        t.apply(lambda v, w, x: v[w][x], id2colname2value, t.id, "rmse_chromatogram"),
        float,
        format_="%.2e",
    )


def _collect_properties(t, pstfx="_chromatogram"):
    d = defaultdict(dict)
    colnames = ["area", "rmse", "valid_model"]
    for id_, model in zip(t.id, t.model_chromatogram):
        for name in colnames:
            colname = name + pstfx
            if name == "valid_model":
                d[id_][colname] = model.is_valid
            else:
                d[id_][colname] = model.__getattribute__(name)
    return d


def _update_linear_model(rtmin, rtmax, chromatogram):
    available = peak_shape_models.available_peak_shape_models
    current = available.get("linear")
    model = current.fit_chromatogram(rtmin, rtmax, chromatogram)
    return model


def _update_precursor_column(peaks_table):
    """
    MS level 1 tables do not require column precursor_mz. However, we us the
    columns mz and precursor_mz foe mixed MS levels to distinguish ms levels
    1 and 2. In case the column is missing we add the column

    """
    if "precursor_mz" not in peaks_table.col_names:
        peaks_table.add_column_with_constant_value(
            "precursor_mz", None, MzType, insert_before="mz"
        )


def _update_postfixes(peaks_table, kwargs):
    _update_id_column(peaks_table)
    peaks_table = peaks_table.copy()
    _update_rt_columns(peaks_table, **kwargs)
    ms_data_type = kwargs["ms_data_type"]
    if ms_data_type == "MS_Chromatogram":
        name2new = _col_names(kwargs)
        required = ["mz", "rtmin", "rtmax"]
        for name in required:
            new_name = name2new[name]
            peaks_table.rename_columns(**{name: new_name})
        # optional for ms level2
        optionals = ["precursor_mz", "rt"]
        for name in optionals:
            if name in peaks_table.col_names:
                peaks_table.rename_columns(**{name: name2new[name]})
    return peaks_table


def _update_rt_columns(t, peak_width_col="rt_window_size", **kwargs):
    if peak_width_col in t.col_names:
        _overwrite_warning(t)
        t.add_or_replace_column(
            "rtmax", t.rt + t[peak_width_col] / 2, RtType, insert_after="rt"
        )
        t.add_or_replace_column(
            "rtmin", t.rt - t[peak_width_col] / 2, RtType, insert_after="rt"
        )


def _overwrite_warning(t, cols=["rtmin", "rtmax"]):
    if set(cols).intersection(set(t.col_names)) == set(cols):
        msg = f""""columns {', '.join(cols)} will be repaced, since peak widths
        values are also given in table"""
        print(msg)


def _update_id_column(t):
    if not "id" in t.col_names:
        t.add_enumeration()


def _col_names(kwargs):
    pstfx = "_chromatogram"
    condition = kwargs["ms_data_type"] == "MS_Chromatogram"
    d = {}
    d["mz"] = "mz" + pstfx if condition else "mz"
    d["rt"] = "rt" + pstfx if condition else "rt"
    d["rtmin"] = "rtmin" + pstfx if condition else "rtmin"
    d["rtmax"] = "rtmax" + pstfx if condition else "rtmax"
    d["area"] = "area" + pstfx if condition else "area"
    d["model"] = "model" + pstfx if condition else "model"
    d["rmse"] = "rmse" + pstfx if condition else "rmse"
    d["precursor_mz"] = "precursor_mz" + pstfx if condition else "precursor_mz"
    d["valid_model"] = "valid_model" + pstfx if condition else "valid_model"
    return d


def add_sample_to_peaks_table(pt, peakmap, kwargs):
    ms_data_type = kwargs["ms_data_type"]
    if ms_data_type == "Spectra":
        pt = add_peakmap_from_spectra(pt, peakmap, kwargs)
    if ms_data_type == "MS_Chromatogram":
        pt = add_chromatograms_to_peaks_table(pt, peakmap, kwargs)
    pt.add_column_with_constant_value("filename", peakmap.meta_data["source"], str)
    pt.add_column_with_constant_value(
        "acquisition_time",
        peakmap.meta_data.get("acquisition_time"),
        str,
        insert_after="filename",
        format_=None,
    )
    _update_tic_area(pt, peakmap, ms_data_type)
    return pt


# BAUSTELLE


def _update_tic_area(t, peakmap, ms_data_type):
    mslevel2tic_area = _get_tic_areas(peakmap, ms_data_type)
    mz = "mz" if ms_data_type == "Spectra" else "mz_chromatogram"
    precursor_mz = (
        "precursor_mz" if ms_data_type == "Spectra" else "precursor_mz_chromatogram"
    )
    t.add_or_replace_column(
        "ms_level", t[precursor_mz].is_none().then_else(1, 2), int, insert_after=mz
    )
    t.add_or_replace_column(
        "tic_area", t.apply(mslevel2tic_area.get, t.ms_level), float, format_="%.2e"
    )


def _get_tic_areas(peakmap, ms_data_type):
    msg = f"tic_area of {peakmap.meta_data['source']}..."
    print(msg)
    if ms_data_type == "Spectra":
        # 1. spectra
        mslevel2tic = {}
        for ms_level in peakmap.ms_levels():
            rts, ints = peakmap.chromatogram(ms_level=ms_level)
            # to avoid zero division
            mslevel2tic[ms_level] = np.trapz(ints, rts) + 1
        return mslevel2tic
    if ms_data_type == "MS_Chromatogram":
        # the dirst chromatogram contains total ion current
        chrom = peakmap.ms_chromatograms[0]
        msg = f"unexpected chromatogram type {chrom.type}"
        assert chrom.type == "TOTAL_ION_CURRENT_CHROMATOGRAM", msg
        tic_area = np.trapz(chrom.intensities, chrom.rts)
        return {i: tic_area for i in range(1, 3)}


def _add_peakmap_from_spectra(pt, peakmap, kwargs):
    ms_level = kwargs["ms_level"]
    pt = pt.copy()
    _update_mz_range(pt, **kwargs)
    if ms_level == 1:
        pt.add_column_with_constant_value("peakmap", peakmap, PeakMap)
    if ms_level == 2:
        t = create_ms2_peakmap_table(peakmap)
        pt = assign_peakmaps_by_precursor(pt, t, **kwargs)
    pt = convert_peakmap_to_chromatogram(pt, **kwargs)
    return pt


def add_peakmap_from_spectra(pt, peakmap, kwargs):
    pt_ms1, pt_ms2 = _split_pt_by_ms_level(pt)
    _update_mz_range(pt_ms1, **kwargs)
    _update_mz_range(pt_ms2, **kwargs)
    pt_ms1.add_column_with_constant_value("peakmap", peakmap, PeakMap)
    t = create_ms2_peakmap_table(peakmap)
    pt_ms2 = assign_peakmaps_by_precursor(pt_ms2, t, **kwargs)
    pt = Table.stack_tables([pt_ms1, pt_ms2])
    return convert_peakmap_to_chromatogram(pt, **kwargs)
    # return pt


def _update_mz_range(pt, mz_tol_abs=0, mz_tol_rel=0, **kwargs):
    mz_tol_rel *= 1e-6  # since mz_tol_rel is given in ppm
    pt.add_or_replace_column(
        "mzmax", pt.mz * (1 + mz_tol_rel) + mz_tol_abs, MzType, insert_after="mz"
    )
    pt.add_or_replace_column(
        "mzmin", pt.mz * (1 - mz_tol_rel) - mz_tol_abs, MzType, insert_after="mz"
    )


def _split_pt_by_ms_level(pt):
    pt_ms1 = pt.filter(pt.precursor_mz.is_none())
    pt_ms2 = pt.filter(pt.precursor_mz.is_not_none())
    return pt_ms1, pt_ms2


def create_ms2_peakmap_table(peakmap):
    if 2 in peakmap.ms_levels():
        prec2pm = peakmap.split_by_precursors()
        precs, pms = zip(*list(prec2pm.items()))
        precursors = np.array(precs).reshape(1, -1)[0].tolist()
        rows = list(zip(precursors, pms))
    else:
        rows = None
    columns = ["precursor_mz", "peakmap"]
    types = [MzType, PeakMap]
    t = Table.create_table(columns, types, rows=rows)
    return t


def assign_peakmaps_by_precursor(
    pt, t, precursor_mz_tol=0, mz_tol_abs=0, mz_tol_rel=0, **kwargs
):
    # since mz_tol_rel is given in ppm
    mz_tol_rel = mz_tol_rel / 1e6
    _update_pm_ranges(t, mz_tol_abs, mz_tol_rel)
    # precursor_mzs match
    condition1 = pt.precursor_mz.approx_equal(t.precursor_mz, precursor_mz_tol, 0)
    # peak mz range is covered by peakmap mz range we sel
    condition2 = pt.mz.in_range(t.mzmin, t.mzmax)
    # the peak range is covered by measure
    condition3 = (pt.rtmax >= t.rtmin) & (pt.rtmin <= t.rtmax)

    t = pt.left_join(t, condition1 & condition2 & condition3)

    drop_cols = [
        cn
        for cn in t.col_names
        if cn.endswith("__0") and cn.startswith("peakmap") == False
    ]
    print(drop_cols)
    t.drop_columns(*drop_cols)
    t.rename_postfixes(__0="")
    _replace_none_by_empty_peakmap(t)
    return t.copy()


def _replace_none_by_empty_peakmap(t, mslevel=2):
    pm_empty = create_empty_peak_map(None, mslevel)
    # pm_empty_neg = create_empty_peak_map('-', mslevel)
    pms = [_replace(pm, pm_empty) for pm in t.peakmap]
    t.replace_column("peakmap", pms, PeakMap)


def _update_pm_ranges(t, mz_tol_abs, mz_tol_rel):
    t.add_column(
        "rtmin", t.apply(_get_rt_value, t.peakmap, 0, ignore_nones=False), RtType
    )
    t.add_column(
        "rtmax", t.apply(_get_rt_value, t.peakmap, 1, ignore_nones=False), RtType
    )
    t.add_column(
        "mzmin", t.apply(_get_mz_value, t.peakmap, 0, ignore_nones=False), MzType
    )
    t.replace_column("mzmin", t.mzmin * (1 - mz_tol_rel) - mz_tol_abs, MzType)
    t.add_column(
        "mzmax", t.apply(_get_mz_value, t.peakmap, 1, ignore_nones=False), MzType
    )
    t.replace_column("mzmax", t.mzmax * (1 + mz_tol_rel) + mz_tol_abs, MzType)


def convert_peakmap_to_chromatogram(
    t, chromatogram_boundary_factor=3, ms_level=None, **kwargs
):
    # _replace_bounderies_by_peakmap_range(t)
    _enlarge_bouderies(t, chromatogram_boundary_factor)
    t = pp.extract_chromatograms(t, ms_level=ms_level)
    _update_original_rts(t)
    drop_cols = ("mzmin", "mzmax", "peakmap", "rtmin", "rtmax")
    cols = [col for col in t.col_names if col in drop_cols]
    t.drop_columns(*cols)
    return t


def update_smoothed_chromatogram(t):
    t.add_or_replace_column(
        "smoothed_chromatogram",
        t.apply(_smoothed_chromatogram, t.chromatogram),
        MSChromatogram,
    )


def _smoothed_chromatogram(chromatogram):
    smoothed = get_smoothed(chromatogram.intensities)
    return Chromatogram(chromatogram.rts, smoothed)


def _replace_bounderies_by_peakmap_range(t):
    t.add_column("rtmin_", t.rtmin, RtType)
    t.add_column("rtmax_", t.rtmax, RtType)
    rtmin, rtmax = t.peakmap.unique_value().rt_range()
    t.replace_column_with_constant_value("rtmin", rtmin, RtType)
    t.replace_column_with_constant_value("rtmax", rtmax, RtType)


def _enlarge_bouderies(t, chromatogram_boundary_factor=3):
    t.add_column("rtmin_", t.rtmin, RtType)
    t.add_column("rtmax_", t.rtmax, RtType)
    t.add_column("rt_range", t.apply(_get_rt_range, t.peakmap), object)
    # rtmin, rtmax = t.peakmap.unique_value().rt_range()
    t.replace_column(
        "rtmin", t.rtmin - chromatogram_boundary_factor * t.rt_max_shift, RtType
    )
    t.replace_column(
        "rtmin",
        (t.rtmin < t.apply(lambda v: v[0], t.rt_range)).then_else(
            t.apply(lambda v: v[0], t.rt_range), t.rtmin
        ),
        RtType,
    )
    t.replace_column(
        "rtmax", t.rtmax + chromatogram_boundary_factor * t.rt_max_shift, RtType
    )
    t.replace_column(
        "rtmax",
        (t.rtmax > t.apply(lambda v: v[1], t.rt_range)).then_else(
            t.apply(lambda v: v[1], t.rt_range), t.rtmax
        ),
        RtType,
    )


def _get_rt_range(pm):
    return pm.rt_range()


def _update_original_rts(t):
    t.replace_column("rtmin_chromatogram", t.rtmin_, RtType)
    t.replace_column("rtmax_chromatogram", t.rtmax_, RtType)
    t.rename_columns(rt="rt_chromatogram")
    t.drop_columns("rtmin_", "rtmax_")


#         return False


def _get_rt_value(peakmap, i):
    return peakmap.rt_range()[i]


def _get_mz_value(peakmap, i):
    return peakmap.mz_range()[i]


def _replace(pm, empty):
    return empty if pm is None else pm


def _get_sample(sample):
    if isinstance(sample, PeakMap):
        return sample
    if isinstance(sample, str):
        if os.path.exists(sample):
            filename = os.path.basename(sample)
            msg = f"loading sample {filename} ..."
            print(msg)
            return load_peak_map(sample)
    assert False, "sample is neither a PeakMap nor a sample path"


def _edit(t):
    # default values required if isotopologue overly correction is not applied
    # currently we
    # t.add_or_replace_column(
    #     "_area_chromatogram",
    #     t.area_chromatogram,
    #     float,
    #     format_=None,
    #     insert_after="area_chromatogram",
    # )
    t.add_or_replace_column_with_constant_value(
        "isotopologue_overlay_correction",
        False,
        bool,
        insert_after="area_chromatogram",
    )
    # we introduce the internal column row_id
    # to support row dwependent operations
    t.add_enumeration("row_id")
    t.set_col_format("row_id", None)
