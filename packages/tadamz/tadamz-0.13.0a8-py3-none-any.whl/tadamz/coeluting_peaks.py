# -*- coding: utf-8 -*-
"""
Created on Sun Dec 10 10:12:24 2023

@author: pkiefer
"""
import numpy as np
from scipy.spatial import distance
from itertools import combinations
from collections import defaultdict
from .adapt_retention_time import adapt_rt_by_coeluting_peaks
from .utils import color_column_by_value


def coeluting_peaks(t, kwargs):
    _coeluting_peaks(t, **kwargs)
    t = adapt_rt_by_coeluting_peaks(t, **kwargs)
    _coeluting_peaks(t, **kwargs)
    return t


def _coeluting_peaks(
    t,
    group_id_column="compound",
    reference_column="is_coelution_reference_peak",
    source_col="filename",
    # dt=0.1,
    only_use_ref_peaks=True,
    **kwargs,
):
    """


    Parameters
    ----------
    t : Table
        integrated peaks_table. required columns are `filename`
    group_id_column : string
        column grouping coeuting peaks.
    reference_id_column : string, optional
        If given, coelution is tested relative to peak with reference id.
        The default is is_coelution_reference_peak.
    source : TYPE, optional
        column name containing acquisition data file. The default is filename.
    only_use_ref_peaks: bool, optional
        If true the cosine distance to median rt of all grouped peaks is
        calculated. The default is False.
    **kwargs : dict
        handles additional unused arguments.

    Returns
    -------
    t : Table
        table with added cosine distance column

    """
    class2color = {"no coelution": "#FF0000", "critical": "#FFFF00", "ok": "#00FF00"}
    # model_col = 'model_chromatogram'
    t.add_enumeration("uid")
    uid2dist = _get_uid2distance(
        t, group_id_column, reference_column, source_col, only_use_ref_peaks
    )
    colname = "cosine_distance" if only_use_ref_peaks else "median_cosine_distance"
    t.add_or_replace_column(
        colname,
        t.apply(uid2dist.get, t.uid, ignore_nones=False),
        float,
        format_="%.3f",
        insert_after="model_chromatogram",
    )
    t.add_or_replace_column(
        "peak_coelutes",
        t.apply(_get_category, t[colname], ignore_nones=False),
        str,
        insert_after="id",
    )
    color_column_by_value(t, "peak_coelutes", class2color)
    t.drop_columns("uid")


def _get_uid2distance(
    t, group_id_column, reference_id_column, source_col, only_use_ref_peaks
):
    uid2dist = {}
    for group_id, filename in set(zip(t[group_id_column], t[source_col])):
        expr = (t[group_id_column] == group_id) & (t[source_col] == filename)
        sub = t.filter(expr, keep_view=True)
        if only_use_ref_peaks:
            if _has_reference(sub, group_id_column, reference_id_column):
                t_id = sub.filter(sub[reference_id_column], keep_view=True)
                uid2dist.update(
                    ref_cosine_distance(
                        t_id, sub.uid.to_list(), sub.model_chromatogram.to_list()
                    )
                )

        else:
            uid2dist.update(
                median_cosine_distance(
                    sub.uid.to_list(), sub.model_chromatogram.to_list()
                )
            )

    return uid2dist


def _has_reference(t, group_id, ref_id):
    assert ref_id in t.col_names, f"Column {ref_id} is missing!"
    if any(t[ref_id].to_list()):
        _check_gid_assignment(t, group_id, ref_id)
        return True


def _check_gid_assignment(t, group_id, ref_id):
    d = defaultdict(int)
    for gid, is_ref in zip(t[group_id], t[ref_id]):
        if is_ref:
            d[gid] += 1
    values = np.array(list(d.values()))
    msg = """"At LEAST ONE reference peak per group is required! """
    assert np.min(values) >= 1, msg


def ref_cosine_distance(t_id, ids, models):
    # import pdb; pdb.set_trace()
    d = defaultdict(list)
    rts = _rts(models)
    for ref_uid, ref_model in zip(t_id.uid, t_id.model_chromatogram):
        ref_peak = _fit_peak(rts, ref_model)
        for id_, model in zip(ids, models):
            peak = _fit_peak(rts, model)
            # since model and hence peak can be None we check for the type
            if type(ref_peak) == np.ndarray and type(peak) == np.ndarray:
                cos_dist = distance.cosine(ref_peak, peak)
                d[id_].append(cos_dist)
            else:
                d[id_].append(1)
    return _determine_mean_distance(d)


def _determine_mean_distance(uid2dists):
    return {key: _mean(value) for key, value in uid2dists.items()}


def _mean(values):
    values = [v for v in values if v is not None]
    return np.mean(values) if len(values) else None


def median_cosine_distance(ids, models):
    try:
        rts = _rts(models)
        dist_mat = np.zeros((len(ids), len(ids)))
        for i, j in combinations(range(len(models)), 2):
            peak1 = _fit_peak(rts, models[i])
            peak2 = _fit_peak(rts, models[j])
            if type(peak1) == np.ndarray and type(peak2) == np.ndarray:
                cos_dist = distance.cosine(peak1, peak2)
            else:
                cos_dist = 1
            dist_mat[j][i] = cos_dist

        return dict(zip(ids, np.median(dist_mat, axis=0)))
    except:
        import pdb

        pdb.set_trace()
        msg = """ This should never happen. Please contact pkiefer
        """
        print(msg)


def _fit_peak(rts, model):
    if model is None:
        return model
    try:
        ints = model.apply(rts)
    except:
        rts_, ints_ = model.graph()
        if not len(rts_):
            return
        ints = np.interp(rts, rts_, ints_, 0, 0)
    return ints


def _get_category(distance):
    category = "no coelution"
    if distance is None:
        return category
    if distance <= 0.2:
        category = "critical"
    if distance <= 0.1:
        category = "ok"
    return category


def _rts(models):
    # we estimate dt from measured delta rts
    rts = []
    drts = []
    for model in models:
        if model is not None:
            rts_ = model.graph()[0]
            if len(rts_):
                rts.extend(rts_)
                deltas = np.diff(rts)
                if len(deltas):
                    drts.append(np.nanmin(deltas))
    # models failed to fitting a peak return nan values
    if np.any(np.isnan(rts)):
        rts = [rt for rt in rts if not np.isnan(rt)]
    if len(rts):
        dt = _estimate_dt(drts)
        return np.arange(np.nanmin(rts), np.nanmax(rts), dt)
    return np.array([])


def _estimate_dt(drts, mindt=1e-2):
    drts = np.array(drts)
    drts = drts[drts > 0]
    return np.min(drts) / 2 if len(drts) else mindt
