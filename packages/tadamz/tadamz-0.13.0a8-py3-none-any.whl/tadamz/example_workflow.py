import os
from .workflow import run_workflow
from pathlib import Path
from .inout import load_config, load_samples_from_folder, load_peaks_table
from emzed import gui

#  folders
home = Path.home().as_posix()
here = os.path.abspath(os.path.dirname(__file__))
data_folder = os.path.join(here, "data")


def run():
    data = _load_example_data()
    result = run_workflow(*data)
    gui.inspect(result)


def _load_example_data():
    path = os.path.join(data_folder, "example.config.txt")
    config = load_config(path)
    samples = load_samples_from_folder(data_folder)
    path = os.path.join(data_folder, "example_peaks.table")
    peaks_table = load_peaks_table(path)
    return peaks_table, samples, config


def description():
    pass
