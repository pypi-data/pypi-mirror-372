# -*- coding: utf-8 -*-
"""
Created on Fri Aug 16 10:01:53 2024

@author: pkiefer
"""

import os
import pytest
import numpy as np
import emzed
from src.tadamz.in_out import load_targets_table

# from emzed import Table, MzType, RtType, mass, quantification
from emzed.ms_data.peak_map import Chromatogram, MSChromatogram
from src.tadamz import correct_isotopologue_overlays as cio

here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")
mztol_abs = 0.003
mztol_rel = 0
precursor_mztol = 0.1


class Model:
    def __init__(self, rts, ints, model_name):
        self.rts = rts
        self.ints = ints
        self.area = np.trapz(ints, rts)
        self.model_name = model_name

    def graph(self):
        return self.rts, self.ints


def gauss(x, area, mu, sigma):
    return (
        area
        / np.sqrt(2 * np.pi * sigma**2)
        * np.exp(-((x - mu) ** 2) / (2.0 * sigma**2))
    )


def generate_chromatogram(rtmin, rtmax, area, mu, sigma):
    rts = np.arange(rtmin, rtmax, 0.1)
    ints = gauss(rts, area, mu, sigma)
    return MSChromatogram(100, None, rts, ints, Chromatogram)


def generate_model(rtmin, rtmax, area, mu, sigma, model_name="linear"):
    rts = np.arange(rtmin, rtmax, 0.1)
    ints = gauss(rts, area, mu, sigma)
    return Model(rts, ints, model_name)


def combine_models(model1, model2):
    rts1, ints1 = model1.graph()
    rts2, ints2 = model2.graph()
    rtmin = np.min([rts1, rts2])
    rtmax = np.max([rts1, rts2])
    rts = np.arange(rtmin, rtmax, 0.1)
    ints = np.interp(rts, rts1, ints1, 0, 0) + np.interp(rts, rts2, ints2, 0, 0)
    ints = np.interp(rts1, rts, ints)
    return Model(rts1, ints, "linear")


def _comp(v1, v2):
    if v1 is None and v2 is None:
        return True
    try:
        return abs(v1 - v2) < 1e-10
    except:
        return False


@pytest.fixture
def result_table_ms1():
    fname = "test_overlapping_peaks_t_result_ms1.table"
    path = os.path.join(data_folder, fname)
    t = emzed.io.load_table(path)
    t.add_or_replace_column(
        "model_chromatogram",
        t.apply(generate_model, t.rtmin, t.rtmax, t.area_chromatogram, t.rt, 1.0),
        object,
    )

    return t


@pytest.fixture
def result_table_ms2():
    fname = "test_overlapping_peaks_t_result_ms2.table"
    path = os.path.join(data_folder, fname)
    t = emzed.io.load_table(path)
    return t


@pytest.fixture
def result_table_ms1ms2():
    fname = "test_overlapping_peaks_t_result_ms1ms2.table"
    path = os.path.join(data_folder, fname)
    t = emzed.io.load_table(path)
    t.add_or_replace_column(
        "model_chromatogram",
        t.apply(generate_model, t.rtmin, t.rtmax, t.area_chromatogram, t.rt, 1.0),
        object,
    )

    return t


@pytest.fixture
def t_iso_dist_ms1():
    path = os.path.join(data_folder, "isotop_dist_table_ms1.xlsx")
    return load_targets_table(path)


@pytest.fixture
def t_iso_dist_ms2():
    path = os.path.join(data_folder, "isotop_dist_table_ms2.xlsx")
    return load_targets_table(path)


@pytest.fixture
def kwargs_ms1():
    d = {
        "compound_col": "compound",
        "mf_col": "mf",
        "norm_group_col": "normalize_by_std_id",
        "std_group_col": "std_id",
        "adduct_col": "adduct",
        "filename_col": "filename",
        "mztol": 0.003,
        "precursor_mztol": 0.5,
    }
    return d


@pytest.fixture
def kwargs_ms2():
    d = {
        "compound_col": "compound",
        "mf_col": "mf",
        "norm_group_col": "normalize_by_std_id",
        "std_group_col": "std_id",
        "adduct_col": "adduct",
        "mf_fragment_col": "mf_fragment",
        "adduct_fragment_col": "adduct_fragment",
        "filename_col": "filename",
        "mztol": 0.003,
        "precursor_mztol": 0.1,
    }
    return d


def test_isotopologue_distribution_table_0(result_table_ms1, t_iso_dist_ms1):
    columns = ["compound", "mf", "adduct", None, None]
    cio._update_isotopologue_distribution_table(
        result_table_ms1,
        t_iso_dist_ms1,
        mztol_abs,
        mztol_rel,
        precursor_mztol,
        *columns
    )
    keys = [int(mz) for mz in t_iso_dist_ms1.mz]
    is_ = dict(zip(keys, t_iso_dist_ms1.id))
    expected = {810: 2, 811: 1, 181: 4, 187: 3}
    assert all([is_[key] == expected[key] for key in expected.keys()])


def test_isotopologue_distribution_table_1(result_table_ms2, t_iso_dist_ms2):
    columns = ["compound", "mf", "adduct", "mf_fragment", "adduct_fragment"]
    cio._update_isotopologue_distribution_table(
        result_table_ms2,
        t_iso_dist_ms2,
        mztol_abs,
        mztol_rel,
        precursor_mztol,
        *columns
    )
    keys = [int(mz) for mz in t_iso_dist_ms2.precursor_mz]
    # y =t_iso_dist_ms2.filter((t_iso_dist_ms2.std_id.is_not_none() | t_iso_dist_ms2.normalize_by_std_id.is_not_none()))
    is_ = dict(zip(keys, t_iso_dist_ms2.id))
    print(is_)
    expected = {371: 6, 373: 11, 572: 0, 574: 3}
    assert all([is_[key] == expected[key] for key in expected.keys()])


def test__group_features_0(result_table_ms1):
    cols = ["normalize_by_std_id", "mf", "adduct", None, None]
    is_ = cio._group_features(result_table_ms1, *cols)
    print(is_)
    expected = {
        2: [("C6H12O6", "M+H", None, None, 4)],
        1: [("C23H38N7O17P3S", "M+H", None, None, 2)],
        3: [("C12H22O11", "M+H", None, None, 6)],
    }
    assert all([is_[key] == expected[key] for key in expected.keys()])


def test__group_features_2(result_table_ms1):
    cols = ["std_id", "mf", "adduct", None, None]
    is_ = cio._group_features(result_table_ms1, *cols)
    expected = {
        2: [("[13]C6H12O6", "M+H", None, None, 3)],
        1: [("[13]CC22H38N7O17P3S", "M+H", None, None, 1)],
        3: [("[13]C6C6H22O11", "M+H", None, None, 5)],
    }
    assert all([is_[key] == expected[key] for key in expected.keys()])


def test__group_features_3(result_table_ms2):
    cols = ["normalize_by_std_id", "mf", "adduct", "mf_fragment", "adduct_fragment"]
    is_ = cio._group_features(result_table_ms2, *cols)
    # expected = {
    #     2: [("C6H12O6", "M+H", "C4H6O2", "M+H", 4)],
    #     1: [("C23H38N7O17P3S", "M+H", "C10H22N2O7", "M+H", 2)],
    #     3: [("C12H22O11", "M+H", "C6H12O6", "M+H", 6)],
    # }
    expected = {
        11: [("C28[13]C6H54N8O10", "M+2H", "C8[13]C6H24N4O7", "M+3H", 6)],
        3: [("C51H73N11O17S", "M+2H", "C34H51N7O15S", "M+3H", 0)],
    }
    print(is_)
    assert all([is_[key] == expected[key] for key in expected.keys()])


def test_get_std_correction_factor_dict_0(result_table_ms1, t_iso_dist_ms1):
    # ids and assigned (compound, type):
    # 1: (acetyl-coa, sample), 2:(acetyl-coa, std),
    # 3: (glucose, sample), 4: (glucose, std),
    # 5: (sucrose, sample), 6: (sucrose, std)
    cols = ["normalize_by_std_id", "mf", "adduct", None, None]
    id2sample_tuple = cio._group_features(result_table_ms1, *cols)
    cols[0] = "std_id"
    id2std_tuple = cio._group_features(result_table_ms1, *cols)
    is_ = cio.get_std_correction_factor_dict(
        id2sample_tuple, id2std_tuple, mztol_abs, mztol_rel, precursor_mztol
    )
    print(is_)
    # sample_id -> std_id -_> f_corr
    exp = {4: {3: 0}, 6: {5: 0}, 2: {1: 0.25972300260573855}}
    equals = []
    for key in exp.keys():
        equals.extend(
            [abs(is_[key][key2] - exp[key][key2]) < 1e-14 for key2 in exp[key].keys()]
        )
    assert all(equals)


def test_get_std_correction_factor_dict_1(result_table_ms2):
    # ids and assigned (compound, type):
    # 1: (acetyl-coa, sample), 2:(acetyl-coa, std),
    # 3: (glucose, sample), 4: (glucose, std),
    # 5: (sucrose, sample), 6: (sucrose, std)
    cols = ["normalize_by_std_id", "mf", "adduct", "mf_fragment", "adduct_fragment"]
    id2sample_tuple = cio._group_features(result_table_ms2, *cols)
    cols[0] = "std_id"
    id2std_tuple = cio._group_features(result_table_ms2, *cols)
    is_ = cio.get_std_correction_factor_dict(
        id2sample_tuple, id2std_tuple, mztol_abs, mztol_rel, precursor_mztol
    )
    print(id2sample_tuple, id2std_tuple)
    print(is_)

    exp = {0: {3: 0.011009755909565414}, 6: {11: 0.0}}
    equals = []
    for key in exp.keys():
        equals.extend(
            [abs(is_[key][key2] - exp[key][key2]) < 1e-14 for key2 in exp[key].keys()]
        )
    assert all(equals)


def test_get_sam_correctuion_factor_dict_0(result_table_ms1, t_iso_dist_ms1):
    cols = ["normalize_by_std_id", "mf", "adduct", None, None]
    cio._update_isotopologue_distribution_table(
        result_table_ms1,
        t_iso_dist_ms1,
        mztol_abs,
        mztol_rel,
        precursor_mztol,
        "compound",
        "mf",
        "adduct",
        None,
        None,
    )
    id2sample_tuple = cio._group_features(result_table_ms1, *cols)
    cols[0] = "std_id"
    id2std_tuple = cio._group_features(result_table_ms1, *cols)
    is_ = cio.get_sam_correction_factor_dict(
        id2sample_tuple,
        id2std_tuple,
        t_iso_dist_ms1,
        mztol_abs,
        mztol_rel,
        precursor_mztol,
    )
    print(is_)
    # std_id -> sample_id -> fcorr
    exp = {3: {4: 0.1}, 5: {6: 0}, 1: {2: 0.0}}
    equals = []
    for key in exp.keys():
        equals.extend(
            [abs(is_[key][key2] - exp[key][key2]) < 1e-14 for key2 in exp[key].keys()]
        )
    assert all(equals)


def test_get_sam_correction_factor_dict_1(result_table_ms2, t_iso_dist_ms2):
    cio._update_isotopologue_distribution_table(
        result_table_ms2,
        t_iso_dist_ms2,
        mztol_abs,
        mztol_rel,
        precursor_mztol,
        "compound",
        "mf",
        "adduct",
        "mf_fragment",
        "adduct_fragment",
    )
    cols = ["normalize_by_std_id", "mf", "adduct", "mf_fragment", "adduct_fragment"]
    id2sample_tuple = cio._group_features(result_table_ms2, *cols)
    cols[0] = "std_id"
    id2std_tuple = cio._group_features(result_table_ms2, *cols)
    is_ = cio.get_sam_correction_factor_dict(
        id2sample_tuple,
        id2std_tuple,
        t_iso_dist_ms2,
        mztol_abs,
        mztol_rel,
        precursor_mztol,
    )
    print(id2std_tuple, id2sample_tuple)
    print("############################")
    print(is_)
    # std_id -> sample_id -> fcorr
    exp = {3: {0: 0.1}, 11: {6: 0}}
    equals = []
    for key in exp.keys():
        equals.extend(
            [abs(is_[key][key2] - exp[key][key2]) < 1e-14 for key2 in exp[key].keys()]
        )
    assert all(equals)


def test__solve_overlapping_areas_0():
    # 1. full overlap
    models_is = [generate_model(40, 80, 1e5, 60, 1)]
    models_nl = [generate_model(40, 80, 1e5, 60, 1)]
    fs_is = [[0.1]]
    fs_nl = [[0.0]]
    areas_is, areas_nl = cio._solve_overlapping_areas(
        models_is, models_nl, fs_is, fs_nl
    )
    print(areas_is)
    assert abs(areas_is[0][0] - 0.9 * 1e5) < 1e-10
    # construct different overlapping cases


def test__solve_overlapping_areas_1():
    # 1. zero overlap
    models_is = [generate_model(40, 80, 1e5, 60, 1)]
    models_nl = [generate_model(100, 140, 1e5, 120, 1)]
    fs_is = [[0.1]]
    fs_nl = [[0.1]]
    areas_is, areas_nl = cio._solve_overlapping_areas(
        models_is, models_nl, fs_is, fs_nl
    )
    print(areas_is)
    assert abs(areas_is[0][0] - areas_nl[0][0]) < 1e-10


def test__solve_overlapping_areas_2():
    # construct different overlapping cases
    # 1. 50% overlap
    models_is = [generate_model(57, 63, 1e5, 60, 1)]
    model_over = generate_model(57, 63, 1e4, 60, 1)
    model_nl = generate_model(58, 64, 1e5, 61, 1)
    models_nl = [combine_models(model_nl, model_over)]
    print(models_nl[0].graph())
    print(models_nl[0].area)
    fs_is = [[0.0]]
    fs_nl = [[0.1]]
    areas_is, areas_nl = cio._solve_overlapping_areas(
        models_is, models_nl, fs_is, fs_nl
    )
    print(areas_nl)
    assert abs(areas_nl[0][0] - model_nl.area) / model_nl.area < 1e-4


def test__solve_overlapping_areas_3():
    # 1. full overlap
    models_is = [generate_model(40, 80, 1e5, 60, 1)]
    models_nl = [generate_model(40, 80, 1e5, 60, 1)]
    fs_is = [[0.0]]
    fs_nl = [[0.0]]
    areas_is, areas_nl = cio._solve_overlapping_areas(
        models_is, models_nl, fs_is, fs_nl
    )
    print(areas_is)
    assert abs(areas_is[0][0] - areas_nl[0][0]) < 1e-10
    # construct different overlapping cases


def test_isotopologue_overlays_0(result_table_ms1, t_iso_dist_ms1, kwargs_ms1):
    cio.correct_isotopologue_overlays(result_table_ms1, kwargs_ms1, t_iso_dist_ms1)
    id2fcorr = {1: 0.259723, 2: 0, 3: 0, 4: 0.1, 5: 0, 6: 0}
    id2area = dict(zip(result_table_ms1.id, result_table_ms1.area_chromatogram))
    exps = []
    for id_, area, area_corr in zip(
        result_table_ms1.id,
        result_table_ms1.original_area_chromatogram,
        result_table_ms1.area_chromatogram,
    ):
        ida = id_ - 1 if (id_ / 2) == int(id_ / 2) else id_ + 1
        delta_rel = abs(area - (id2area[ida] * id2fcorr[id_]) - area_corr) / area_corr
        exps.append(delta_rel < 1e-8)
    assert all(exps)


def test_isotopologue_overlays_1(result_table_ms1, t_iso_dist_ms1, kwargs_ms1):
    t = result_table_ms1
    t.replace_column(
        "area_chromatogram", (t.id == 3).then_else(None, t.area_chromatogram), float
    )
    t.replace_column(
        "model_chromatogram", (t.id == 3).then_else(None, t.model_chromatogram), object
    )
    cio.correct_isotopologue_overlays(result_table_ms1, kwargs_ms1, t_iso_dist_ms1)
    exp = {
        (1, "S1"): True,
        (2, "S1"): True,
        (3, "S1"): False,
        (4, "S1"): False,
        (5, "S1"): True,
        (6, "S1"): True,
        (1, "S2"): True,
        (2, "S2"): True,
        (3, "S2"): False,
        (4, "S2"): False,
        (5, "S2"): True,
        (6, "S2"): True,
    }
    is_ = dict(zip(zip(t.id, t.filename), t.isotopologue_overlay_correction))
    assert all([exp[key] == is_[key] for key in exp.keys()])


def test_isotopologue_overlays_2(result_table_ms1, kwargs_ms1):
    cio.correct_isotopologue_overlays(result_table_ms1, kwargs_ms1, None)
    id2fcorr = {1: 0.259723, 2: 0, 3: 0, 4: 0.0, 5: 0, 6: 0}
    id2area = dict(zip(result_table_ms1.id, result_table_ms1.area_chromatogram))
    exps = []
    for id_, area, area_corr in zip(
        result_table_ms1.id,
        result_table_ms1.original_area_chromatogram,
        result_table_ms1.area_chromatogram,
    ):
        ida = id_ - 1 if (id_ / 2) == int(id_ / 2) else id_ + 1
        delta_rel = abs(area - (id2area[ida] * id2fcorr[id_]) - area_corr) / area_corr
        print(delta_rel)
        exps.append(delta_rel < 1e-8)
    assert all(exps)


def test_isotopologue_overlays_3(result_table_ms2, t_iso_dist_ms2, kwargs_ms2):
    # sub = result_table_ms2.filter(result_table_ms2.filename=='210205_H3.mzML')
    cio.correct_isotopologue_overlays(result_table_ms2, kwargs_ms2, t_iso_dist_ms2)
    # we check wether all non corrected peaks remain unchanged
    sub = result_table_ms2.filter(result_table_ms2.id.is_in([0, 3]) == False)
    # for sub in result_table_ms2.split_by('filename'):
    exps = [
        abs(p[0] - p[1]) < 1e-10
        for p in zip(sub.area_chromatogram, sub.original_area_chromatogram)
    ]

    assert all(exps)


def test_isotopologue_overlays_4(result_table_ms2, t_iso_dist_ms2, kwargs_ms2):
    t = result_table_ms2.filter(result_table_ms2.id.is_in([0, 3]))
    t.replace_column(
        "area_chromatogram", (t.id == 3).then_else(None, t.area_chromatogram), float
    )
    t.replace_column(
        "model_chromatogram", (t.id == 3).then_else(None, t.model_chromatogram), object
    )
    # since 3 and 6 depend on each other we expect a false for both peaks
    assert set(t.isotopologue_overlay_correction).pop() == False


def test_isotopologue_overlays_5(result_table_ms2, t_iso_dist_ms2, kwargs_ms2):
    t = result_table_ms2.filter(result_table_ms2.id.is_in([0, 3, 6, 11]))
    cio.correct_isotopologue_overlays(t, kwargs_ms2, t_iso_dist_ms2)
    assert set(t.isotopologue_overlay_correction).pop()


def test_calc_propabilities_0():
    el2mono = cio._element_to_monoisotopic_mass_number()
    mf = "C6H12O6"
    mf_frag = "C6H12O6"
    is_ = cio._calc_propability(mf, mf_frag, el2mono)
    assert is_ == 1


def test_calc_propabilities_1():
    el2mono = cio._element_to_monoisotopic_mass_number()
    mf = "[13]CC5H12O6"
    mf_frag = "C3H6O3"
    is_ = cio._calc_propability(mf, mf_frag, el2mono)
    print(is_)
    assert is_ == 0.5


def test_calc_propabilities_2():
    el2mono = cio._element_to_monoisotopic_mass_number()
    mf = "[13]CC5H12O6"
    mf_frag = "[13]CC2H6O3"
    is_ = cio._calc_propability(mf, mf_frag, el2mono)
    print(is_)
    assert is_ == 0.25


def test_correct_isotopologue_overlays_0(result_table_ms1ms2, kwargs_ms2):
    t1 = result_table_ms1ms2.filter(result_table_ms1ms2.mf_fragment.is_none())
    cio.correct_isotopologue_overlays(t1, kwargs_ms2)
    # is2 = cio.correct_isotopologue_overlays(result_table_ms2, kwargs_ms2)
    cio.correct_isotopologue_overlays(result_table_ms1ms2, kwargs_ms2)
    is1 = t1
    is12 = result_table_ms1ms2
    comb = is12.join(
        is1,
        (
            (is12.compound == is1.compound)
            & (is12.mf == is1.mf)
            & is12.mf_fragment.is_none()
            & is1.mf_fragment.is_none()
            & (is1.filename == is12.filename)
        ),
    )
    comb.add_column(
        "delta_rel",
        (comb.area_chromatogram - comb.area_chromatogram__0) / comb.area_chromatogram,
        float,
    )
    comb.replace_column("delta_rel", comb.apply(abs, comb.delta_rel), float)
    is_ = np.array(comb.delta_rel.to_list())
    assert len(comb) == len(t1)
    assert np.all(is_ < 1e-14)


def test_correct_isotopologue_overlays_1(result_table_ms1ms2, kwargs_ms2):
    t2 = result_table_ms1ms2.filter(result_table_ms1ms2.mf_fragment.is_not_none())
    # we apply the processing twice to check for repeatability
    cio.correct_isotopologue_overlays(t2, kwargs_ms2)
    cio.correct_isotopologue_overlays(t2, kwargs_ms2)
    # is2 = cio.correct_isotopologue_overlays(result_table_ms2, kwargs_ms2)
    cio.correct_isotopologue_overlays(result_table_ms1ms2, kwargs_ms2)
    is1 = t2
    is12 = result_table_ms1ms2
    comb = is12.join(
        is1,
        (
            (is12.compound == is1.compound)
            & (is12.mf == is1.mf)
            & (is12.mf_fragment == is1.mf_fragment)
            & (is12.filename == is1.filename)
        ),
    )
    comb.add_column(
        "delta_rel",
        (comb.area_chromatogram - comb.area_chromatogram__0) / comb.area_chromatogram,
        float,
    )
    comb.replace_column("delta_rel", comb.apply(abs, comb.delta_rel), float)
    is_ = np.array(comb.delta_rel.to_list())
    assert len(comb) == len(t2)
    assert np.all(is_ < 1e-14)
