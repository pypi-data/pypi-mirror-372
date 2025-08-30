# -*- coding: utf-8 -*-
"""
Created on Tue Apr  8 09:35:06 2025

@author: pkiefer
"""

import pytest
import os
from emzed import Table
from src.tadamz import in_out
from src.tadamz import track_changes as tc

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


@pytest.fixture
def t_before():
    col_names = "row_id", "a", "b", "c"
    col_types = int, int, float, str
    rows = [[0, 1, 2.5, "hallo"], [1, 4, 7.31, "hi"], [2, 0, 0.1, "what"]]
    return Table.create_table(col_names, col_types, rows=rows)


@pytest.fixture
def t_after():
    col_names = "row_id", "a", "b", "c"
    col_types = int, int, float, str
    rows = [[0, 2, 0.3, "allo"], [1, 4, 7.31, "hi"], [2, 0, 0.1, "what"]]
    return Table.create_table(col_names, col_types, rows=rows)


@pytest.fixture
def result_post():
    path = os.path.join(data_folder, "test_processing_steps_changed_rows.table")
    return in_out.load_tadamz_table(path)


def test_track_changes_0(t_before, t_after):
    tracked_cols = "a", "b"
    immutable_cols = ("c",)
    t_ref = tc._get_ref_table(t_before, tracked_cols, immutable_cols)
    tc._track_changes(t_after, t_ref, tracked_cols, 0.01)
    is_ = t_after.meta_data["tracked_changes"]
    print(is_)
    expected = {
        "a": {0: {"after": 2, "before": 1}},
        "b": {0: {"after": 0.3, "before": 2.5}},
    }
    assert is_ == expected


def test_track_changes_1(t_before, t_after):
    tracked_cols = "a", "b"
    immutable_cols = ("c",)
    t_ref = tc._get_ref_table(t_before, tracked_cols, immutable_cols)
    tc._reset_immutable_columns(t_after, t_ref, immutable_cols)
    assert t_ref.rows[0]["c"] == t_after.rows[0]["c"]


def test_track_changes_2(t_before, t_after):
    tracked_cols = []
    immutable_cols = []
    expected = t_after.copy()
    t_ref = tc._get_ref_table(t_before, tracked_cols, immutable_cols)
    tc._track_changes(t_after, t_ref, tracked_cols, 0.01)
    tc._reset_immutable_columns(t_after, t_ref, immutable_cols)
    t_after.meta_data.pop("tracked_changes")
    t_after.meta_data.pop("changed_rows")
    assert t_after.unique_id == expected.unique_id


def test_track_changes_3(t_before):
    tracked_cols = "a", "b"
    immutable_cols = ("c",)
    t = t_before[:0].consolidate()
    t_ref = tc._get_ref_table(t, tracked_cols, immutable_cols)
    tc._track_changes(t, t_ref, tracked_cols, 0.01)
    tc._reset_immutable_columns(t, t_ref, immutable_cols)
    assert t.meta_data["tracked_changes"] == {}


def test_track_changes_4(t_before, t_after):
    tracked_cols = "a", "b"
    immutable_cols = ("c",)
    t_ref = tc._get_ref_table(t_before, tracked_cols, immutable_cols)
    tc._track_changes(t_after, t_ref, tracked_cols, 0.01)
    is_ = t_after.meta_data["changed_rows"]
    print(is_)
    expected = {0}
    assert is_ - expected == expected - is_


def test_reset_changes_0(t_before, t_after):
    tracked_cols = "a", "b", "c"
    t_ref = tc._get_ref_table(t_before, tracked_cols, [])
    tc._track_changes(t_after, t_ref, tracked_cols, 0.01)
    tc.reset_track_changes(t_after)
    assert t_before.unique_id == t_after.unique_id


def test_reset_changes_1(t_before):
    t = t_before[:0].consolidate()
    exp = t.copy()
    tracked_cols = "a", "b", "c"
    t_ref = tc._get_ref_table(t, tracked_cols, [])
    tc._track_changes(t, t_ref, tracked_cols, 0.01)
    tc.reset_track_changes(t)
    assert t.unique_id == exp.unique_id


def test_extract_track_changes_0(result_post):
    print(result_post.meta_data["changed_rows"])
    t, _ = tc.extract_track_changes(result_post, True)
    is_ = set(t.row_id)
    print(is_)
    expected = set(range(20, 30))
    assert is_ - expected == expected - is_


def test_extract_track_changes_1(result_post):
    _, is_ = tc.extract_track_changes(result_post, False)
    assert is_ is None


def test_extract_track_changes_2(result_post):
    t, _ = tc.extract_track_changes(result_post, True, ["compound", "filename"])
    is_ = set(t.row_id)
    expected = set(range(20, 30))
    print(is_)
    assert is_ - expected == expected - is_
