#!/usr/bin/env python
import pickle
import re

import numpy as np
import pyopenms


def encode(s):
    if isinstance(s, str):
        return s.encode("utf-8")
    return s


def decode(s):
    if isinstance(s, bytes):
        return str(s, "utf-8")
    return s


def load_experiment_detailed(path):
    experiment = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(encode(path), experiment)
    dt = experiment.getDateTime()
    timestamp = " ".join([dt.getDate(), dt.getTime()])
    return (
        spectra(experiment),
        chromatograms(experiment),
        decode(experiment.getLoadedFilePath()),
        timestamp,
    )


def spectra(mse):
    return pickle.dumps(
        sorted(
            [extract_spectrum(mse[i]) for i in range(mse.size())],
            key=lambda t: t[1],
        )
    )


def chromatograms(mse):
    return pickle.dumps(
        [
            (
                chromatogram.getMZ(),
                chromatogram.getPrecursor().getMZ(),
                chromatogram.get_peaks(),
                chromatogram.getChromatogramType(),
            )
            for chromatogram in mse.getChromatograms()
        ]
    )


def extract_spectrum(mspec):
    precursors = [
        (p.getMZ(), p.getIntensity(), p.getCharge()) for p in mspec.getPrecursors()
    ]
    polarity = {
        pyopenms.IonSource.Polarity.POLNULL: "0",
        pyopenms.IonSource.Polarity.POSITIVE: "+",
        pyopenms.IonSource.Polarity.NEGATIVE: "-",
    }.get(mspec.getInstrumentSettings().getPolarity())
    peaks = mspec.get_peaks()

    # sort by mz
    mz, ii = peaks
    perm = np.argsort(mz)
    peaks = np.hstack((mz[perm, None], ii[perm, None]))

    native_id = mspec.getNativeID()
    scan_number = _extract_scan_number(native_id)

    # signature changed in pyopenms
    return peaks, mspec.getRT(), mspec.getMSLevel(), polarity, precursors, scan_number


def _extract_scan_number(native_id):
    native_id = encode(native_id)
    for pattern in (rb"scan[^=]*=(\d+)", rb"spectrum=(\d+)"):
        match = re.search(pattern, native_id)
        if match:
            match = match.groups()[0]
            try:
                scan_number = int(match)
            except ValueError:
                raise ValueError(
                    f"scan number entry in {native_id!r} is not a valid int"
                )
            break
    else:
        raise ValueError(f"cound not parse {native_id!r} to extract scan number")
    return scan_number


# def to_openms_experiment(data):
#     spectra, ms_chromatograms, source = pickle.loads(data)
#     exp = pyopenms.MSExperiment()
#     for s in spectra:
#         exp.addSpectrum(to_openms_spectrum(*s))

#     for ms_chromatogram in ms_chromatograms:
#         exp.addChromatogram(to_openms_chromatogram(*ms_chromatogram))

#     exp.updateRanges()
#     exp.setLoadedFilePath(encode(source))
#     return exp


# def to_openms_chromatogram(mz, precursor_mz, rts, intensities, type_):
#     product = pyopenms.Product()
#     product.setMZ(mz)

#     precursor = pyopenms.Precursor()
#     precursor.setMZ(precursor_mz)

#     c = pyopenms.MSChromatogram()
#     c.setProduct(product)
#     c.setPrecursor(precursor)
#     c.set_peaks((rts, intensities))
#     c.setChromatogramType(type_)
#     return c


# def to_openms_spectrum(
#     rt, ms_level, polarity, precursors, mzs, intensities, scan_number
# ):
#     """converts to pyopenms.MSSpectrum"""
#     spec = pyopenms.MSSpectrum()
#     spec.setRT(rt)
#     spec.setMSLevel(ms_level)
#     ins = spec.getInstrumentSettings()
#     pol = {
#         "0": pyopenms.IonSource.Polarity.POLNULL,
#         "+": pyopenms.IonSource.Polarity.POSITIVE,
#         "-": pyopenms.IonSource.Polarity.NEGATIVE,
#     }[polarity]
#     ins.setPolarity(pol)
#     spec.setInstrumentSettings(ins)
#     oms_pcs = []
#     for mz, ii, charge in precursors:
#         p = pyopenms.Precursor()
#         p.setMZ(mz)
#         p.setIntensity(ii)
#         p.setCharge(charge)
#         oms_pcs.append(p)
#     spec.setPrecursors(oms_pcs)
#     spec.set_peaks((mzs, intensities))
#     if scan_number is not None:
#         spec.setNativeID("scan=%d" % scan_number)
#     spec.updateRanges()
#     return spec


# def feature_finder(
#     verbose, mse, mtd_params, epdet_params, run_feature_grouper, ffm_params
# ):
#     info = print if verbose else lambda *a, **kw: None

#     log_type = pyopenms.LogType.NONE

#     info()
#     info("run mass trace detection")

#     mtd = pyopenms.MassTraceDetection()
#     mtd.setLogType(log_type)

#     mtd.setParameters(mtd_params)
#     mass_traces = []

#     try:
#         mtd.run(mse, mass_traces, max_traces=2**64 - 1)  # max unsigned int64
#     except Exception:
#         info("no mass traces found")

#     info("found %d mass traces" % len(mass_traces))
#     info()

#     mass_traces.sort(key=lambda mt: mt.getCentroidMZ())

#     rows = []
#     splitted_mass_traces = []
#     if mass_traces:
#         info("run elution peak detection")
#         epdet = pyopenms.ElutionPeakDetection()
#         epdet.setLogType(log_type)
#         epdet.setParameters(epdet_params)
#         splitted_mass_traces = []
#         epdet.detectPeaks(mass_traces, splitted_mass_traces)

#     splitted_mass_traces.sort(key=lambda mt: (mt.getCentroidMZ(), mt.getCentroidRT()))

#     if splitted_mass_traces and run_feature_grouper:
#         if epdet_params.getValue("width_filtering") == "auto":
#             final_mass_traces = []
#             epdet.filterByPeakWidth(splitted_mass_traces, final_mass_traces)
#         else:
#             final_mass_traces = splitted_mass_traces

#         info(
#             "%d splitted mass traces after elution peak detection"
#             % len(final_mass_traces)
#         )
#         info()

#         ffm = pyopenms.FeatureFindingMetabo()
#         ffm.setLogType(log_type)
#         ffm.setParameters(ffm_params)
#         feature_map = pyopenms.FeatureMap()
#         chromatograms = []
#         ffm.run(final_mass_traces, feature_map, chromatograms)

#         info("found %d features" % feature_map.size())
#         info()
#         rows = _prepare_feature_table_data(feature_map, mse)

#     else:
#         rows = _prepare_peak_table_data(mass_traces, mse)

#     return pickle.dumps(rows)


# def _prepare_feature_table_data(feature_map, mse):
#     rows = []
#     for i, feature in enumerate(sorted(feature_map, key=lambda f: f.getMZ())):
#         intensity = feature.getIntensity()
#         quality = feature.getOverallQuality()
#         width = feature.getWidth()
#         z = feature.getCharge()
#         rts = feature.getMetaValue(b"masstrace_centroid_rt")
#         mzs = feature.getMetaValue(b"masstrace_centroid_mz")
#         intensities = feature.getMetaValue(b"masstrace_intensity")
#         convex_hulls = feature.getConvexHulls()
#         for convex_hull, rt, mz, intensity in zip(convex_hulls, rts, mzs, intensities):
#             bb = convex_hull.getBoundingBox()
#             rtmin, mzmin = bb.minPosition()
#             rtmax, mzmax = bb.maxPosition()
#             if intensity == 0.0:
#                 # fix issue from openms
#                 intensity = _area(mse, mzmin, mzmax, rtmin, rtmax)
#             row = [i, mz, mzmin, mzmax, rt, rtmin, rtmax, intensity, quality, width, z]
#             rows.append(row)
#     return rows


# def _prepare_peak_table_data(elution_peaks, mse):
#     rows = []
#     for elution_peak in elution_peaks:
#         convex_hull = elution_peak.getConvexhull()
#         quality = None
#         width = elution_peak.getFWHM()
#         z = None
#         mz = elution_peak.getCentroidMZ()
#         rt = elution_peak.getCentroidRT()
#         bb = convex_hull.getBoundingBox()
#         rtmin, mzmin = bb.minPosition()
#         rtmax, mzmax = bb.maxPosition()
#         intensity = elution_peak.getIntensity(False)  # not smoothed
#         if intensity == 0.0:
#             # fix issue from openms
#             intensity = _area(mse, mzmin, mzmax, rtmin, rtmax)
#         row = [None, mz, mzmin, mzmax, rt, rtmin, rtmax, intensity, quality, width, z]
#         rows.append(row)
#     return rows


# def _area(mse, mzmin, mzmax, rtmin, rtmax):
#     area = 0.0
#     for s in mse.getSpectra():
#         if rtmin <= s.getRT() <= rtmax:
#             mzs, iis = s.get_peaks()
#             area += np.sum(iis[(mzmin <= mzs) * (mzs <= mzmax)])
#     return area


# def transform_rt_values(transformation, rts):
#     apply = transformation.apply
#     return [apply(rti) for rti in rts]


# def merge_spectra(spectra, mz_binning_width, ppm, rt_block_size, ms_level):
#     exp = to_openms_experiment(spectra)

#     merger = pyopenms.SpectraMerger()
#     params = merger.getDefaults()
#     params.setValue("mz_binning_width", mz_binning_width)
#     params.setValue("mz_binning_width_unit", ppm)
#     params.setValue("block_method:rt_block_size", rt_block_size)
#     params.setValue("block_method:ms_levels", [ms_level])
#     merger.setParameters(params)

#     merger.mergeSpectraBlockWise(exp)
#     assert exp.size() == 1, "looks like mergeSpectraBlockWise failed"

#     peaks, rt, ms_level, polarity, precursors, scan_number = extract_spectrum(exp[0])
#     return scan_number, rt, ms_level, polarity, peaks


optimizations = {
    "MSSpectrum.extract_spectrum": extract_spectrum,
    "MSExperiment.spectra": spectra,
    "MSExperiment.chromatograms": chromatograms,
    # "module.to_openms_spectrum": to_openms_spectrum,
    # "module.to_openms_chromatogram": to_openms_chromatogram,
    # "module.to_openms_experiment": to_openms_experiment,
    "module.load_experiment_detailed": load_experiment_detailed,
    # "module.feature_finder": feature_finder,
    # "module.transform_rt_values": transform_rt_values,
    # "module.merge_spectra": merge_spectra,
}
