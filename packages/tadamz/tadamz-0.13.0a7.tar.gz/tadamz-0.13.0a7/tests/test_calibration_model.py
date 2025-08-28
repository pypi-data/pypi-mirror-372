# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 11:54:38 2024

@author: pkiefer
"""

import pytest
import numpy as np
from src.tadamz.calibration import calibration_model as cm


@pytest.fixture
def xvalues():
    return np.array([0.0, 5.0, 10.0, 50.0, 100.0])


@pytest.fixture
def ys_lin(xvalues):
    np.random.seed(0)
    mat = np.random.normal(0, 0.5, size=(5, 4))[-1]
    xs = xvalues.reshape(-1, 1) * np.ones((5, 4))
    return cm.linear(xs, 4.5, 0.1) + mat


@pytest.fixture
def ys_quad(xvalues):
    np.random.seed(0)
    xs = xvalues.reshape(-1, 1) * np.ones((5, 4))
    return cm.quadratic(xs, -0.001, 4.5, 0.1)


@pytest.fixture
def sample_names():
    rows = []
    for i in range(5):
        row = []
        for j in range(4):
            row.append("_".join(["S", str(i), str(j)]))
        rows.append(row)
    return np.array(rows, dtype=object)


def test_CalbrationModel_0(sample_names, xvalues, ys_lin):
    model = cm.CalibrationModel(
        sample_names, xvalues, ys_lin, "ala", "none", "uM", "linear"
    )
    is_ = model.__dict__
    expected = {
        "compound": "ala",
        "weights": np.array([1, 1, 1, 1, 1]),
        "xvalues": xvalues,
        "yvalues": ys_lin,
        "unit": "uM",
        "sample_names": sample_names,
        "included_samples": cm._initialize_samples(sample_names),
        "x_range": (0.0, 100.0),
        "y_range": (np.min(ys_lin), np.max(ys_lin)),
        "lod": 0.01909911669665972,
        "loq": 0.06366372232219908,
    }
    print(is_)
    for key in expected.keys():
        print(key)
        if isinstance(expected[key], np.ndarray):

            assert np.all(expected[key] == is_[key])
        else:
            current = is_[key]
            exp = expected[key]
            if isinstance(current, float):
                assert abs(exp - current) < 1e-10


def test_CalbrationModel_1(sample_names, xvalues, ys_lin):
    model = cm.CalibrationModel(
        sample_names, xvalues, ys_lin, "ala", "none", "uM", "linear"
    )
    model.model_name = "quadratic"
    model.fit_calibration_curve()
    model.determine_limits()
    assert model.inv_fun == cm.inv_quadratic


def test_CalbrationModel_2(sample_names, xvalues, ys_lin):
    model = cm.CalibrationModel(
        sample_names, xvalues, ys_lin, "ala", "none", "uM", "linear"
    )
    row = model.included_samples[0]
    new_row = [(el[0], False) for el in row]
    model.included_samples[0] = new_row
    model.fit_calibration_curve()
    model.determine_limits()
    print(model.included_samples)
    print(model.popt)
    assert model.x_range == (5.0, 100.0)


def test_CalbrationModel_3(sample_names, xvalues, ys_quad):
    model = cm.CalibrationModel(
        sample_names, xvalues, ys_quad, "ala", "none", "uM", "quadratic"
    )
    is_ = np.array([model.get_amount(v) for v in ys_quad[:, 0]])
    assert np.all(np.abs(is_ - xvalues) < 1e-10)


def test_CalbrationModel_4(sample_names, xvalues, ys_quad):
    model = cm.CalibrationModel(
        sample_names, xvalues, ys_quad, "ala", "none", "uM", "quadratic"
    )
    is_ = model.get_plotting_data()
    assert is_.xs.shape == is_.ys.shape, (
        is_.included_sample_data.shape == is_.sample_names.shape
    )


def test_CalbrationModel_5(sample_names, xvalues, ys_quad):
    model = cm.CalibrationModel(
        sample_names, xvalues, ys_quad, "ala", "1/x", "uM", "quadratic"
    )
    model.fit_calibration_curve()
    deltas = [abs(a - b) < 1e-10 for a, b in zip(xvalues, model.xvalues)]
    assert all(deltas)
