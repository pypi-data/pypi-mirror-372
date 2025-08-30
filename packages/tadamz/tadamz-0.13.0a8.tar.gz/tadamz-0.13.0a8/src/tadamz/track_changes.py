# -*- coding: utf-8 -*-
"""
Created on Mon Apr  7 10:08:32 2025

@author: pkiefer
"""
from emzed import gui, MzType, RtType
from collections import defaultdict


def inspect_with_track_changes(table, kwargs={}):
    _inspect_with_track_changes(table, **kwargs)
    pass


def _inspect_with_track_changes(
    table,
    tracked_columns=[
        "rtmin_chromatogram",
        "rtmax_chromatogram",
        "area_chromatogram",
        "peak_shape_model_chromatogram",
    ],
    immutable_columns=[],
    rel_tol_float=1e-6,
    **kwargs,
):
    t_ref = _get_ref_table(table, tracked_columns, immutable_columns)
    gui.inspect(table)
    _reset_immutable_columns(table, t_ref, immutable_columns)
    _track_changes(table, t_ref, tracked_columns, rel_tol_float)


def _get_ref_table(table, tracked_columns, immutable_columns):
    assert "row_id" in table.col_names, "Column `row_id` is missing!"
    cols = ["row_id"]
    cols.extend(tracked_columns)
    cols.extend(immutable_columns)
    return table.extract_columns(*cols)


def _track_changes(table, t_ref, tracked_columns, rel_tol_float):
    t_comp = table.join(t_ref, table.row_id == t_ref.row_id)
    track_dict, row_ids = _collect_differences(t_comp, tracked_columns, rel_tol_float)
    table.meta_data["tracked_changes"] = track_dict
    table.meta_data["changed_rows"] = row_ids


def _reset_immutable_columns(t, t_ref, immutable_columns):
    col2pair = dict(zip(t.col_names, zip(t.col_types, t.col_formats)))
    for col in immutable_columns:
        d = dict(zip(t_ref.row_id, t_ref[col]))
        t.replace_column(
            col, t.apply(d.get, t.row_id), col2pair[col][0], format_=col2pair[col][1]
        )


def _collect_differences(t_comp, tracked_columns, rel_tol):
    pstfx = t_comp.supported_postfixes([])[-1]
    col2type = dict(zip(t_comp.col_names, t_comp.col_types))
    col2tid2tuple = defaultdict(dict)
    row_ids = set([])
    for col in tracked_columns:
        # import pdb; pdb.set_trace()
        for tid, val, ref_val in zip(t_comp.row_id, t_comp[col], t_comp[col + pstfx]):
            if col2type[col] in [float, MzType, RtType]:
                if _is_diff(val, ref_val, rel_tol):
                    col2tid2tuple[col][tid] = {"after": val, "before": ref_val}
                    row_ids.add(tid)
            elif col2type[col] in [int, str]:
                if _is_diff(val, ref_val):
                    col2tid2tuple[col][tid] = {"after": val, "before": ref_val}
                    row_ids.add(tid)
            else:
                msg = f"no difference check for column {col} of type {col2type[col]}"
                print(msg)
    return col2tid2tuple, row_ids


def _is_diff(v1, v2, rel_tol=None):
    if v1 is None and v2 is None:
        return False
    if v1 is None or v2 is None:
        return True
    return abs((v1 - v2) / (v2 + 1e-16)) > rel_tol if rel_tol is not None else v1 != v2


def reset_track_changes(table):
    col2info = dict(zip(table.col_names, zip(table.col_types, table.col_formats)))
    d = table.meta_data.pop("tracked_changes")
    table.meta_data.pop("changed_rows")
    for col, rid2pair in d.items():
        table.replace_column(
            col,
            table.apply(
                _replace, rid2pair, table.row_id, table[col], ignore_nones=False
            ),
            col2info[col][0],
            format_=col2info[col][1],
        )


def _replace(rid2pair, rid, current):
    return rid2pair[rid]["before"] if rid in rid2pair.keys() else current


def extract_track_changes(
    table, process_only_tracked_changes, splitting_cols=["filename", "compound"]
):
    if not process_only_tracked_changes:
        return table, None
    return _extract_changes(table, splitting_cols)


def _extract_changes(table, splitting_cols):
    selected = []
    if _track_changes_applied(table):
        t_tracked = table.filter(
            table.row_id.is_in(table.meta_data["changed_rows"]), keep_view=True
        )
        ntuples = set(zip(*[t_tracked[col] for col in splitting_cols]))
        for rid, ntuple in zip(
            table.row_id, zip(*[table[col] for col in splitting_cols])
        ):
            if ntuple in ntuples:
                selected.append(rid)
        return table.filter(table.row_id.is_in(selected)), table.filter(
            table.row_id.is_in(selected) == False
        )
    return table[:0].consolidate(), table


def _track_changes_applied(t):
    msg = "track changes was not applied. The complete table will be re processed."
    tracked = "changed_rows" in t.meta_data.keys()
    if not tracked:
        print(msg)
    return tracked
