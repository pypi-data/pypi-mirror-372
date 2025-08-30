# -*- coding: utf-8 -*-
"""
Created on Wed Oct 30 13:52:19 2024

@author: pkiefer
"""
import numpy as np
import pylab
from scipy.stats import t as t_dist
from uncertainties import ufloat, unumpy
from operator import mul
import inspect
from collections import namedtuple

# from statsmodels.stats.weightstats import DescrStatsW


class CalibrationModel:

    def __init__(
        self,
        sample_names,
        xvalues,
        yvalues,
        compound,
        calibration_weight,
        unit,
        model_name,
        alpha_lodq=0.00135,
        **kwargs
    ):

        self.model_name = model_name
        self.params = []
        # None
        self.popt = None
        self.alpha_lodq = alpha_lodq
        # self.params = _create_params(popt, perr)
        self.sample_names = sample_names
        self.included_samples = _initialize_samples(sample_names)
        self.compound = compound
        self.xvalues = xvalues
        self.yvalues = yvalues
        self.calibration_weight = calibration_weight
        self.lod = None
        self.loq = None
        self.x_range = (None, None)
        self.y_range = (None, None)
        self.unit = unit
        self.fit_calibration_curve()
        self.determine_limits()

    def fit_calibration_curve(self):
        self.fun, self.inv_fun = _get_fitting_functions(self.model_name)
        self.weights = get_weights(self.xvalues, self.yvalues, self.calibration_weight)
        degree = 1 if self.model_name == "linear" else 2
        self.popt = [None] * (degree + 1)
        self.perr = [None] * (degree + 1)
        if _not_empty(self.xvalues) and _not_empty(self.yvalues):
            xs_, ys_, ws_ = _select_values(
                self.included_samples, self.xvalues, self.yvalues, self.weights
            )
            ys = linearize_data_mat(ys_)
            xs = expand_vector_by_replicates(xs_, ys_)
            ws = expand_vector_by_replicates(ws_, ys_)
            self.x_range = (np.nanmin(xs), np.nanmax(xs)) if len(xs) else (None, None)
            self.y_range = (
                (np.nanmin(ys), np.nanmax(ys)) if all(ys.shape) else (None, None)
            )
            # polyfit can only handle finite values all data points with nan or inf
            # will be ignored for the fitting
            idxs = np.isfinite(xs) & np.isfinite(ys) & np.isfinite(ws)
            # we apply try /  except to handle cases where no fitting is possible
            # e.g. not enough or no values
            try:
                self.popt, pcov = np.polyfit(
                    xs[idxs], ys[idxs], degree, w=ws[idxs], cov=True
                )
                self.perr = np.sqrt(np.diag(pcov))
            except:
                pass
        self.params = _create_params(self.popt, self.perr)

    def determine_limits(self):
        _check_params(self.popt)
        if _not_empty(self.xvalues) and _not_empty(self.yvalues):
            xs, ys, ws = _select_values(
                self.included_samples, self.xvalues, self.yvalues, self.weights
            )
            self.lod = determine_LOX(
                self.fun, self.inv_fun, self.popt, xs, ys, ws, 1, self.alpha_lodq
            )
            self.loq = determine_LOX(
                self.fun, self.inv_fun, self.popt, xs, ys, ws, 10 / 3, self.alpha_lodq
            )

    def get_amount(self, value):
        return self.inv_fun(value, *self.params)

    def plot_fitting(self):
        xs_, ys_, _ = _select_values(
            self.included_samples, self.xvalues, self.yvalues, self.weights
        )
        xvalues = xs_[~np.isnan(xs_)]
        fix, ax = pylab.subplots(1, figsize=(5, 5))
        y_fit = [v for v in self.fun(xvalues, *self.popt)]

        ax.plot(xvalues, y_fit)
        _, n = self.yvalues.shape
        for i in range(n):
            yvalues = ys_[:, i][~np.isnan(xs_)]
            ax.plot(xvalues, yvalues, "*")
        ax.set_xlabel(self.unit)
        ax.set_ylabel("response")
        ax.set_title(self.compound)

    def get_plotting_data(self):
        """
        reshapes plotting data for simplified plotting

        Returns
        -------
        1-d arrays of xvalues, yvalues, sample names, and included_samples as namedtuple object

        """
        Plotting = namedtuple(
            "Plotting_data", ["xs", "ys", "sample_names", "included_data_points"]
        )
        r, c = self.yvalues.shape
        xs = np.array(list(self.xvalues) * c)
        ys = self.yvalues.flatten()
        included = np.array(self.included_samples)[:, :, 1].flatten()
        sample_names = np.array(self.included_samples)[:, :, 0].flatten()
        return Plotting(xs, ys, sample_names, included)


def _check_params(popt):
    if popt is None:
        msg = "You have to run method `fit_calibration_curve()` prior `to detect_limits()`!"
        assert False, msg


def _not_empty(mat):
    return np.all(mat.shape)


def determine_LOX(model, inv_model, popt, xs, ys, ws, fac=1, alpha=0.00135):
    # BAUASTELLE zero value required!
    """

    Upper limit approach
    Source: IUPAC, Pure and applied chemistry 1997 (69), p. 309
    determine LOD and LOQ

    Parameters
    ----------
    model: object.
        calibration curve model signal = f(amount)
    inv_model : object
        inverse calibration curve model amount = f(signal).
    params : TYPE
        DESCRIPTION.
    xs : array like of shape m
        standars amounts.
    ys : array like of shape m, n
        Signal responses. rows: response level, n: replicate
    ws : arrray like of shape m
        weight vector.
    f : int
        limit factor. f=1 for LOD and f=3 for LOQ
    alpha : float, optional
        Determiens t stats upper confidence limit 1-alpha. The default is 0.01.

    Returns
    -------
    float
        Limits in amount domain.

    """
    yd = None
    if np.any(np.array(popt)):
        yd = yl_from_curve(model, popt, xs, ys, ws, fac, alpha)
    return inv_model(yd, *popt)


def yl_from_curve(model, params, xs, ys, ws, fac, alpha):
    """
    determines LOD from calibration curve UIPAC ULAC method, ecquation (28)

    Parameters
    ----------
    xs : TYPE
        DESCRIPTION.
    ys : TYPE
        DESCRIPTION.
    alpha : TYPE, optional
        DESCRIPTION. The default is 0.01.

    Returns
    -------
    float
        limt value in the signal domain.

    """
    m, n = ys.shape
    nub = n * m - len(params) + 1
    # ybm corresponds to the intercept of the fitting  curve
    ybm = params[-1]
    s2xx = calc_s2xx(xs, ys)
    syxw = calc_syxw(model, params, xs, ys, ws)
    kd = t_dist.ppf(1 - alpha, nub) * (1 + 1 / (m * n) + s2xx) ** 0.5
    return ybm + kd * fac * syxw


def calc_s2xx(xs, ys):
    xs_ = mn_shape_m_vector(xs, ys)
    xm = np.nanmean(xs_)
    return xm**2 / np.sum((xs_ - xm) ** 2)


def calc_syxw(model, params, xs, ys, ws):
    """
    determines weighted std

    Parameters
    ----------
    model: object,
        calibration curve model
    params: tuple,
        calibration model fitting parameters
    xs : array like of shape m
        standars amounts.
    ys : array like of shape m,n
        Signal responses. rows response leve, n replicate
    ws : arrray like of shape m
        weight vector.

    Returns
    -------
    float
        weighted standard deviation.

    """
    # note we have to use 1/s weighting for polyfit and
    # 1/s^2 for the calculation of syxw. hence
    # ws = mn_shape_m_vector(ws, ys)**2
    xs = mn_shape_m_vector(xs, ys)
    yiw_mat = model(xs, *params)
    residuals = ys - yiw_mat
    residuals = linearize_data_mat(residuals)
    ws = mn_shape_m_vector(ws, ys)
    # ws = expand_vector_by_replicates(ws, ys)
    variance = np.sum(ws * (ys - yiw_mat) ** 2) / np.sum(ws)
    return np.sqrt(variance) / (mul(*ys.shape) - len(params))


# helper funs
def _get_fitting_functions(model_name):
    name2fun = {
        linear.__name__: linear,
        inv_linear.__name__: inv_linear,
        quadratic.__name__: quadratic,
        inv_quadratic.__name__: inv_quadratic,
    }
    fun = name2fun[model_name]
    inv_fun = name2fun["inv_" + model_name]
    return fun, inv_fun


def _select_values(selected_samples, x_values, y_values, weights):
    excluded = _selected_as_array(selected_samples)
    excluded_ = np.all(excluded, axis=1)
    sel_y = y_values.copy()
    sel_x = x_values.copy()
    sel_w = weights.copy()
    sel_y[excluded] = np.nan
    sel_x[excluded_] = np.nan
    sel_w[excluded_] = np.nan
    return sel_x, sel_y, sel_w


def _selected_as_array(selected_samples):
    selected = []
    for rep in selected_samples:
        selected.append([s[-1] == False for s in rep])
    return np.array(selected)


# calibration models
def linear(x, a, b):
    x = np.nan if x is None else x
    if _not_none((a, b)):
        return a * x + b


def inv_linear(y, a, b):
    y = np.nan if y is None else y
    if _not_none((a, b)) and a != 0:
        return (y - b) / a


def quadratic(x, a, b, c):
    x = np.nan if x is None else x
    if _not_none((a, b, c)):
        return a * x**2 + b * x + c


def inv_quadratic(y, a, b, c):
    y = np.nan if y is None else y
    if _not_none((a, b, c)) and a != 0:
        if a != 0:
            return 0.5 * (-b + unumpy.sqrt(b**2 - 4 * a * c + 4 * a * y)) / a
            # we expect the solution (amount) to be >=0
            # we exclusde the second analytical solution
        # sol2 = 0.5 *(-1* np.sqrt(-4 * a * c  + 4 * a * x + b**2) -b) / a
        # linear model
        if b != 0:
            return (y - c) / b
        return c


def _not_none(params):
    # case 1 params contains None values
    if any([p is None for p in params]):
        return False
    # case 2. params contains only ufloats
    return np.all(~unumpy.isnan(params))


def get_weights(amounts, values, weights, **kwargs):
    # zero value weight is not defined

    if weights == "1/x":
        # we weight the data point by 10x the minimal vector weight
        weights = amounts.copy()
        weights[weights == 0] = min(weights[weights > 0]) / 10
        return 1 / weights
    if weights == "1/x^2":
        return 1 / amounts**2
    if weights == "1/s^2":
        # polyfit: ``w[i] = 1/sigma(y[i])``
        # we use noew measured sigmas directly and do not fit!
        sigmas = _get_sigmas(values)
        # sigmas  = np.nanstd(values, axis=1)
        # # we weight the data point by 10x the minimal vector weight
        # sigmas[sigmas == 0] = min(sigmas[sigmas > 0]) / 10
        return 1 / sigmas
    if weights == "none":
        return np.ones(len(amounts))
    assert False


def _initialize_samples(sample_names):
    # includes = namedtuple('included_samples', ['sample_name', 'is_included'])
    r, c = sample_names.shape
    included = []
    for i in range(r):
        included.append([(sn, True) for sn in sample_names[i, :]])
    return included


def _create_params(popt, perr):
    pairs = zip(np.array(popt, dtype=float), np.array(perr, dtype=float))
    return [ufloat(*pair) for pair in pairs]


def _get_sigmas(values):
    # we check for measurement replicates with only nans
    # import pdb; pdb.set_trace()
    nan_cols = np.all(np.isnan(values), axis=1)
    pos = np.argwhere(nan_cols)
    for i in pos:
        values[i, :] = 0
    sigmas = np.nanstd(values, axis=1)
    try:
        sigmas[sigmas == 0] = np.min(sigmas[sigmas > 0]) / 10
    except:
        sigmas = np.array([1] * len(nan_cols))
    return sigmas


# __________ shape data __________


def linearize_data_mat(ys):
    """
    converts m x n matrix to vector of length m*n
    values are added along m axis
    """
    return ys.T.reshape(mul(*ys.shape))


def expand_vector_by_replicates(vs, mat):
    m, n = mat.shape
    assert m == len(vs)
    return np.hstack([vs] * n)


def mn_shape_m_vector(vs, ys):
    """
    brings vector of length m to shape of signal response matrix

    Parameters
    ----------
    ys : 2d array
        m x n signal response matrics with m reponses and n replicates.
    ws : 1-d array like
        vector of length m

    Returns
    -------
    None.

    """
    m, n = ys.shape
    assert len(vs.shape) == 1
    assert len(vs) == m
    return vs.reshape(-1, 1) * np.ones(ys.shape)


# ------ helper fun ------------------


def convert_model(old_model):
    om = old_model
    sample_names = np.zeros(om.yvalues.shape, dtype=str)
    model = CalibrationModel(
        sample_names, om.xvalues, om.yvalues, om.compound, "1/x", om.unit, om.model_name
    )
    model.fit_calibration_curve()
    model.determine_limits()
    return model


def model_to_dict(model):
    keys = [
        key
        for key in inspect.signature(model.__init__).parameters.keys()
        if key != "kwargs"
    ]
    return {key: model.__dict__[key] for key in keys}


def dict_to_model(model_dict):
    return CalibrationModel(**model_dict)
