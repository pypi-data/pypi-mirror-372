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

from numpy import sqrt, trapz

from .base import PeakShapeModelBase

with warnings.catch_warnings():
    warnings.filterwarnings("ignore")
    from scipy.signal import savgol_filter


class SavGolModel(PeakShapeModelBase):
    model_name = "sgolay"

    __slots__ = [
        "_rts",
        "_intensities_smoothed",
        "_area",
        "_rmse",
    ]

    def __init__(self, rts, intensities_smoothed, area, rmse):
        self._rts = rts
        self._intensities_smoothed = intensities_smoothed
        self._area = area
        self._rmse = rmse

    def __getstate__(self):
        return (
            self._rts,
            self._intensities_smoothed,
            self._area,
            self._rmse,
        )

    def __setstate__(self, data):
        (
            self._rts,
            self._intensities_smoothed,
            self._area,
            self._rmse,
        ) = data

    @property
    def is_valid(self):
        return True

    @classmethod
    def _fit(cls, rts, intensities, extra_args):
        window_size = extra_args.get("window_size", 11)
        order = extra_args.get("window_size", 2)
        smoothed = savgol_filter(intensities, window_size, order, mode="constant")
        area = trapz(smoothed, rts)
        rmse = sqrt(sum((smoothed - intensities) ** 2) / len(rts))
        return cls(rts, smoothed, area, rmse)

    def graph(self):
        return (self._rts, self._intensities_smoothed)

    @property
    def area(self):
        return self._area

    @property
    def rmse(self):
        return self._rmse
