# -*- coding: utf-8 -*-
"""
Created on Thu Apr  3 15:32:25 2025

@author: pkiefer
requirements there is only 1 quantifier peak per compound. The qualifier
refers NOT to internal standard peaks

"""
from collections import defaultdict
from .utils import color_column_by_value


def check_qualifier_peaks(table, kwargs):
    _check_qualifier_peaks(table, **kwargs)
    return table


def _check_qualifier_peaks(
    table,
    group_peak_col="compound",
    qualifier_col="is_qualifier",
    value_col="area_chromatogram",
    source_col="filename",
    lower_limit_col="qualifier_ratio_min",
    upper_limit_col="qualifier_ratio_max",
    **kwrags,
):
    table.add_enumeration("rid")
    rid2ratio = _extract_qualifier_ratios(
        table, group_peak_col, source_col, value_col, qualifier_col
    )
    table.add_or_replace_column(
        "qualifier_ratio",
        table.apply(rid2ratio.get, table.rid, ignore_nones=False),
        float,
        format_="%.3f",
        insert_after=qualifier_col,
    )
    table.add_or_replace_column(
        "qualifier_quality_check",
        table.qualifier_ratio.in_range(
            table[lower_limit_col], table[upper_limit_col]
        ).then_else("passed", "failed"),
        str,
        insert_after=table.col_names[0],
    )
    class2color = {"failed": "#FF0000", "passed": "#00FF00"}
    color_column_by_value(table, "qualifier_quality_check", class2color)
    table.drop_columns("rid")


def _extract_qualifier_ratios(
    table, group_peak_col, source_col, value_col, qualifier_col
):
    gid2values = defaultdict(dict)
    rid2ratio = {}
    # group = table.group_by(table[group_peak_col], table[source_col])
    _update_item_id(table, group_peak_col, source_col)
    for rid, item_id, value, is_qualifier in zip(
        table.rid, table.item_id, table[value_col], table[qualifier_col]
    ):
        if is_qualifier == True:
            gid2values[item_id][rid] = value
        elif is_qualifier == False:
            assert (
                "quantifier" not in gid2values[item_id]
            ), f"you have more than one quantifier per qualifier in row {rid}"
            gid2values[item_id]["quantifier"] = value
        else:
            pass
    for d in gid2values.values():
        q = d.pop("quantifier")
        for rid in d.keys():
            try:
                rid2ratio[rid] = q / d[rid]
            except:
                rid2ratio[rid] = None
    table.drop_columns("item_id")
    return rid2ratio


def _update_item_id(t, group_peak_col, source_col):
    count = 0
    d = {}
    for key in set(zip(t[group_peak_col], t[source_col])):
        d[key] = count
        count += 1
    t.add_column("item_id", t.apply(_update, d, t[group_peak_col], t[source_col]), int)


def _update(d, key1, key2):
    return d.get((key1, key2))
