# This file is part of emzed (https://emzed.ethz.ch), a software toolbox for analysing
# LCMS data with Python.
#
# Copyright (C) 2020 ETH Zurich, SIS ID.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.


import warnings

import numpy as np
import scipy.optimize as opt
from numpy import trapz

from .base import PeakShapeModelBase

"""
based on https://doi.org/10.1093/chromsci/33.10.568
(pdf at https://watermark.silverchair.com/33-10-568.pdf as of jan 2020)

adapted formula from:
https://github.com/OpenMS/OpenMS/blob/master/\
        src/openms/source/TRANSFORMATIONS/FEATUREFINDER/EmgFitter1D.cpp#L61
"""

FAC1 = -2.4055 / np.sqrt(2)
SQRT2_PI = np.sqrt(2 * np.pi)


class SimplifiedEmgModel(PeakShapeModelBase):
    model_name = "emg"

    NPOINTS_INTEGRAL = 300
    NPOINTS_GRAPH = 300

    __slots__ = [
        "_height",
        "_center",
        "_width",
        "_symmetry",
        "_area",
        "_rmse",
        "_rtmin",
        "_rtmax",
    ]

    def __init__(self, parameters, area, rmse, rtmin, rtmax):
        self._height, self._center, self._width, self._symmetry = parameters
        self._area = area
        self._rmse = rmse
        self._rtmin = rtmin
        self._rtmax = rtmax

    def __getstate__(self):
        return (
            self._height,
            self._center,
            self._width,
            self._symmetry,
            self._area,
            self._rmse,
            self._rtmin,
            self._rtmax,
        )

    def __setstate__(self, data):
        (
            self._height,
            self._center,
            self._width,
            self._symmetry,
            self._area,
            self._rmse,
            self._rtmin,
            self._rtmax,
        ) = data

    @property
    def is_valid(self):
        return self._height is not None

    @property
    def area(self):
        return self._area

    @property
    def rmse(self):
        return self._rmse

    def graph(self):
        if self._height is None:
            return [], []
        rts = np.linspace(self._rtmin, self._rtmax, self.NPOINTS_GRAPH)
        intensities = self._apply(
            rts, self._height, self._center, self._width, self._symmetry
        )
        intensities[intensities < 0] = 0
        return rts, intensities

    def apply(self, rt_values):
        return self._apply(
            rt_values, self._height, self._center, self._width, self._symmetry
        )

    @staticmethod
    def _apply(rt_values, height, center, width, symmetry):
        rt_values = np.atleast_1d(rt_values)

        # avoid zero division
        if symmetry * symmetry == 0.0:
            symmetry = 1e-6

        inner = (
            width * width / 2.0 / symmetry / symmetry - (rt_values - center) / symmetry
        )

        # avoid overflow: may happen if _fun_eval is called with full rtrange and
        # symmetry is small:
        inner[inner > 200] = 200
        nominator = np.exp(inner)

        # avoid zero division
        if width == 0:
            width = 1e-6

        denominator = 1 + np.exp(
            FAC1 * ((rt_values - center) / width - width / symmetry)
        )

        return height * width / symmetry * SQRT2_PI * nominator / denominator

    @classmethod
    def _fit(cls, rts, intensities, extra_args):
        if len(rts) < 4:
            return cls((None,) * 4, None, None, None, None)

        imax = np.argmax(intensities)
        center_est = rts[imax]
        height_est = intensities[imax] * 2
        width_est = 0.2
        symmetry_est = 0.3

        start_parameters = (height_est, center_est, width_est, symmetry_est)

        def err(parameters, rts, intensities):
            return cls._apply(rts, *parameters) - intensities

        # relative error on parameters:
        xtol = extra_args.get("xtol", 1e-7)

        # error on gradient orthogonality:
        gtol = extra_args.get("gtol", 1e-12)

        (height, center, width, symmetry), _cov, _info_dict, msg, ierr = opt.leastsq(
            err,
            start_parameters,
            xtol=xtol,
            gtol=gtol,
            args=(rts, intensities),
            full_output=True,
        )

        if height < 0 or width < 0 or symmetry < 0 or center < -100 or ierr == 5:
            # optimizer did not converge
            return cls((None,) * 4, None, None, None, None)

        if ierr not in (1, 2, 3, 4):
            warnings.warn(msg)
            return cls((None,) * 4, None, None, None, None)

        rtmin, rtmax = cls._detect_eic_limits(
            height, center, width, symmetry, min(rts), max(rts)
        )

        rt_full = np.linspace(rtmin, rtmax, cls.NPOINTS_INTEGRAL)
        ii_full = cls._apply(rt_full, height, center, width, symmetry)
        area = trapz(ii_full, rt_full)

        ii_smoothed = cls._apply(rts, height, center, width, symmetry)
        rmse = np.sqrt(np.sum((ii_smoothed - intensities) ** 2) / len(rts))

        parameters = (height, center, width, symmetry)
        return cls(parameters, area, rmse, rtmin, rtmax)

    @classmethod
    def _detect_eic_limits(
        cls, height, center, width, symmetry, overall_rtmin, overall_rtmax
    ):
        rtmin = rtmax = center

        h0 = cls._apply(rtmin, height, center, width, symmetry)
        while rtmin > overall_rtmin - 100:
            rtmin -= 5
            h = cls._apply(rtmin, height, center, width, symmetry)
            if h > 2 * h0 or h < 0.01 * h0:
                break

        while rtmin < center:
            rtmin += 1
            h = cls._apply(rtmin, height, center, width, symmetry)
            if h > 0.01 * h0:
                rtmin -= 1
                break

        while rtmax < overall_rtmax + 100:
            rtmax += 5
            h = cls._apply(rtmax, height, center, width, symmetry)
            if h > 2 * h0 or h < 0.01 * h0:
                break

        while rtmax > center:
            rtmax -= 1
            h = cls._apply(rtmax, height, center, width, symmetry)
            if h > 0.01 * h0:
                rtmax += 1
                break

        return rtmin, rtmax
