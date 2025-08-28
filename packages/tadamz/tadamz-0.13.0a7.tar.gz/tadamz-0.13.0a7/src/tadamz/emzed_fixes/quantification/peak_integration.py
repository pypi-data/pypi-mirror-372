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


import os
import sys
import tempfile
import time

from emzed.core.multiprocessing import multiprocessing

from .peak_shape_models import available_peak_shape_models

MIN_SIZE_DEFAULT = 100


def integrate(
    peak_table,
    peak_shape_model,
    ms_level=None,
    show_progress=True,
    n_cores=1,
    min_size_for_parallel_execution=MIN_SIZE_DEFAULT,
    post_fixes=None,
    max_cores=8,
    in_place=False,
    path=None,
    overwrite=False,
    **model_extra_args,
):
    """integrates peaks of peak_table.

    :param peak_table: :py:class:`emzed.Table` with required columns
                        ``id, mzmin, mzmax, rtmin, rtmax, peakmap``.
    :param peak_shape_model: String of model name applied to determine peak area.
                             Available models are: ``asym_gauss``, ``linear``,
                             ``no_integration``, ``sgolay``, ``emg``.
    :param ms_level: MS level of peak integration. Must only be specified if peakmap
                     has more than one MS levels. ``Default = None``.
    :param show_progress: Boolean value to activate progress bar. ``Default = True``.

    :param n_cores: Defines the number of cores used for multicore processing.
                    If ``n_cores`` exceeds the number of available cores  a
                    warning is displayed and.
                    ``Default = 1``.
    :param min_size_for_parallel_execution: Defines the number of table rows required
                    to execute multicore processing. ``Default = 100``.
    :param post_fixes: Defines a subset of peaks via postfixes i. e. ['__0', '__1'].
                        By default, all peak_tables of a table get integrated.
                        ``Default = None``.
    :param max_cores: The maximal number of cores used for multicore processing.
                      If ``max_cores`` exceeds the number of available cores
                      a warning is displayed and the ``n_cores`` is set to
                      ``max_cores``. Default is ``8``.
    :param in_place:  Allows operation in place if True.
                      Note: if ``in_place`` is ``True`` multicore processing
                      is not possible and n_cores is set to 1.
                      Default = ``False``.
                      Using in-place integration has performance benefits.
    :param path: If specified the result will be a Table with a db file backend,
             else the result will be managed in memory.
    :param overwrite: Indicate if an already existing database file should be
                  overwritten.
    :returns: :py:class:`emzed.Table` by default. Returns None if ``in_place`` is
              ``True``

    Example:

    For given peak_table t:

    .. parsed-literal::

        id   mzmin       mzmax       rtmin     rtmax
        int  float       float       RtType    RtType
        ---  ----------  ----------  --------  --------
        0  791.488450  791.498450    0.46 m    1.01 m
        1  741.464140  741.474140    0.50 m    0.76 m
        2  895.064630  895.074630    3.70 m    4.07 m

    .. code-block:: python

        t1=emzed.quantification.integrate(t, 'linear')

    .. parsed-literal::

        id   mzmin       mzmax       rtmin     rtmax     peak_shape_model  area      rmse      valid_model
        int  float       float       RtType    RtType    str               float     float     bool
        ---  ----------  ----------  --------  --------  ----------------  --------  --------  -----------
        0  791.488450  791.498450    0.46 m    1.01 m    linear            1.34e+07  0.00e+00         True
        1  741.464140  741.474140    0.50 m    0.76 m    linear            3.03e+06  0.00e+00         True
        2  895.064630  895.074630    3.70 m    4.07 m    linear            1.68e+06  0.00e+00         True

    """  # noqa: E501
    if peak_shape_model not in available_peak_shape_models:
        names = ", ".join(available_peak_shape_models)
        raise ValueError(f"given integrator {peak_shape_model} must be one of {names}")

    needed_columns = ["mzmin", "mzmax", "rtmin", "rtmax", "peakmap"]
    if post_fixes is None:
        post_fixes = peak_table.supported_postfixes(needed_columns)
        if not post_fixes:
            raise ValueError("given table is no peak table")
    else:
        missing = []
        for post_fix in post_fixes:
            for name in needed_columns:
                if name + post_fix not in peak_table.col_names:
                    missing.append(name + post_fix)
        if missing:
            raise ValueError("column name(s) {} missing".format(", ".join(missing)))

    messages, n_cores = check_num_cores(
        n_cores, len(peak_table), min_size_for_parallel_execution, max_cores, in_place
    )

    started = time.time()

    indices = range(len(peak_table))
    if n_cores == 1:
        result = _integrate(
            (
                peak_table,
                indices,
                post_fixes,
                peak_shape_model,
                ms_level,
                show_progress,
                model_extra_args,
                len(peak_table),
            )
        )
    else:
        temp_folder = tempfile.mkdtemp()
        args = []
        for i in range(n_cores):
            sub_table = peak_table[i::n_cores]
            sub_indices = indices[i::n_cores]
            _path = os.path.join(temp_folder, f"part_{i:03d}.table")
            sub_table = sub_table.consolidate(path=_path)
            show_progress = i == 0  # only first process prints progress status
            args.append(
                (
                    sub_table,
                    sub_indices,
                    post_fixes,
                    peak_shape_model,
                    ms_level,
                    show_progress,
                    model_extra_args,
                    len(peak_table),
                )
            )

        try:
            with multiprocessing.Pool(n_cores) as pool:
                results = pool.map(_integrate, args)
        finally:
            for p in os.listdir(temp_folder):
                try:
                    os.unlink(os.path.join(temp_folder, p))
                except IOError:
                    pass

        if results:
            result = results[0]
            for r in results[1:]:
                result.update(r)
        else:
            result = {}

    result_table = create_result_table(
        peak_table,
        indices,
        peak_shape_model,
        post_fixes,
        result,
        path,
        overwrite,
        in_place,
    )

    if show_progress:
        needed = time.time() - started
        minutes, seconds = divmod(needed, 60)
        if minutes:
            print("needed %d minutes and %.1f seconds" % (minutes, seconds))
        else:
            print("needed %.1f seconds" % seconds)

    return result_table


def _integrate(args):
    (
        peak_table,
        indices,
        postfixes,
        peak_shape_model,
        ms_level,
        show_progress,
        model_extra_args,
        n,
    ) = args

    lastcent = -1
    result = {}
    for postfix in postfixes:
        for index, row in zip(indices, peak_table):
            if show_progress:
                cent = int((index + 1) * 20 / n / len(postfixes))
                if cent != lastcent:
                    print(cent * 5, end=" ")
                    try:
                        if sys.stdout is not None:
                            sys.stdout.flush()
                    except OSError:
                        # migh t happen on win cmd console
                        pass
                    lastcent = cent
            rtmin = row["rtmin" + postfix]
            rtmax = row["rtmax" + postfix]
            mzmin = row["mzmin" + postfix]
            mzmax = row["mzmax" + postfix]
            peakmap = row["peakmap" + postfix]
            if (
                rtmin is None
                or rtmax is None
                or mzmin is None
                or mzmax is None
                or peakmap is None
            ):
                current_peak_shape_model = available_peak_shape_models["no_integration"]
            else:
                current_peak_shape_model = available_peak_shape_models[peak_shape_model]
            model = current_peak_shape_model.fit(
                peakmap, rtmin, rtmax, mzmin, mzmax, ms_level, **model_extra_args
            )

            result[index, postfix] = model
    return result


def check_num_cores(n_cores, table_size, min_table_size, max_cores, in_place):
    messages = []
    if multiprocessing.current_process().daemon and n_cores != 1:
        messages.append(
            "WARNING: you choose n_cores = %d but integrate already runs inside a "
            "daemon process which is not allowed. therefore set n_cores = 1" % n_cores
        )
        n_cores = 1

    if n_cores <= 0:
        messages.append(
            "WARNING: you requested to use %d cores, "
            "we use single core instead !" % n_cores
        )
        n_cores = 1

    n_cores = min(n_cores, max_cores)

    if n_cores > 1 and in_place:
        messages.append(
            "WARNING: you requested to use %d cores but you set in_place = True, "
            " which is not allowed and we set n_cores = 1" % n_cores
        )
        n_cores = 1

    if n_cores > 1 and table_size < min_table_size:
        messages.append(
            "INFO: as the table has les thann %d rows, we switch to one cpu mode"
            % min_table_size
        )
        n_cores = 1

    elif n_cores > multiprocessing.cpu_count():
        messages.append(
            "WARNING: more processes demanded than available cpu cores, this might be "
            "inefficient"
        )

    return messages, n_cores


def create_result_table(
    peak_table,
    indices,
    peak_shape_model,
    post_fixes,
    result,
    path,
    overwrite,
    in_place,
):
    result_table = (
        peak_table if in_place else peak_table.copy(path=path, overwrite=overwrite)
    )
    for post_fix in post_fixes:
        peak_shape_models = []
        areas = []
        rmses = []
        models = []
        is_valid = []

        for index, row in zip(indices, peak_table):
            model = result.get((index, post_fix))
            areas.append(model.area)
            rmses.append(model.rmse)
            models.append(model)
            is_valid.append(model.is_valid)
            peak_shape_models.append(model.model_name)

        result_table.add_or_replace_column("peak_shape_model", peak_shape_models, str)
        result_table.add_or_replace_column(
            "area" + post_fix, areas, float, format_="%.2e"
        )
        result_table.add_or_replace_column(
            "rmse" + post_fix, rmses, float, format_="%.2e"
        )
        result_table.add_or_replace_column(
            "model" + post_fix, models, object, format_=None
        )
        result_table.add_or_replace_column("valid_model" + post_fix, is_valid, bool)
    return None if in_place else result_table
