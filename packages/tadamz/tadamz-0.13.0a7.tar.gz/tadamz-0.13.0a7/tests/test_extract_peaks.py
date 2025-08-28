# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 08:58:37 2023

@author: pkiefer
"""

import os
import pytest
import emzed
from emzed import RtType, MzType, Table
from src.tadamz import extract_peaks as ep

here = os.path.abspath(os.path.dirname(__file__))


@pytest.fixture
def config_srm():
    config = {
        "integration_algorithm": "linear",
        "chromatogram_boundary_factor": 3.0,
        "precursor_column": "precursor_mz",
        "precursor_mz_tol": 0.5,
        "mz_tol_abs": 0.5,
        "mz_tol_rel": 0.0,
        "subtract_baseline": False,
        "ms_data_type": "MS_Chromatogram",
        "peak_width_col": None,
    }
    return config


@pytest.fixture
def config_prm():
    config = {
        "integration_algorithm": "linear",
        "chromatogram_boundary_factor": 3.0,
        "precursor_column": "precursor_mz",
        "precursor_mz_tol": 0.5,
        "mz_tol_abs": 0.005,
        "mz_tol_rel": 0.0,
        "ms_level": 2,
        "subtract_baseline": False,
        "ms_data_type": "Spectra",
        "peak_width_col": None,
    }
    return config


@pytest.fixture
def config_ms1():
    config = {
        "integration_algorithm": "linear",
        "chromatogram_boundary_factor": 3.0,
        "precursor_column": "pecursor_mz",
        "precursor_mz_tol": None,
        "mz_tol_abs": 0.005,
        "mz_tol_rel": 0.0,
        "subtract_baseline": False,
        "ms_data_type": "Spectra",
        "peak_width_col": None,
    }
    return config


@pytest.fixture
def config_sim():
    config = {
        "integration_algorithm": "linear",
        "chromatogram_boundary_factor": 3.0,
        "precursor_column": "pecursor_mz",
        "precursor_mz_tol": None,
        "mz_tol_abs": 0.5,
        "mz_tol_rel": 0.0,
        "subtract_baseline": False,
        "ms_data_type": "MS_Chromatogram",
        "peak_width_col": None,
    }
    return config


@pytest.fixture
def srm():
    path = os.path.join(here, "data/mrm_data_large.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def prm():
    path = os.path.join(here, "data/prm_data.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def ms1():
    path = os.path.join(here, "data/ms1_data.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def sim():
    path = os.path.join(here, "data", "sim_data.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def ms_prm():
    path = os.path.join(here, "data", "ms_prm_data.mzml")
    return emzed.io.load_peak_map(path)


@pytest.fixture
def pt_srm():
    columns = (
        "precursor_mz",
        "mz",
        "mzmin",
        "mzmax",
        "rt",
        "rtmin",
        "rtmax",
        "rt_max_shift",
    )
    types = [MzType, MzType, MzType, MzType, RtType, RtType, RtType, float]
    rows = [
        [
            372.212521,
            401.259831,
            401.159831,
            401.359831,
            165.77099609,
            161.84700012,
            173.19500732,
            5.0,
        ],
        [
            307.498975,
            404.198793,
            404.098793,
            404.298793,
            109.11599731,
            103.36699677,
            121.41999817,
            5.0,
        ],
        [
            408.550103,
            461.753824,
            461.653824,
            461.853824,
            133.89300537,
            129.4940033,
            141.41499329,
            5.0,
        ],
        [
            472.918238,
            552.286774,
            552.186774,
            552.386774,
            299.72198486,
            296.25799561,
            305.44900513,
            5.0,
        ],
    ]

    t = Table.create_table(columns, types, rows=rows)
    t.add_enumeration()
    return t


@pytest.fixture
def pt_sim():
    columns = (
        "precursor_mz",
        "mz",
        "rt",
        "rtmin",
        "rtmax",
        "rt_max_shift",
    )
    types = [MzType, MzType, RtType, RtType, RtType, float]
    rows = [
        [
            None,
            88.0404,
            174.0,
            150.0,
            192.0,
            5.0,
        ],
        [
            None,
            104.0355,
            205.8,
            198.0,
            219.0,
            5.0,
        ],
        [
            None,
            115.0023,
            282.0,
            277.8,
            285.0,
            5.0,
        ],
        [
            None,
            116.0717,
            112.8,
            108.0,
            117.6,
            5.0,
        ],
    ]
    t = Table.create_table(columns, types, rows=rows)
    t.add_enumeration()
    return t


@pytest.fixture
def pt_prm():
    columns = (
        "precursor_mz",
        "mz",
        "mzmin",
        "mzmax",
        "rt",
        "rtmin",
        "rtmax",
        "rt_max_shift",
    )
    types = [MzType, MzType, MzType, MzType, RtType, RtType, RtType, float]
    rows = [
        [
            146.0,
            102.05456351,
            102.05401611,
            102.05512238,
            269.702082,
            252.227826,
            287.866704,
            5.0,
        ],
        [
            215.0,
            89.0228633,
            89.02237701,
            89.02349091,
            83.833074,
            77.002614,
            89.731656,
            5.0,
        ],
        [
            146.0,
            128.03391296,
            128.03282166,
            128.03465271,
            270.865692,
            259.679022,
            287.866704,
            5.0,
        ],
        [
            215.0,
            179.05523453,
            179.05459595,
            179.05619812,
            83.522574,
            78.399984,
            88.645668,
            5.0,
        ],
    ]
    t = Table.create_table(columns, types, rows=rows)
    t.add_enumeration()
    return t


@pytest.fixture
def pt_ms1():
    columns = (
        "precursor_mz",
        "mz",
        "mzmin",
        "mzmax",
        "rt",
        "rtmin",
        "rtmax",
        "rt_max_shift",
    )
    types = [MzType, MzType, MzType, MzType, RtType, RtType, RtType, float]
    rows = [
        [None, 175.11895, 175.11495, 175.12295, 332.4, 330.0, 339.0, 5.0],
        [None, 148.06043, 148.0564, 148.0644, 296.4, 291.530574, 298.62465, 5.0],
        [None, 134.0448, 134.0408, 134.0488, 316.2, 312.287562, 323.322864, 5.0],
    ]
    t = Table.create_table(columns, types, rows=rows)
    t.add_enumeration()
    return t


@pytest.fixture
def pt_ms_prm():
    columns = (
        "precursor_mz",
        "mz",
        "rt",
        "rtmin",
        "rtmax",
        "rt_max_shift",
    )
    types = [MzType, MzType, RtType, RtType, RtType, float]
    rows = [
        [None, 90.05495569, 259.2, 255, 262.8, 10],
        [None, 94.06205569, 259.2, 255, 262.8, 10],
        [175.1189529, 70.065669, 336, 332.4, 339.6, 5],
    ]
    t = Table.create_table(columns, types, rows=rows)
    t.add_enumeration()
    return t


def test_add_sample_to_peaks_table_0(pt_srm, srm, config_srm, regtest):
    pt_srm = ep._update_postfixes(pt_srm, config_srm)
    t = ep.add_sample_to_peaks_table(pt_srm, srm, config_srm)
    # t.add_column("uid", t.apply(lambda v: v.unique_id, t.peakmap), str)
    print(t, file=regtest)


def test_add_sample_to_peaks_table_1(pt_srm, srm):
    # empty peaks table
    kwargs = {
        "precursor_column": "precursor_mz",
        "precursor_mz_tol": 0.5,
        "mz_tol_abs": 0.5,
        "mz_tol_rel": 0.0,
        "ms_level": 2,
        "ms_data_type": "MS_Chromatogram",
        "peak_width_col": None,
    }
    pt_srm = ep._update_postfixes(pt_srm, kwargs)
    pt = pt_srm[:0].consolidate()

    t = ep.add_sample_to_peaks_table(pt, srm, kwargs)
    assert len(t) == 0


def test_add_sample_to_peaks_table_2(pt_srm, srm, config_srm):
    pt_srm = ep._update_postfixes(pt_srm, config_srm)
    t = ep.add_sample_to_peaks_table(pt_srm, srm, config_srm)
    # t.add_column("uid", t.apply(lambda v: v.unique_id, t.peakmap), str)
    assert "peakmap" not in t.col_names
    # print(t, file=regtest)


def test_add_sample_to_peaks_table_3(pt_srm, srm, config_srm):
    pt_srm = ep._update_postfixes(pt_srm, config_srm)
    t = ep.add_sample_to_peaks_table(pt_srm, srm, config_srm)
    col2format = dict(zip(t.col_names, t.col_formats))
    assert col2format["acquisition_time"] is None
    assert t.acquisition_time.unique_value() == "0000-00-00 00:00:00"


def test_add_peakmap_from_spectra_0(pt_ms1, ms1):
    kwargs = {
        "chromatogram_boundary_factor": 3.0,
        "mz_tol_abs": 0.005,
        "mz_tol_rel": 0.0,
        "ms_level": 1,
        "ms_data_type": "Spectra",
    }
    t = ep.add_peakmap_from_spectra(pt_ms1, ms1, kwargs)
    print(t.col_names)
    assert "chromatogram" in t.col_names


def test_add_peakmap_from_spectra_1(pt_prm, prm):
    kwargs = {
        "chromatogram_boundary_factor": 3.0,
        "precursor_column": "precursor_mz",
        "precursor_mz_tol": 0.1,
        "mz_tol_abs": 0.005,
        "mz_tol_rel": 0.0,
        "ms_level": 2,
        "ms_data_type": "Spectra",
    }
    t = ep.add_peakmap_from_spectra(pt_prm, prm, kwargs)
    print(t.col_names)
    assert "chromatogram" in t.col_names


def test_add_sample_to_peaks_table_3(pt_prm, prm, regtest):
    kwargs = {
        "chromatogram_boundary_factor": 3.0,
        "precursor_column": "precursor_mz",
        "precursor_mz_tol": 0.1,
        "mz_tol_abs": 0.005,
        "mz_tol_rel": 0.0,
        "ms_level": 2,
        "ms_data_type": "Spectra",
    }
    t = ep.add_sample_to_peaks_table(pt_prm, prm, kwargs)
    print(t, file=regtest)


def test_add_sample_to_peaks_table_4(pt_ms1, ms1, regtest):
    kwargs = {
        "chromatogram_boundary_factor": 3.0,
        "mz_tol_abs": 0.005,
        "mz_tol_rel": 0.0,
        "ms_level": 1,
        "ms_data_type": "Spectra",
    }
    t = ep.add_sample_to_peaks_table(pt_ms1, ms1, kwargs)
    print(t, file=regtest)


def test_add_sample_to_peaks_table_5(pt_ms_prm, ms_prm, config_prm, regtest):
    t = ep.extract_peaks(pt_ms_prm, [ms_prm], config_prm)
    print(t, file=regtest)


def test_extract_peaks_srm_0(pt_srm, srm, config_srm, regtest):
    t = ep.extract_peaks(pt_srm, [srm], config_srm)
    print(t, file=regtest)


def test_extract_peaks_prm(pt_prm, prm, config_prm, regtest):
    t = ep.extract_peaks(pt_prm, [prm], config_prm)
    print(t, file=regtest)


def test_extract_peaks_ms1(pt_ms1, ms1, config_ms1, regtest):
    t = ep.extract_peaks(pt_ms1, [ms1], config_ms1)
    print(t, file=regtest)


def test_extract_peaks_ms1_0(pt_ms1, ms1, config_ms1):
    pt_ms1.drop_columns("precursor_mz")
    t = ep.extract_peaks(pt_ms1, [ms1], config_ms1)
    assert set(t.precursor_mz).pop() is None


def test_extract_peaks_sim(pt_sim, sim, config_sim, regtest):
    t = ep.extract_peaks(pt_sim, [sim], config_sim)
    print(t, file=regtest)


def test_extract_peaks_from_sample_path(pt_ms1, config_ms1, regtest):
    path = os.path.join(here, "data/ms1_data.mzml")
    t = ep.extract_peaks(pt_ms1, [path], config_ms1)
    print(t, file=regtest)


def test_extract_peaks_fall_back_integration_0(pt_ms1, config_ms1):
    config_ms1["integration_algorithm"] = "emg"
    path = os.path.join(here, "data/ms1_data.mzml")
    t = ep.extract_peaks(pt_ms1, [path], config_ms1)
    t.replace_column("valid_model_chromatogram", [True, False, True], bool)
    ep._fall_back_integration(t)
    is_ = dict(zip(t.id, t.peak_shape_model_chromatogram))
    print(is_)
    expected = {0: "emg", 1: "linear", 2: "emg"}
    assert all([is_[key] == expected[key] for key in expected.keys()])


def test_extract_peaks_fall_back_integration_1(pt_ms1, config_ms1):
    config_ms1["integration_algorithm"] = "emg"
    path = os.path.join(here, "data/ms1_data.mzml")
    t = ep.extract_peaks(pt_ms1, [path], config_ms1)
    t1 = t[2:].consolidate()
    emzed.quantification.integrate_chromatograms(t1, "no_integration", in_place=True)
    t = emzed.Table.stack_tables([t[:2].consolidate(), t1])
    t.replace_column("valid_model_chromatogram", [True, False, None], bool)
    ep._fall_back_integration(t)
    is_ = dict(zip(t.id, t.peak_shape_model_chromatogram))
    print(t)
    expected = {0: "emg", 1: "linear", 2: "no_integration"}
    assert all([is_[key] == expected[key] for key in expected.keys()])


def test__update_mz_range(pt_ms1, ms1, config_ms1):
    config_ms1["mz_tol_rel"] = 5
    rel_tol = 5 / 1e6
    ep._update_mz_range(pt_ms1, **config_ms1)
    expected = []
    for mz, mzmin, mzmax in zip(pt_ms1.mz, pt_ms1.mzmin, pt_ms1.mzmax):
        c1 = abs(mzmin - mz * (1 - rel_tol)) < 1e20
        c2 = abs(mzmax - mz * (1 + rel_tol)) < 1e20
        expected.append(c1 and c2)
    assert all(expected)


def test_mz_tolerance_set_0():
    with pytest.raises(AssertionError):
        ep._mz_tolerance_set()


def test_mz_tolerance_set_1():
    assert ep._mz_tolerance_set(0.1) is None


def test__update_postfixes(pt_srm, config_srm):
    config_srm["peak_width_col"] = "delta_rt"
    pt_srm.add_column(
        "delta_rt", pt_srm.rtmax - pt_srm.rtmin, RtType, insert_after="rt"
    )
    pt_srm.drop_columns("rtmin", "rtmax")
    t = ep._update_postfixes(pt_srm, config_srm)
    print(t)
    c1 = "rtmin_chromatogram" in t.col_names
    c2 = "rtmax_chromatogram" in t.col_names
    assert c1 and c2


def test_assign_peakmap_by_precursor(pt_prm, prm):
    # peak window does not completely overlap with eic
    pt = pt_prm[:1].consolidate()
    pt.replace_column_with_constant_value("rtmin", 251, RtType)
    t = ep.create_ms2_peakmap_table(prm)
    tt = ep.assign_peakmaps_by_precursor(pt, t, 0.5, 0.005, 0)
    is_ = tt.peakmap.unique_value()
    expected = prm.split_by_precursors()[(146.0459,)]
    assert is_.unique_id == expected.unique_id
