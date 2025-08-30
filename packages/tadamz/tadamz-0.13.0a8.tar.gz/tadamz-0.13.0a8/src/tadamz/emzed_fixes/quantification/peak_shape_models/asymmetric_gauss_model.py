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
from numpy import trapz

from .base import PeakShapeModelBase

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    import scipy.optimize as opt


class AsymmetricGaussModel(PeakShapeModelBase):
    model_name = "asym_gauss"

    DEFAULT_OFFSET = 0.01

    NPOINTS_INTEGRAL = 200

    LIMITS_GRAPH = 1.5
    LIMITS_AREA = 2

    NPOINTS_GRAPH = 100

    __slots__ = ["_a", "_s1", "_s2", "_mu", "_area", "_rmse"]

    def __init__(self, parameters, area, rmse):
        self._a, self._s1, self._s2, self._mu = parameters
        self._area = area
        self._rmse = rmse

    def __getstate__(self):
        return (self._a, self._s1, self._s2, self._mu, self._area, self._rmse)

    def __setstate__(self, data):
        self._a, self._s1, self._s2, self._mu, self._area, self._rmse = data

    @property
    def is_valid(self):
        return self._a is not None

    @property
    def area(self):
        return self._area

    @property
    def rmse(self):
        return self._rmse

    def graph(self):
        if self._a is None:
            return [], []
        rts = np.linspace(
            self._mu - self.LIMITS_GRAPH * self._s1,
            self._mu + self.LIMITS_GRAPH * self._s1,
            self.NPOINTS_GRAPH,
        )
        intensities = self._apply(rts, self._a, self._s1, self._s2, self._mu)
        return rts, intensities

    @staticmethod
    def _apply(rt_values, a, s1, s2, mu):
        is_left = rt_values < mu
        s = s2 + is_left * (s1 - s2)
        return a * np.exp(-((rt_values - mu) ** 2) / s)

    @classmethod
    def _fit(cls, rts, intensities, extra_args):
        assert len(rts) == len(intensities)

        a_est = np.max(intensities)
        mu_est = rts[intensities == a_est][0]

        """
        ii = a * np.exp(-(ri - mu) ** 2 / s)
        s * (log ii / a) = - (ri - mu) ** 2
        """

        i1 = (rts <= mu_est) * (intensities > 0)
        i2 = (rts >= mu_est) * (intensities > 0)

        if np.sum(i1) <= 3 or np.sum(i2) <= 3:
            return cls((None,) * 4, None, None)

        offset = extra_args.get("offset", cls.DEFAULT_OFFSET)

        s1_est = -np.median(
            (rts[i1] - mu_est) ** 2 / np.log(offset + (intensities[i1] / a_est))
        )
        s2_est = -np.median(
            (rts[i2] - mu_est) ** 2 / np.log(offset + (intensities[i2] / a_est))
        )

        s1_est = max(s1_est, 0.5)
        s2_est = max(s2_est, 0.5)

        start_parameters = (a_est, s1_est, s2_est, mu_est)

        def err(parameters, rts, intensities):
            return cls._apply(rts, *parameters) - intensities

        gtol = extra_args.get("gtol", 0.0)

        (a, s1, s2, mu), _cov, _info_dict, msg, ierr = opt.leastsq(
            err, start_parameters, gtol=gtol, args=(rts, intensities), full_output=True
        )

        if ierr not in (1, 2, 3, 4):
            return cls((None,) * 4, None, None)

        # we use trapez to evaluate area on +/- LIMITS_AREA
        rt_full = np.linspace(
            mu - cls.LIMITS_AREA * s1, mu + cls.LIMITS_AREA * s2, cls.NPOINTS_INTEGRAL
        )
        ii_full = cls._apply(rt_full, a, s1, s2, mu)
        ii_smoothed = cls._apply(rts, a, s1, s2, mu)

        area = trapz(ii_full, rt_full)
        rmse = np.sqrt(np.sum((ii_smoothed - intensities) ** 2) / len(rts))

        parameters = (a, s1, s2, mu)
        return cls(parameters, area, rmse)
