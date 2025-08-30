# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 15:52:27 2023

@author: pkiefer
"""

from src.tadamz import processing_steps as ps
from src.tadamz import in_out
import pytest
from emzed import Table
import os

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


@pytest.fixture
def result_post():
    path = os.path.join(data_folder, "test_processing_steps_changed_rows.table")
    return in_out.load_tadamz_table(path)


@pytest.fixture
def result_pqn():
    columns = ["id", "area_chromatogram", "filename", "sample_type"]
    coltypes = [int, float, str, str]
    rows = [
        [0, 1e5, "S1", "Sample"],
        [1, 1.5e5, "S1", "Sample"],
        [2, 3e5, "S1", "Sample"],
        [3, 1e5, "S1", "Sample"],
        [4, 2e5, "S1", "Sample"],
        [0, 1e4, "Q1", "QC"],
        [1, 2e5, "Q1", "QC"],
        [2, 2e5, "Q1", "QC"],
        [3, 1e5, "Q1", "QC"],
        [4, 2e5, "Q1", "QC"],
        [0, 3e4, "Q2", "QC"],
        [1, 2e5, "Q2", "QC"],
        [2, 2e5, "Q2", "QC"],
        [3, 1e5, "Q2", "QC"],
        [4, 2e5, "Q2", "QC"],
    ]
    return Table.create_table(columns, coltypes, rows=rows)


@pytest.fixture
def config_pqn():
    d = {
        "pq_normalize_peaks": {},
        "postprocessing0": ["pq_normalize_peaks"],
        "postprocessings": ["postprocessing0"],
    }
    return d


@pytest.fixture
def config_srm():
    path = os.path.join(data_folder, "test_mrm_config.txt")
    return in_out.load_config(path)


@pytest.fixture
def kwargs():
    return {"ms_data_type": "MS_Chromatogram"}


@pytest.fixture
def kwargs1():
    return {"ms_data_type": "Spectra"}


def test_postprocess_0(result_post, config_srm):
    pr_all = ps.PostProcessResult(result_post, config_srm)
    pr_sub = ps.PostProcessResult(
        result_post, config_srm, process_only_tracked_changes=True
    )
    pr_all.normalize_peaks()
    pr_sub.normalize_peaks()
    pr_sub.merge_reprocessed()
    # print(pr_sub.result)
    # print(pr_all.result)
    is_ = dict(zip(pr_sub.result.row_id, pr_sub.result.normalized_area_chromatogram))
    exp = dict(zip(pr_all.result.row_id, pr_all.result.normalized_area_chromatogram))
    print(is_)
    print(exp)
    exp = dict(zip(pr_all.result.row_id, pr_all.result.normalized_area_chromatogram))

    def _comp(v1, v2):
        if v1 is None and v2 is None:
            return True
        return abs(v1 - v2) / v2 < 1e-16

    assert all([_comp(is_[key], exp[key]) for key in exp.keys()])


def test_postprocess_1(result_post, config_srm):
    exp = dict(zip(result_post.row_id, result_post.normalized_area_chromatogram))
    result_post.meta_data["tracked_change"] = {}
    result_post.meta_data["changed_rows"] = set()
    pr_sub = ps.PostProcessResult(
        result_post, config_srm, process_only_tracked_changes=True
    )
    pr_sub.normalize_peaks()
    pr_sub.merge_reprocessed()
    # print(pr_sub.result)
    # print(pr_all.result)
    is_ = dict(zip(pr_sub.result.row_id, pr_sub.result.normalized_area_chromatogram))
    print(is_)
    print(exp)

    def _comp(v1, v2):
        if v1 is None and v2 is None:
            return True
        return abs(v1 - v2) / v2 < 1e-16

    assert all([_comp(is_[key], exp[key]) for key in exp.keys()])


def test_postprocess_2(result_pqn, config_pqn):
    is_ = ps.PostProcessResult(result_pqn, config_pqn)
    is_.pq_normalize_peaks()
    # print(is_.result.pqn_area_chromatogram.to_list())
    print(is_.result)
    print(is_.result.meta_data)
    cols = set(["pq_denom", "pqn_area_chromatogram"])
    cond1 = cols - set(is_.result.col_names) == set()
    cond2 = is_.result.pq_denom.unique_value() == 1.0
    assert all([cond1, cond2])
