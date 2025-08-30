# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 08:59:16 2022

@author: pkiefer

TO DO: Check whether snr is required for efficient random forest
peaks classification or if it can be removed.
Reasoning. SNR requires at least 6 spectra for savgol filtering.
Alternative approach: inject a peak via linear model

"""
import numpy as np

# from emzed.quantification import integrate_chromatograms

# import emzed
from scipy.optimize import curve_fit
from scipy.signal import savgol_filter
from ..utils import integrate_table

# from random import uniform
# import os
# here = os.path.abspath(os.path.dirname(__file__))
# data_folder = os.path.join(os.path.dirname(here), 'data')


def update_metrics(t, ms_data_type="MS_Chromatogram"):
    area_col = _column_with_pstfx("area", ms_data_type)
    model_col = _column_with_pstfx("model", ms_data_type)
    _update_linear_model(t, model_col, ms_data_type)
    update = t.add_or_replace_column
    update(
        "no_spectra", t.apply(count_spectra, t.linear_model), int, insert_after=area_col
    )
    update(
        "tpsar",
        t.apply(tpasr_sum, t.linear_model, t.no_spectra),
        float,
        format_="%.2e",
        insert_after=area_col,
    )
    update(
        "sharpness",
        t.apply(sharpness, t.linear_model, t.no_spectra),
        float,
        format_="%.2e",
        insert_after=area_col,
    )
    update(
        "max_apex_boundery_ratio",
        t.apply(max_apex_boundery_ratio, t.linear_model, t.no_spectra),
        float,
        format_="%.2e",
        insert_after=area_col,
    )
    update(
        "gaussian_similarity",
        t.apply(gaussian_similarity, t.linear_model, t.no_spectra),
        float,
        format_="%.2e",
        insert_after=area_col,
    )
    update(
        "zigzag_index",
        t.apply(zigzag_index, t.linear_model, t.no_spectra),
        float,
        format_="%.2e",
        insert_after=area_col,
    )
    # update('snr',
    #        t.apply(estimate_snr, t[model_col]), float, format_='%.2e',
    #        insert_after='area')
    # mv_imputation(t)


def count_spectra(model):
    rts, ints = model.graph()
    if model.model_name == "no_integration":
        return 0
    return len(ints[ints > 0])


def zigzag_index(model, no_spectra):
    # source: https://rdrr.io/cran/MetaClean/src/R/calculateZigZagIndex.R
    rts, ints = set_peak_bounderies(model)
    if no_spectra > 4:
        epi = max(ints) - np.mean([ints[0], ints[1], ints[-2], ints[-1]])
        zig_zags = (2 * ints[1:-1] - ints[:-2] - ints[2:]) ** 2
        try:
            return np.sum(zig_zags) / (epi**2 * len(ints))
        except:
            import pdb

            pdb.set_trace()


def tpasr_sum(model, no_spectra):
    # source: https://rdrr.io/cran/MetaClean/src/R/calculateTPASR.R
    # Note TPASR is based on sums and not on areas.
    rts, ints = set_peak_bounderies(model)
    if no_spectra > 2:
        peak_width = len(ints)
        tar = 0.5 * (max(ints) - min(ints)) * peak_width
        return abs(tar - np.sum(ints)) / (tar + 1)  # to avoid zero devision


def sharpness(model, no_spectra):
    rts, ints = set_peak_bounderies(model)
    if no_spectra > 1:
        index = np.where(ints == max(ints))[0][0]
        # we avouid zero division
        ints[ints == 0] = 1
        # replace ones by min baseline
        ints[ints == 1] = min([ints[0], ints[-1]])
        ints_0 = ints[: index + 1]
        ints_1 = ints[index:][::-1]  # reverse the direction to apply np.diff
        s0 = np.sum(np.diff(ints_0) / ints_0[:-1])
        s1 = np.sum(np.diff(ints_1) / ints_1[1:])  # since the direction is rev
        return s0 + s1


def max_apex_boundery_ratio(model, no_spectra):
    rts, ints = set_peak_bounderies(model)
    # to avoid zero division
    ints[ints == 0] = 1
    if no_spectra > 2:
        max_boundery = np.max([ints[0], ints[-1]])
        return max(ints) / max_boundery


def estimate_snr(model, no_spectra):
    rts, ints = set_peak_bounderies(model)
    if no_spectra > 5:
        winlen = int(len(ints) / 3)
        # winlen must be odd
        winlen = winlen + 1 if winlen / 2 == int(winlen / 2) else winlen
        # we set a maximal winlen
        winlen = 25 if winlen > 25 else winlen
        filtered = savgol_filter(ints, winlen, 2)
        apex = np.where(filtered == max(filtered))[0][0]
        slope = (
            (filtered[-1] + filtered[-2] - filtered[0] - filtered[1])
            / 2
            / len(filtered)
        )
        baseline_at_appex = filtered[0] + slope * apex
        signal = max(filtered) - baseline_at_appex
        noise = np.percentile(np.abs(ints - filtered), 95) + 1  # to avoid zero division
        return signal / noise


def gaussian_similarity(model, no_spectra):
    # source https://rdrr.io/cran/MetaClean/src/R/calculateGaussianSimilarity.R
    rts, ints = set_peak_bounderies(model)
    if no_spectra > 3:
        fit_params = None
        # to avoiud zero division we replace
        # return start_values
        start_values = estimate_params(rts, ints)
        if all(start_values):
            fit_params = fit_curve(rts, ints, gaussian_peak, start_values)
        if fit_params is None:
            fit_params = rough_estimate_gauss_params(rts, ints)
        y_fit = gaussian_peak(rts, *fit_params)
        # standard normalization
        y_norm = _normalize(y_fit)
        ints_norm = _normalize(ints)
        return np.sum(y_norm * ints_norm)


def rough_estimate_gauss_params(rts, ints):
    # we isolate peaks by +- 2fwhm -> 4.71 * sigma
    sigma = (max(rts) - min(rts)) / (4.71 * 2)
    mu = 0.5 * (max(rts) + min(rts))
    intensity = max(ints) * np.sqrt(2 * np.pi * sigma**2)
    return sigma, mu, intensity


def _normalize(values):
    z_trans = (values - np.mean(values)) / (np.std(values) + 0.01)
    return z_trans / np.linalg.norm(z_trans)  # Frobenius norm


def estimate_params(rts, ints):
    mu = rts[np.where(ints == max(ints))][0]
    pos = np.where(ints >= 0.682 * max(ints))
    s = (max(rts[pos]) - min(rts[pos])) / 2
    intensity = max(ints) * np.sqrt(2 * np.pi * s**2)
    return s, mu, intensity


def gaussian_peak(t, sigma, rt, intensity):
    v = (
        np.sqrt(2 * np.pi * sigma**2) ** (-1)
        * np.exp(-((t - rt) ** 2) / (2 * sigma**2))
        * intensity
    )
    return v


def fit_curve(x, y, fun, params, sigma=None):
    #    import pdb; pdb.set_trace()
    try:
        popt, _ = curve_fit(
            fun, np.array(x), np.array(y), p0=params, sigma=sigma, maxfev=10000
        )
        return popt
    except:
        pass


def set_peak_bounderies(model):
    rts, ints = model.graph()
    if len(rts):
        i, j = _get_bounderies(ints)
        return rts[i:j], ints[i:j]
    return np.array([]), np.array([])


def _get_bounderies(ints):
    # start = 0
    # end = len(ints)
    # zero_pos = np.where(ints==0)[0]
    value_pos = np.where(ints > 0)[0]
    if len(value_pos):
        rshift = 1 if max(value_pos) < len(ints) else 0
        lshift = -1 if min(value_pos) > 0 else 0
        return min(value_pos) + lshift, max(value_pos) + 1 + rshift
    return 0, 0


def _update_linear_model(t, model_col, ms_data_type):
    name2type = dict(zip(t.col_names, t.col_types))
    name2format = dict(zip(t.col_names, t.col_formats))
    all_linear = all([is_linear(model) for model in t[model_col]])
    t.add_column("temp_", t[model_col], object)
    # ----------------------------------------------------------
    # # FIX We drop existing integration associated columns
    # drop_cols = ('area_chromatogram',
    #  'model_chromatogram',
    #  'peak_shape_model_chromatogram',
    #  'rmse_chromatogram',
    #  'valid_model_chromatogram')
    # t.drop_columns(*drop_cols)
    # ----------------------------------------------------------
    if not all_linear:
        integrate_table(t, ms_data_type=ms_data_type, in_place=True)
        # integrate_chromatograms(t, "linear", in_place=True)
    t.add_or_replace_column("linear_model", t[model_col], object)
    pstfx = "" if ms_data_type == "Spectra" else "_chromatogram"
    column2attribute = {
        "peak_shape_model" + pstfx: "model_name",
        "area" + pstfx: "area",
        "rmse" + pstfx: "rmse",
        "valid_model" + pstfx: "is_valid",
    }
    for column, attribute in column2attribute.items():
        t.replace_column(
            column,
            t.apply(getattr, t.temp_, attribute),
            name2type[column],
            format_=name2format[column],
        )
    t.replace_column(model_col, t.temp_, object)
    t.drop_columns("temp_")


def is_linear(model):
    if model is not None:
        return model.model_name == "linear"
    else:
        return False


def _column_with_pstfx(name, ms_data_type):
    pstfx = "" if ms_data_type == "Spectra" else "_chromatogram"
    return name + pstfx
