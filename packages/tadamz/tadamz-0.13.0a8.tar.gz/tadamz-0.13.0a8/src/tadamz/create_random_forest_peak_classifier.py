# -*- coding: utf-8 -*-
"""
Created on Mon Dec  4 13:40:32 2023

@author: pkiefer
"""
# import emzed_webgui
import emzed, os
from emzed.utils import busy_indicator
from .in_out import save_classifier_data
from .scoring import peak_metrics
from .scoring.random_forest_peak_classification import create_classifier


def generate_peak_classifier(
    classifier_name,
    min_spectra=5,
    max_depth=3,
    inspect=True,
    path_to_folder=None,
    ext=".pickle",
    path_to_table=None,
    table=None,
    ms_data_type="MS_Chromatogram",
    ms_level=None,
    score_col="peak_quality_score",
    overwrite=False,
):
    """
    Generates a peaks classifier from peaks table and saves it to `path_to_folder`.

    Parameters
    ----------
    classifier_name : str
        THe name of the classifier file
    min_spectra : int, optional
        The minimal number of peak intensity values > 0. All peaks with less
        than min_spectra will be excluded. The default is 5.
    max_depth : int, optional
        The depth of the Random Forest tree. The default is 3.
    inspect: bool, optional,
        If True, Table explorer opens table to manualy score peak quality.
        The default is True.
    path_to_folder : string, optional
        path to the folder with resulting classifier name. If None, it will be
        saved to the default data folder and can be accessed for scoring by
        setting path_to_folder to None. The default is None.
    ext : string, optional
        File extension of classifier file. The default is ".predict".
    path_to_table : str, optional
        path to the table with measured peaks. If None you have to provide
        the table. The default is None.
    table : Table, optional
        Table with measured peaks Peaks can be from MS Chromnatograms or from
        spectra. If Non, you have to provide a path to to a table.
        The default is None.
    ms_data_type: str, optional
        MS data type can be `MS_Chromatogram` or `Spectra`. The Default is
        `Spectra`.
    score_col : str, optional
        Name of column containing peak quality score. The default is
        `peak_quality_score`.
    overwrite : bool, optional
        If `True` existing file will be overwritten. The default is False.

    Returns
    -------
    None.

    """
    t = _get_table(path_to_table, table)
    _update_score_column(t, score_col)
    model_col, area_col = update_area(t, ms_data_type, ms_level)
    with busy_indicator("calculating peak metrics ..."):
        peak_metrics.update_metrics(t, ms_data_type=ms_data_type)
    t = t.filter(t.no_spectra >= min_spectra)
    if inspect:
        _score_peaks(t, score_col)
    msg = f"saving peaks_table with peak metrics to {path_to_folder} ..."
    print(msg)
    path = os.path.join(path_to_folder, classifier_name)
    emzed.io.save_table(t, path, overwrite=overwrite)
    with busy_indicator("generating classifier ..."):
        clf, meta_data, t_data = create_classifier(t, max_depth, score_col, area_col)
    msg = "saving classifier  ..."
    print(msg)
    save_classifier_data(
        clf, meta_data, t_data, classifier_name, path_to_folder, overwrite
    )


def _get_table(path, table):
    if path and not table:
        return emzed.io.load_table(path)
    if table and not path:
        msg = f"table must be of type Table and not of type {type(table)}!"
        assert isinstance(table, emzed.Table), msg
        return table
    if all([path, table]):
        msg = """Exactly 1 of the 2 function arguments `table` and `path_to_table` 
        must not be None. Both parameters are not None!"""
        assert False, msg
    msg = """Exactly 1 of the 2 function arguments `table` and `path_to_table` 
    must not be None. Both parameters are None!"""

    assert False, msg


def update_area(t, ms_data_type, ms_level):
    msg = f"`ms_data_type` must be `MS_Chromatogram` or `Spectra`and not {ms_data_type}"
    assert ms_data_type in ["MS_Chromatogram", "Spectra"], msg
    if ms_data_type == "Spectra":
        emzed.quantification.integrate(t, "linear", in_place=True, ms_level=ms_level)
        model_col = "model"
        area_col = "area"
    else:
        emzed.quantification.integrate_chromatograms(
            t, "linear", in_place=True, ms_level=ms_level
        )
        model_col = "model_chromatogram"
        area_col = "area_chromatogram"
    return model_col, area_col


def _score_peaks(t, score_col):
    msg = f"""Please evaluate peaks manualy. You can assign values from 0 to 2
    to {score_col}
    """
    print(msg)
    emzed.gui.inspect(t)


def _update_score_column(t, score_col):
    if score_col in t.col_names:
        return
    ins_col = t.col_names[0]
    t.add_column_with_constant_value(score_col, 0, int, insert_before=ins_col)
