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


import abc

import numpy as np


class PeakShapeModelBase(abc.ABC):
    @abc.abstractmethod
    def __init__(self, parameters): ...

    @abc.abstractproperty
    def is_valid(self): ...

    @property
    def model_name(self):
        # abstract class attribute
        raise NotImplementedError()

    @classmethod
    def fit(cls, peakmap, rtmin, rtmax, mzmin, mzmax, ms_level, **extra_args):
        rts, intensities = peakmap.chromatogram(mzmin, mzmax, rtmin, rtmax, ms_level)
        return cls._fit(rts, intensities, extra_args)

    @abc.abstractclassmethod
    def _fit(cls, rts, intensities, extra_args): ...

    @abc.abstractmethod
    def graph(self): ...

    @abc.abstractproperty
    def area(self): ...

    @abc.abstractproperty
    def rmse(self): ...

    @abc.abstractmethod
    def __getstate__(self): ...

    @abc.abstractmethod
    def __setstate__(self, data): ...

    def __eq__(self, other):
        return isinstance(other, self.__class__) and all(
            equal(getattr(self, name), getattr(other, name)) for name in self.__slots__
        )


def equal(a, b):
    if isinstance(a, np.ndarray):
        return isinstance(b, np.ndarray) and a.shape == b.shape and np.all(a == b)
    return a == b
