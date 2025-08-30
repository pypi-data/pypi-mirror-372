# -*- coding: utf-8 -*-
"""
Created on Tue Jun 11 09:23:07 2024

@author: pkiefer
"""
import numpy as np
import emzed
from collections import defaultdict
from datetime import datetime

# from . import basic_calibration_functions as bcf
from .calibration_model import CalibrationModel

# from calibration_model import CalibrationModel

from ..utils import cleanup_last_join


# _______________ main function ________________


def calibrate(result_table, calibration_table, sample_table, kwargs):
    """
    generates calibration curves of all analytes from batch process.

    result_table : Table
        output table of targeted_workflow processing with mandatory columns:
        compound_col, value_col, source_col specified in -> kwargs.
    calibration_table : Table
        Table with mandatory columns sample_col, amount_col, compound_col, unit,
        specified in -> kwargs.
    sample_table : Table
        Table with mandatory columns source_col, sample_col, sample_type,
        specified in -> kwargs.

    Returns
    -------
    t_cal : Table
        Table with columns compound_col, calibration_model_dict, 'sample_' +amount_col,
        'sample_' + value_col

    """
    t_cal = build_calibration_table(
        result_table, calibration_table, sample_table, kwargs
    )
    prepare_calibration_table_evaluation(
        t_cal, result_table, calibration_table, sample_table, kwargs
    )
    return t_cal


#  _____________ main processing steps______________________


def build_calibration_table(result_table, calibration_table, sample_table, kwargs):
    """


    Parameters
    ----------
    result_table : Table
        output table of targeted_workflow processing with mandatory columns:
        compound_col, value_col, source_col specified in -> kwargs.
    calibration_table : Table
        Table with mandatory columns sample_col, amount_col, compound_col, unit,
        specified in -> kwargs.
    sample_table : Table
        Table with mandatory columns source_col, sample_col, sample_type,
        specified in -> kwargs.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    t_cal = extract_sample_type(result_table, sample_table, calibration_table, **kwargs)
    t_cal = extract_calibration_data(t_cal, **kwargs)
    update_calibration_model_settings(t_cal, **kwargs)
    default_calibration(t_cal, **kwargs)
    return edit_calibration_table(t_cal, **kwargs)


def prepare_calibration_table_evaluation(
    t_cal, result_table, calibration_table, sample_table, kwargs
):
    # BAUSTELLE
    """
    adds compound values determined in all samples to calibration table
    adds column include to amount table to allow user specific exclusion

    Parameters
    ----------
    t_cal : Table
        calibration table as returned by function calibrate (see above).
    result_table : Table
        output table of targeted_workflow processing with mandatory columns:
        compound_col, value_col, source_col specified in -> kwargs.
    calibration_table : Table
        Table with mandatory columns sample_col, amount_col, compound_col, unit,
        specified in -> kwargs.
    sample_table : Table
        Table with mandatory columns source_col, sample_col, sample_type,
        specified in -> kwargs.
    kwargs : dict
        config[calibrate] paramters dictionary. For details see -> calibrate.

    Returns
    -------
    None

    """
    # we extract sample response values and add them to the calibration table
    t_s = extract_sample_type(
        result_table, sample_table, calibration_table, sample_type="sample", **kwargs
    )
    if len(t_s):
        print(t_s.col_names)
        t_s = _extract_sample_data(t_s, **kwargs)
    update_values(t_cal, t_s, "sample", **kwargs)
    update_amounts(t_cal, "sample", **kwargs)


# _________________________ functions ___________________________________
def extract_sample_type(
    tr,
    ts,
    tc,
    sample_types,
    unit_col="unit",
    compound_col="compound",
    sample_type="standard",
    sample_type_col="sample_type",
    sample_id_col="sample_name",
    filename_col="filename",
    value_col="normalized_area_chromatogram",
    std_group_col="std_id",
    norm_id_col="normalize_by_std_id",
    external_calibration=False,
    **kwargs,
):
    # we remove all internal standard related rows if internal standard was applied
    type_ = sample_types[sample_type]
    tr = select_quantification_rows(
        tr, std_group_col, norm_id_col, external_calibration
    )
    calibrants = ts.filter(ts[sample_type_col] == type_)
    t = tr.join(calibrants, tr[filename_col] == calibrants[filename_col])
    cleanup_last_join(t)
    if sample_type == "standard":
        t = t.join(
            tc,
            (t[sample_id_col] == tc[sample_id_col])
            & (t[compound_col] == tc[compound_col]),
        )
        cleanup_last_join(t)
    else:
        d = defaultdict(set)
        for comp, unit in set(zip(tc[compound_col], tc[unit_col])):
            d[comp].add(unit)
        comp2unit = {}
        for comp, units in d.items():
            assert len(units) == 1
            comp2unit[comp] = units.pop()
        t.add_column(
            unit_col, t.apply(comp2unit.get, t[compound_col], ignore_nones=False), str
        )

    return t


def select_quantification_rows(
    t, std_id_col, norm_id_col, external_calibration, **kwargs
):
    if external_calibration:
        return t
    return t.filter((t[std_id_col].is_none() & t[norm_id_col].is_not_none()))


def _cleanup(t, drop_columns, pstfx="__0"):
    removes = ["".join([col, pstfx]) for col in drop_columns]
    t.drop_columns(*removes)
    t.rename_postfixes(**{pstfx: ""})


def unique_sample_files(t, sample_id_col, compound_col, filename_col, **kwargs):
    # for each analyte and sample name the number of different file nameuniqs corresponds
    # the len of the sub table
    ntuples = []
    for sub in t.split_by_iter(compound_col, sample_id_col):
        analyte = sub[compound_col].unique_value()
        no_files = len(sub)
        no_diff_files = len(set(sub[filename_col]))
        if no_files != no_diff_files:
            ntuples.append((analyte, str(no_files), str(no_diff_files)))
    if len(ntuples):
        cases = "\n".join([", ".join(ntuple) for ntuple in ntuples])

        msg = f""" compounds with non unique sample files:
        {cases}
        """
        assert False, msg


def _extract_sample_data(
    t,
    unit_col="unit",
    compound_col="compound",
    filename_col="filename",
    value_col="normalized_area_chromatogram",
    **kwargs,
):
    d = defaultdict(list)
    d1 = defaultdict(set)
    t = _remove_duplicates(t, compound_col, value_col, filename_col)
    for comp, value, unit in zip(t[compound_col], t[value_col], t[unit_col]):
        d[comp].append(value)
        d1[comp].add(unit)
    for key, values in d.items():
        d[key] = np.array(values)
    tr = emzed.to_table(compound_col, sorted(d), str)
    tr.add_column(value_col, tr.apply(d.get, tr[compound_col]), object)
    tr.add_column(
        unit_col, tr.apply(lambda v, w: v.get(w).pop(), d1, tr[compound_col]), str
    )
    tr.add_enumeration()
    return tr


def extract_calibration_data(
    t,
    compound_col="compound",
    filename_col="filename",
    amount_col="amount",
    value_col="normalized_area_chromatogram",
    **kwargs,
):
    t = _remove_duplicates(t, compound_col, value_col, filename_col)
    d = _collect_data(t, compound_col, amount_col, filename_col, value_col)
    compound2concs, compound2data, compound2fnames = _regroup_data(d)
    tr = emzed.to_table(compound_col, sorted(compound2concs), str)
    tr.add_column(amount_col, tr.apply(compound2concs.get, tr[compound_col]), object)
    tr.add_column(value_col, tr.apply(compound2data.get, tr[compound_col]), object)
    tr.add_column(filename_col, tr.apply(compound2fnames.get, tr[compound_col]), object)
    tr.add_column_with_constant_value("unit", t.unit.unique_value(), str)
    tr.add_enumeration()
    return tr


def _remove_duplicates(t, compound_col, value_col, source_col):
    df = t.to_pandas().drop_duplicates(subset=[compound_col, value_col, source_col])
    assert len(df) == len(set(zip(df[source_col], df[compound_col])))
    return emzed.Table.from_pandas(df)


def _collect_data(t, compound_col, amount_col, filename_col, value_col):
    d = defaultdict(dict)
    for compound, x, fname, y in zip(
        t[compound_col], t[amount_col], t[filename_col], t[value_col]
    ):
        if x in d[compound].keys():
            d[compound][x].append((fname, y))
        else:
            d[compound][x] = [(fname, y)]
    return d


def _regroup_data(d):
    compound2data = {}
    compound2concs = {}
    compound2fnames = {}
    for compound in d.keys():
        concs = sorted(d[compound])
        compound2concs[compound] = np.array(concs)
        rows = len(concs)
        cols = max([len(l) for l in d[compound].values()])
        data = np.zeros((rows, cols))
        fnames = np.zeros((rows, cols), dtype=object)
        data[data == 0] = np.nan
        for i, conc in enumerate(concs):
            for j, value in enumerate(d[compound][conc]):
                fnames[i][j] = value[0]
                data[i][j] = value[1]
        compound2data[compound] = np.array(data)
        compound2fnames[compound] = fnames
    return compound2concs, compound2data, compound2fnames


def update_calibration_model_settings(
    t, calibration_model_name, calibration_weight, compound_col="compound", **kwargs
):

    if "calibration_model_name" in t.col_names:
        t.replace_column(
            "calibration_model_name",
            t.colibration_model_name.if_not_none_else(calibration_model_name),
            str,
        )
    else:
        t.add_column_with_constant_value(
            "calibration_model_name", calibration_model_name, str
        )
    if "calibration_weight" in t.col_names:
        t.replace_column(
            "calibration_weight",
            t.colibration_weight.if_not_none_else(calibration_weight),
            str,
        )
    else:
        t.add_column_with_constant_value("calibration_weight", calibration_weight, str)


def _update_from_specific(specific, compound, key):
    if compound in specific.keys():
        return specific[compound].get(key)


# ____________


def assisted_calibration(t, amount_col, **kwargs):
    pass


def default_calibration(
    t,
    alpha_lodq,
    unit_col="unit",
    filename_col="filename",
    compound_col="compound",
    amount_col="amount",
    value_col="normalized_area_chromatogram",
    **kwargs,
):

    update = t.add_or_replace_column
    update(
        "calibration_model",
        t.apply(
            _get_calibration_model,
            t[filename_col],
            t[amount_col],
            t[value_col],
            t[compound_col],
            t.calibration_weight,
            t[unit_col],
            t.calibration_model_name,
            alpha_lodq,
        ),
        object,
        insert_after="calibration_model_name",
    )
    update(
        "calibration_weights",
        t.apply(lambda v: v.weights, t.calibration_model),
        object,
        insert_after=value_col,
    )
    update("fit_fun", t.apply(lambda v: v.fun, t.calibration_model), object)
    update(
        "inv_fit_fun",
        t.apply(lambda v: v.inv_fun, t.calibration_model),
        object,
    )
    update("popt", t.apply(lambda v: v.popt, t.calibration_model), object)
    update("perr", t.apply(lambda v: v.perr, t.calibration_model), object)
    _update_ranges(t, amount_col, value_col)
    update(
        "LOD", t.apply(lambda v: v.lod, t.calibration_model, ignore_nones=False), float
    )
    update(
        "LOQ", t.apply(lambda v: v.loq, t.calibration_model, ignore_nones=False), float
    )


def _update_ranges(t, amount_col, value_col):
    for column in amount_col, value_col:
        colname = column + "_range"
        t.add_or_replace_column(
            colname, t.apply(lambda v: (v[0], v[-1]), t[column]), object
        )


def _get_calibration_model(
    filenames,
    amounts,
    data,
    compound,
    calibration_weight,
    unit,
    calibration_model_name,
    alpha_lodq,
):
    model = CalibrationModel(
        filenames,
        amounts,
        data,
        compound,
        calibration_weight,
        unit,
        calibration_model_name,
        alpha_lodq,
    )
    model.fit_calibration_curve()
    model.determine_limits()
    return model


def get_namepairs(compound_col, amount_col, value_col):
    pairs = (
        (compound_col, "compound"),
        ("calibration_model_name", "calibration_model_name"),
        ("unit", "unit"),
        (amount_col, "x_values"),
        (value_col, "y_values"),
        ("popt", "popt"),
        ("perr", "perr"),
        ("LOD", "lod"),
        ("LOQ", "loq"),
    )
    return pairs


def edit_calibration_table(
    t, compound_col="compound", amount_col="amount", unit_col="unit", **kwargs
):
    t.add_column_with_constant_value(
        "calibration_date", datetime.today().strftime("%Y-%m-%d"), str
    )
    columns = [
        "id",
        compound_col,
        amount_col + "_range",
        unit_col,
        "calibration_model",
        "calibration_model_name",
        "LOD",
        "LOQ",
        "calibration_date",
    ]
    return t.extract_columns(*columns)


def update_values(
    t_target,
    t_source,
    sample_type,
    compound_col="compound",
    value_col="normalized_area_chromatogram",
    **kwargs,
):
    colname = "_".join([sample_type, value_col])
    if len(t_source):
        t_target.add_or_replace_column(
            colname,
            t_target[compound_col].lookup(t_source[compound_col], t_source[value_col]),
            object,
        )
    else:
        t_target.add_or_replace_column_with_constant_value(
            colname, np.array([]), object
        )


def update_amounts(
    t,
    prefix,
    amount_col="amount",
    value_col="normalized_area_chromatogram",
    **kwargs,
):
    colname = "_".join([prefix, amount_col])
    value_col = "_".join([prefix, value_col])
    t.add_or_replace_column(
        colname,
        t.apply(_update_amounts, t.calibration_model, t[value_col]),
        object,
    )


def _update_amounts(model, values):
    values = np.array(values, dtype=float)
    return model.get_amount(values)
