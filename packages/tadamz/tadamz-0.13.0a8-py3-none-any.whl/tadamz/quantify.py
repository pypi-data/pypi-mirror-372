# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 12:26:37 2023

@author: pkiefer
"""
import numpy as np
from emzed import Table

# from .calibration import basic_calibration_functions as bcf
from .calibration.calibration_model import CalibrationModel
from .utils import cleanup_last_join
from copy import deepcopy


def quantify(table, kwargs, calibration_table=None):
    if calibration_table is not None:
        table = _update_calibration_data(table, calibration_table, **kwargs)
    _check_table(table)
    update_amounts(table, **kwargs)
    return table


def update_amounts(
    t,
    compound_col="compound",
    value_col="normalized_area_chromatogram",
    amount_col="amount",
    unit_col="unit",
    **kwargs,
):
    update = t.add_or_replace_column
    update(
        "temp",
        t.apply(_get_amount, t[value_col], t.calibration_model, ignore_nones=False),
        object,
    )
    update(
        amount_col + "_nominal",
        t.apply(lambda v: v.nominal_value, t.temp),
        float,
        format_="%.3f",
    )
    update(
        amount_col + "_std", t.apply(lambda v: v.std_dev, t.temp), float, format_="%.3f"
    )
    update(unit_col, t.apply(lambda v: v.unit, t.calibration_model), str)
    update("LOD", t.apply(lambda v: v.lod, t.calibration_model), float, format_="%.3f")
    update("LOQ", t.apply(lambda v: v.loq, t.calibration_model), float, format_="%.3f")
    update(
        amount_col + "_range", t.apply(lambda v: v.x_range, t.calibration_model), object
    )
    t.drop_columns("temp")


def _get_amount(value, model):
    if isinstance(model, CalibrationModel):
        try:
            return model.get_amount(value)
        except:
            msg = f"model results no real value for {model.compound}"
            print(msg)


def _update_calibration_data(
    t,
    t_cal,
    compound_col="compound",
    value_col="normalized_area_chromatogram",
    amount_col="amount",
    unit_col="unit",
    **kwargs,
):
    meta_data = deepcopy(t.meta_data)
    print(t_cal.col_names)
    print(unit_col)
    t_cal = _update_misssing_models(t, t_cal, compound_col, unit_col)
    t_cal = t_cal.extract_columns(compound_col, unit_col, "calibration_model")
    t = t.left_join(t_cal, t[compound_col] == t_cal[compound_col])
    cleanup_last_join(t)

    t.replace_column(
        "calibration_model",
        t.calibration_model.if_not_none_else(
            t.apply(_add_empty_model, t[compound_col], t[unit_col])
        ),
        object,
    )
    _update_meta_data(t, meta_data)
    return t
    # update = t.add_or_replace_column
    # comp2model = dict(zip(t_cal.compound, t_cal.calibration_model))
    # # update(
    # #     "calibration_model",
    # #     t[compound_col].lookup(t_cal[compound_col], t_cal.calibration_model),
    # #     object,
    # # )
    # update('calibration_model', t.apply(comp2model.get, t.compound, ignore_nones=False), object)


def _add_empty_model(compound, unit):
    model = CalibrationModel(
        np.array([[]]), np.array([]), np.array([[]]), compound, "none", unit, "linear"
    )
    model.fit_calibration_curve()
    return model


def _update_misssing_models(t, t_cal, compound_col, unit_col):
    unit = t_cal[unit_col].unique_value()
    t_cal = t_cal.extract_columns(compound_col, "calibration_model", unit_col)
    missings = set(t[compound_col]) - set(t_cal[compound_col])
    rows = []
    for compound in missings:
        model = CalibrationModel(
            np.array([[]]),
            np.array([]),
            np.array([[]]),
            compound,
            "none",
            unit,
            "linear",
        )
        row = [compound, model, unit]
        rows.append(row)
    t_miss = Table.create_table(t_cal.col_names, t_cal.col_types, rows=rows)
    return Table.stack_tables([t_cal, t_miss])


def _check_table(t):
    msg = "column `calibration_model` is not in table. Please provide a calibration table!"
    assert "calibration_model" in t.col_names, msg


def _update_meta_data(t, meta_data):
    for key, value in meta_data.items():
        t.meta_data[key] = value
