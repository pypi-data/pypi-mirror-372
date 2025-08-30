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


from numpy import trapz

from .base import PeakShapeModelBase


class LinearInterpolationModel(PeakShapeModelBase):
    model_name = "linear"

    __slots__ = ["_rts", "_intensities"]

    def __init__(self, rts, intensities):
        self._rts = rts
        self._intensities = intensities
        self._area = trapz(self._intensities, self._rts)

    def __getstate__(self):
        return (self._rts, self._intensities, self._area)

    def __setstate__(self, data):
        self._rts, self._intensities, self._area = data

    @property
    def is_valid(self):
        return True

    @classmethod
    def _fit(cls, rts, intensities, extra_args):
        assert not extra_args, f"{cls}.fit does not support extra args"
        return cls(rts, intensities)

    def graph(self):
        return (self._rts, self._intensities)

    @property
    def area(self):
        return self._area

    @property
    def rmse(self):
        return 0.0
