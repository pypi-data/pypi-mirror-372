# -*- coding: utf-8 -*-
"""
Created on Fri Jun 30 11:14:21 2023

@author: pkiefer
"""
from .extract_peaks import extract_peaks
from .coeluting_peaks import coeluting_peaks
from .correct_isotopologue_overlays import correct_isotopologue_overlays
from .normalize_peaks import normalize_peaks
from .classify_peaks import classify_peaks
from .check_qualifier_peaks import check_qualifier_peaks
from .update_sample_information import update_sample_information
from .std_free_normalization import tic_normalize_peaks
from .std_free_normalization import pq_normalize_peaks
from .quantify import quantify
from .calibration.calibrate import calibrate
from .track_changes import extract_track_changes
from emzed import Table

# from collections import defaultdict


class ProcessingSteps:
    @classmethod
    def create_peaks_table(self, info_table, ms_data_type, table_type="IDMS"):
        pass

    @staticmethod
    def calibrate(result_table, calibration_table, sample_table, config):
        key = calibrate.__name__
        return calibrate(result_table, calibration_table, sample_table, config[key])

    def __init__(
        self,
        peaks_table,
        samples,
        config,
        calibration_table=None,
        sample_table=None,
        std_isotop_dist_table=None,
    ):
        self.peaks_table = peaks_table
        self.samples = samples
        self.config = config
        self.result = None
        self.calibration_table = calibration_table
        self.sample_table = sample_table
        self.std_isotop_dist_table = std_isotop_dist_table

    def extract_peaks(self):
        key = extract_peaks.__name__
        kwargs = get_kwargs(self.config, key)
        self.result = extract_peaks(self.peaks_table, self.samples, kwargs)
        update_sample_information(self.result, self.sample_table, kwargs)
        update_applied_processing_steps(self.result, key)

    def coeluting_peaks(self):
        key = coeluting_peaks.__name__
        kwargs = get_kwargs(self.config, key)
        self.result = coeluting_peaks(self.result, kwargs)
        update_applied_processing_steps(self.result, key)

    def correct_isotopologue_overlays(self):
        key = correct_isotopologue_overlays.__name__
        kwargs = get_kwargs(self.config, key)
        correct_isotopologue_overlays(self.result, kwargs, self.std_isotop_dist_table)
        update_applied_processing_steps(self.result, key)

    def tic_normalize_peaks(self):
        key = tic_normalize_peaks.__name__
        kwargs = get_kwargs(self.config, key)
        self.result = tic_normalize_peaks(self.result, kwargs)
        update_applied_processing_steps(self.result, key)

    def pq_normalize_peaks(self):
        key = pq_normalize_peaks.__name__
        kwargs = get_kwargs(self.config, key)
        self.result = pq_normalize_peaks(self.result, kwargs)
        update_applied_processing_steps(self.result, key)

    def normalize_peaks(self):
        key = normalize_peaks.__name__
        kwargs = get_kwargs(self.config, key)
        self.result = normalize_peaks(self.result, kwargs)
        update_applied_processing_steps(self.result, key)

    def classify_peaks(self):
        key = classify_peaks.__name__
        kwargs = get_kwargs(self.config, key)
        self.result = classify_peaks(self.result, kwargs)
        update_applied_processing_steps(self.result, key)

    def quantify(self):
        key = quantify.__name__
        kwargs = get_kwargs(self.config, key)
        self.result = quantify(self.result, kwargs, self.calibration_table)
        update_applied_processing_steps(self.result, key)

    def check_qualifier_peaks(self):
        key = check_qualifier_peaks.__name__
        kwargs = get_kwargs(self.config, key)
        self.result = check_qualifier_peaks(self.result, kwargs)
        update_applied_processing_steps(self.result, key)


class PostProcessResult(ProcessingSteps):
    def __init__(
        self,
        table,
        config,
        calibration_table=None,
        std_isotop_dist_table=None,
        process_only_tracked_changes=False,
        splitting_cols=["filename", "compound"],
    ):
        self.config = config
        self.calibration_table = calibration_table
        self.std_isotop_dist_table = std_isotop_dist_table
        self.result, self.fixed = extract_track_changes(
            table, process_only_tracked_changes, splitting_cols
        )

    def merge_reprocessed(self):
        if self.fixed is None:
            return
        self.result = Table.stack_tables([self.fixed, self.result]).sort_by("row_id")


def update_applied_processing_steps(t, processing_step_name):
    if not "applied_processing_steps" in t.meta_data.keys():
        t.meta_data["applied_processing_steps"] = set([])
    y = t.meta_data["applied_processing_steps"]
    y.add(processing_step_name)
    t.meta_data["applied_processing_steps"] = y


def get_kwargs(config, key):
    kwargs = config.get(key)
    return kwargs if kwargs is not None else {}
