# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 12:24:42 2023

@author: pkiefer
"""


def normalize_peaks(t, kwargs):
    _normalize(t, **kwargs)
    return t


def _normalize(
    t,
    peak_group_col="compound",
    std_group_col="std_id",
    norm_id_col="normalize_by_std_id",
    value_col="area_chromatogram",
    sample_wise=True,
    source_col="filename",
    isotopologue_col=None,
    **kwargs
):
    """
    normalizes the sum of quantifier peaks by the sum of standard peaks
    If standard peaks are missing it determines sum of quantifier peaks.

    Parameters
    ----------
    t : TYPE
        DESCRIPTION.
    peak_group_col : TYPE, optional
        DESCRIPTION. The default is 'pid'.
    std_group_col : TYPE, optional
        DESCRIPTION. The default is 'std_id'.
    norm_id_column : TYPE, optional
        DESCRIPTION. The default is 'normalize_by_std_id'.
    value_col : TYPE, optional
        DESCRIPTION. The default is 'area'.
    sample_wise : TYPE, optional
        DESCRIPTION. The default is True.
    source_col: str,
        Nome of column containing filenames. The default is 'filename'.
    Returns
    -------
    t : TYPE
        DESCRIPTION.

    """

    # we define column names
    group_value_col = "_".join([peak_group_col, value_col])
    std_value_col = "_".join([std_group_col, value_col])
    # since column names have to be different and in case of isotopologue
    # distribution we can use the same column for peak_group_col, and std_group_col
    if peak_group_col == std_group_col:
        std_value_col = std_value_col + "_"
    norm_col = "normalization_" + value_col
    normalized_value_col = "_".join(["normalized", value_col])
    # we determine the total area of grouped peaks (nominator)
    pid_col = norm_id_col if isotopologue_col is None else isotopologue_col
    columns = [source_col, sample_wise, peak_group_col, pid_col]
    # columns.append(isotopologue_col) if isotopologue_col is not None else None
    expr = _get_expression(t, *columns)
    t.add_or_replace_column(
        group_value_col,
        t.group_by(*expr).sum(t[value_col]),
        float,
        format_="%.2e",
        insert_after=value_col,
    )
    expr = _get_expression(t, source_col, sample_wise, std_group_col)
    t.add_or_replace_column(
        std_value_col,
        t.group_by(*expr).sum(t[value_col]),
        float,
        format_="%.2e",
        insert_after=group_value_col,
    )

    ## since analyte and standard signals are in different rows we transfer
    ## the grouped standard signals into the row of the corresponding analyte signal
    std_id2amount = dict(zip(zip(*expr), t[std_value_col]))
    expr = _get_expression(t, source_col, sample_wise, norm_id_col)
    t.add_or_replace_column(
        norm_col,
        t.apply(_get_norm_col, std_id2amount, *expr, ignore_nones=False),
        float,
        format_="%.2e",
        insert_after=std_value_col,
    )
    t.drop_columns(std_value_col)
    _peaks_without_is(
        t,
        peak_group_col,
        std_group_col,
        norm_id_col,
        group_value_col,
        value_col,
        norm_col,
        source_col,
    )
    t.add_or_replace_column(
        normalized_value_col, t[group_value_col] / t[norm_col], float, format_="%.2e"
    )
    return t


def _peaks_without_is(
    t,
    peak_group_col,
    std_group_col,
    norm_id_col,
    group_value_col,
    value_col,
    norm_col,
    source_col,
):
    # compounds without defined internal standard peaks
    # -> we set the normalization value to -> 1.0
    #  if all grouped peaks are without internal standard

    # stdid2stdid = dict(zip(t[std_group_col], t[std_group_col]))
    t.add_or_replace_column(
        "no_std",
        t.apply(_no_std, t[std_group_col], t[norm_id_col], ignore_nones=False),
        bool,
    )

    t.add_or_replace_column(
        "no_std_peaks",
        t.group_by(t[peak_group_col], t[source_col], group_nones=True).aggregate(
            _no_stds, t.no_std
        ),
        bool,
    )
    t.replace_column(
        norm_col,
        (t.no_std_peaks == True).then_else(1.0, t[norm_col]),
        float,
        format_="%.2e",
    )
    t.add_or_replace_column(
        "area_sum_",
        t.group_by(t[peak_group_col], t[source_col], group_nones=True).sum(
            t[value_col]
        ),
        float,
        format_="%.2e",
    )
    t.replace_column(
        group_value_col,
        (t.no_std_peaks == True).then_else(t.area_sum_, t[group_value_col]),
        float,
        format_="%.2e",
    )
    t.drop_columns("no_std", "no_std_peaks", "area_sum_")


def _no_std(std_id, norm_id):
    return std_id is None and norm_id is None
    # return True if d.get(key) is not None else False


def _no_stds(no_stds):
    return all(no_stds)


def _get_expression(t, source_col, sample_wise, *group_cols):
    expression = [t[group_col] for group_col in group_cols]
    expression.append(t[source_col]) if sample_wise else None
    return expression


def _get_norm_col(d, *cols):
    return d.get(cols)


def _pstfx(colname):
    x = "_chromatogram"
    fields = [x] if x in colname else []
    blocks = colname.split("__")
    if len(blocks) == 2:
        if not len(fields):
            return "__" + blocks[-1]
        fields.append(blocks[-1])
        return "__".join(fields)
    return x if len(fields) else ""
