# -*- coding: utf-8 -*-
"""
Created on Tue Jul 18 12:27:21 2023

@author: pkiefer
"""
from .scoring.peak_metrics import update_metrics
from .in_out import load_classifier_object
from .in_out import save_classifier_data
from .scoring.random_forest_peak_classification import (
    create_classifier,
    score_peaks,
    _get_meta_data,
)


def classify_peaks(table, kwargs):
    _classify_peaks(table, **kwargs)
    return table


def _classify_peaks(table, scoring_model, scoring_model_params, **kwargs):
    fun = globals()[scoring_model]
    fun(table, **scoring_model_params)


def random_forest_classification(
    table,
    classifier_name,
    path_to_folder=None,
    min_spectra=6,
    ms_data_type="MS_Chromatogram",
    **kwargs,
):
    classifier = get_classifier(classifier_name, path_to_folder)
    # area_col = "area_chromatogram" if ms_data_type == "MS_Chromatogram" else "area"
    update_metrics(table, ms_data_type=ms_data_type)
    score_peaks(table, classifier, min_spectra)


def get_classifier(classifier_name, path_to_folder, **kwargs):
    clf = None
    try:
        clf = load_classifier_object(classifier_name, ".pickle", path_to_folder)

    except:
        pass

    try:
        meta_data = load_classifier_object(classifier_name, ".json", path_to_folder)
    except:
        meta_data = _get_meta_data()
    if not _evaluate_classifier_env(clf, classifier_name, meta_data):
        t_data = load_classifier_object(classifier_name, ".table", path_to_folder)
        print("(re)building peak classifier ...")
        clf, meta_data_, t_data = create_classifier(t_data)
        _compare_cross_validation_results(meta_data, meta_data_)
        save_classifier_data(
            clf, meta_data, t_data, classifier_name, path_to_folder, overwrite=True
        )
    return clf


def _evaluate_classifier_env(classifier, classifier_name, meta_data):
    current_meta_data = _get_meta_data()
    if classifier is None:
        msg = f""" 
        We could not load {classifier_name}. We try to rebuild the
        the classifier from the correspondning training data file ...
        """
        print(msg)
        return False
    for key in current_meta_data.keys():
        if not current_meta_data[key] == meta_data[key]:
            msg = f""" {key} version {meta_data[key]} used for building classifier 
            is not the same as currently installed verions {current_meta_data[key]}!
            We therefore rebuild the classifier from the corresponding training data file"""
            return False
    return True


def _compare_cross_validation_results(md_before, md_after):
    key = "cross_validation_score_mean"
    std_key = "cross_validation_score_std"
    if isinstance(md_before.get(key), float):
        delta_perc = (md_after[key] - md_before[key]) / md_before[key] * 100
        if delta_perc < -5:
            msg = f"""
            Please note, the new mean cross vaöidation score {md_after[key]} +- {md_after[std_key]}
            is {delta_perc:.1f} smaller than before ({md_before[key]} +- {md_before[std_key]})"""
            print(msg)
