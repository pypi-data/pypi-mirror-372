# -*- coding: utf-8 -*-
"""
Created on Tue Jul  4 16:52:40 2023

@author: pkiefer
"""

from .utils import get_group_cols


def tic_normalize_peaks(t, kwargs):
    return _normalize_by_tic(t, **kwargs)


def _normalize_by_tic(
    t,
    peak_group_col="id",
    amount_col="area_chromatogram",
    tic_col="tic_area",
    sample_wise=True,
    **kwargs
):
    """


    Parameters
    ----------
    t : TYPE
        DESCRIPTION.
    peak_group_col : TYPE, optional
        DESCRIPTION. The default is 'pid'.
    amount_col : TYPE, optional
        DESCRIPTION. The default is 'area'.
    tic_col : TYPE, optional
        DESCRIPTION. The default is 'tic_area'.
    sample_wise : TYPE, optional
        DESCRIPTION. The default is True.

    Returns
    -------
    t : Table


    """

    group_cols = get_group_cols(t, peak_group_col, sample_wise)
    expr = [t[group_col] for group_col in group_cols]
    group_amount_col = "_".join([peak_group_col, amount_col])
    t.add_or_replace_column(
        group_amount_col,
        t.group_by(*expr).sum(t[amount_col]),
        float,
        format_="%.2e",
        insert_after=amount_col,
    )
    norm_value = amount_col + "_per_" + tic_col
    t.add_or_replace_column(
        norm_value,
        t[group_amount_col] / t[tic_col],
        float,
        format_="%.2e",
        insert_after=tic_col,
    )
    return t


def pq_normalize_peaks(t, kwargs):
    return _normalize_by_pq(t, **kwargs)


def _normalize_by_pq(
    t,
    id_col="id",
    sample_type_col="sample_type",
    sample_type="QC",
    value_col="area_chromatogram",
    filename_col="filename",
):
    """


    Parameters
    ----------
    t : TYPE
        DESCRIPTION.
    id_col : TYPE, optional
        DESCRIPTION. The default is 'id'.
    sample_type_col : TYPE, optional
        DESCRIPTION. The default is 'sample_type'.
    sample_type : TYPE, optional
        DESCRIPTION. The default is 'QC'.
    value_col : TYPE, optional
        DESCRIPTION. The default is 'area_chromatogram'.
    filename_col : TYPE, optional
        DESCRIPTION. The default is 'filename'.

    Returns
    -------
    t : TYPE
        DESCRIPTION.

    """
    t_denom = t.filter(t[sample_type_col] == sample_type)
    t_denom.add_column(
        "median_response",
        t_denom.group_by(t_denom[id_col]).median(t_denom[value_col]),
        float,
    )
    id2resp = dict(zip(t_denom[id_col], t_denom.median_response))
    update = t.add_or_replace_column
    update("_denom", t.apply(id2resp.get, t[id_col], ignore_nones=False), float)
    update("ratio", t[value_col] / t._denom, float)
    update(
        "pq_denom",
        t.group_by(t[filename_col]).median(t.ratio),
        float,
        format_="%.2e",
        insert_after=value_col,
    )
    colname = "pqn_" + value_col
    update(
        colname,
        t[value_col] / t.pq_denom,
        float,
        format_="%.2e",
        insert_after="pq_denom",
    )
    t.drop_columns("_denom", "ratio")
    return t
