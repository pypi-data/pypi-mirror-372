# -*- coding: utf-8 -*-
""" """

"""

Created on Thu Oct 10 09:35:12 2024

@author: pkiefer

TO DO:
- Integrate std isotope table
- change dictionary key or introduce pid
"""

import numpy as np
import emzed
import pandas as pd
from emzed import adducts, chemistry, elements, mass, MzType
from collections import defaultdict
from scipy.linalg import solve
from scipy.special import binom
from math import prod


def correct_isotopologue_overlays(t, kwargs, std_isotope_dist_table=None):
    """
    corrects for isotopologue peak overlays of stable isotope labeled standard and
    natural labeled sample. Partial peak overlaps are also taken into account.

    Parameters
    ----------
    t : emzed Table
        Table with mandatory columns listed below.
    std_isotope_dist_table : emzed.Table
        Table with the isotopologue fractions of the internal standard. It
        is only required if an  internal standard isotopologue peak overlaps
        with the (monoisotopic) quantifier peak of the sample
    kwargs : dictionary
        with keyword arguments:
            compound_col : str, optional
                Nome of the column with compound names. The default is 'compound'.
            mf_col : str, optional
                Nome of the column with the compound's molecurlar formula. The default is 'mf'.
            norm_group_col : str, optional
                Nome of the column with grouping id for peak normalization.
                The id refers to the standard peak(s) used for normalization
                The default is 'normalize_by_std_id'.
            std_group_col : std, optional
                Nome of the column containing ids of the standard peaks.
                The default is 'std_id'.
            adduct_col : str, optional
                Nome of the column with adduct names. The default is 'adduct'.
            filename_col : str, optional
                Nome of the column with the mz(X)ML filename. The default is 'filename'.
            mztol : float, optional
                mz tolerance of the extracted ion chromatogram m/z +- mztol.
                The default is 0.003.
            precursor_mztol : float, optional
                m/z tolerance of the precurrsor ion  m/z +- precursor_mztol. (ms level 2 data).
                The default is 0.5.
            mf_fragment_col : str, optional
                Nome of the column with molecurlar formula of the fragemnt (ms level 2). The default is None.
            adduct_fragment_col : str, optional
                Nome of the column with adduct names (ms level 2). The default is None.


    Returns
    -------
    None.

    """
    _correct_isotopologue_overlays(t, std_isotope_dist_table, **kwargs)


def _correct_isotopologue_overlays(
    t,
    std_isotope_dist_table=None,
    compound_col="compound",
    mf_col="mf",
    norm_group_col="normalize_by_std_id",
    std_group_col="std_id",
    adduct_col="adduct",
    filename_col="filename",
    mztol_abs=0.003,
    mztol_rel=0,
    precursor_mztol=0.5,
    mf_fragment_col=None,
    adduct_fragment_col=None,
    **kwargs,
):
    _table_has_required_columns(
        t,
        mf_col,
        norm_group_col,
        std_group_col,
        adduct_col,
        mf_fragment_col,
        adduct_fragment_col,
        filename_col,
    )
    _parent_mf_includes_fragment_mf(t, mf_col, mf_fragment_col, compound_col)
    _normalize_abundances(std_isotope_dist_table, std_group_col)
    _update_isotopologue_distribution_table(
        t,
        std_isotope_dist_table,
        mztol_abs,
        mztol_rel,
        precursor_mztol,
        compound_col,
        mf_col,
        adduct_col,
        mf_fragment_col,
        adduct_fragment_col,
    )
    id2sample_tuple = _group_features(
        t, norm_group_col, mf_col, adduct_col, mf_fragment_col, adduct_fragment_col
    )
    id2std_tuple = _group_features(
        t, std_group_col, mf_col, adduct_col, mf_fragment_col, adduct_fragment_col
    )
    id_sample2id_std2fcorr = get_std_correction_factor_dict(
        id2sample_tuple, id2std_tuple, mztol_abs, mztol_rel, precursor_mztol
    )
    id_std2id_sample2fcorr = get_sam_correction_factor_dict(
        id2sample_tuple,
        id2std_tuple,
        std_isotope_dist_table,
        mztol_abs,
        mztol_rel,
        precursor_mztol,
    )
    # return id_sample2id_std2fcorr, id_std2id_sample2fcorr
    source_id2model = dict(zip(zip(t[filename_col], t.id), t.model_chromatogram))
    norm_id2ids = _grouped_peaks_as_dict(t, norm_group_col)
    std_id2ids = _grouped_peaks_as_dict(t, std_group_col)
    sources = set(t[filename_col])
    # id_sample2id_std2fcorr, id_std2id_sample2fcorr, source_id2model , norm_id2ids, std_id2ids, sources
    pair2area_corr = get_source_id2area_corrs(
        id_sample2id_std2fcorr,
        id_std2id_sample2fcorr,
        source_id2model,
        norm_id2ids,
        std_id2ids,
        sources,
    )
    # for key in pair2area_corr.keys():
    #     print(key, pair2area_corr[key], source_id2model[key].area)
    # print()
    _update_isotopologue_correction(t, pair2area_corr, filename_col)


def _update_isotopologue_distribution_table(
    t, dist_table, mztol_abs, mztol_rel, precursor_mz_tol, *columns
):
    if dist_table:
        # dist table contains no id. To avoid combersome keys
        # we add the peak id `id` originating from the targets table to dist_table
        dist_table.add_enumeration("rowid")
        ms_level2 = all([col is not None for col in columns])
        _update_mz_values(dist_table, ms_level2, *columns)
        compound_col, mf_col, adduct_col, mf_frag_col, adduct_frag_col = columns
        cols = [col for col in columns if col is not None]
        cols.append("id")
        check = emzed.Table.from_pandas(
            t.extract_columns(*cols).to_pandas().drop_duplicates()
        )
        if ms_level2:
            check.add_column(
                "precursor_mz",
                check.apply(_get_mz, check[mf_col], check[adduct_col]),
                MzType,
            )
            check.add_column(
                "mz",
                check.apply(_get_mz, check[mf_frag_col], check[adduct_frag_col]),
                MzType,
            )
            comp = check.join(
                dist_table,
                check.mz.approx_equal(dist_table.mz, mztol_abs, mztol_rel)
                & check.precursor_mz.approx_equal(
                    dist_table.precursor_mz, precursor_mz_tol, 0
                ),
            )
        else:
            check.add_column(
                "mz", check.apply(_get_mz, check[mf_col], check[adduct_col]), MzType
            )
            comp = check.join(
                dist_table, check.mz.approx_equal(dist_table.mz, mztol_abs, mztol_rel)
            )
        rowid2id = dict(zip(comp.rowid__0, comp.id))
        dist_table.add_or_replace_column(
            "id",
            dist_table.apply(rowid2id.get, dist_table.rowid, ignore_nones=False),
            int,
            insert_before="rowid",
        )
        dist_table.drop_columns("rowid")


def _update_mz_values(dist_table, ms_level2, *columns):
    compound_col, mf_col, adduct_col, mf_frag_col, adduct_frag_col = columns

    mz_cols = ["mz", "precursor_mz"] if ms_level2 else ["mz"]
    if all([col in dist_table.col_names for col in mz_cols]):
        return
    if ms_level2:
        dist_table.add_column(
            "precursor_mz",
            dist_table.apply(
                _get_mz, dist_table[mf_col], dist_table[adduct_col], ignore_nones=False
            ),
            MzType,
        )
        dist_table.add_column(
            "mz",
            dist_table.apply(
                _get_mz,
                dist_table[mf_frag_col],
                dist_table[adduct_frag_col],
                ignore_nones=False,
            ),
            MzType,
        )


def _table_has_required_columns(t, *colnames):
    missings = [
        name for name in colnames if name is not None and name not in t.col_names
    ]
    msg = f"""Correcting peak areas for overlapping isotopologue peaks is not possible since columns
    {', '.join(missings)} were not in peaks_table. Please set parameter `correct_for_natural_abundance`to false
    or add missing columns to peaks_table and reprocess the data.
    """
    assert len(missings) == 0, msg


def _normalize_abundances(t, std_group_col):
    if t is not None:
        group = t.group_by(t[std_group_col])
        t.add_column("max_abundance", group.max(t.abundance), float)
        t.replace_column(
            "abundance", t.abundance / t.max_abundance, float, format_="%.3f"
        )
        t.drop_columns("max_abundance")


def _grouped_peaks_as_dict(t, group_col):
    d = defaultdict(list)
    for key, value in set(zip(t[group_col], t.id)):
        if key is not None:
            d[key].append(value)
    return d


# -----
def _group_features(t, *columns):
    d = defaultdict(list)
    expr = [_get_col(t, col) for col in columns]
    # column `id` is peak specific since it is added to the peaks_table, initially
    # we can use `id` to assign the correction factors to the correct peakls
    expr.append(t.id)
    for ntuple in set(zip(*expr)):
        if ntuple[0] is not None:
            d[ntuple[0]].append(tuple(ntuple[1:]))
    return d


def _get_col(t, col):
    return t[col].to_list() if col is not None else [None] * len(t)


# -----


def _get_tuple_key(d, *keys):
    return d.get(keys)


# --------------------------------------------------------
def get_std_correction_factor_dict(
    id2sample_tuple, id2std_tuple, mztol_abs, mztol_rel, precursor_mztol
):
    """
    We determine the  contribution factor of the sample isotopologue peaks
    to the internal standard peaks
    """
    id2id2fcorr = defaultdict(dict)
    # import pdb; pdb.set_trace()
    for key, tuples1 in id2sample_tuple.items():
        for tuple1 in tuples1:
            for tuple2 in id2std_tuple[key]:
                mf1, adduct1, mf_frag1, adduct_frag1, id1 = tuple1
                mf_frag1 = mf1 if mf_frag1 is None else mf_frag1
                adduct_frag1 = adduct1 if adduct_frag1 is None else adduct_frag1
                mf2, adduct2, mf_frag2, adduct_frag2, id2 = tuple2
                mf_frag2 = mf2 if mf_frag2 is None else mf_frag2
                adduct_frag2 = adduct2 if adduct_frag2 is None else adduct_frag2
                # ms2values = [mf_frag1, mf_frag2, adduct_frag1, adduct_frag2]
                # if all([v is None for v in ms2values]):
                #     mz = _get_mz(mf2, adduct2)
                #     f_corr = _calculate_correction_factor_ms1(
                #         mf1, adduct1, mz, mztol_abs, mztol_rel
                #     )
                # else:
                precursor_mz = _get_mz(mf2, adduct2)
                mz = _get_mz(mf_frag2, adduct_frag2)
                f_corr = _calculate_correction_factor_ms2(
                    mf1,
                    adduct1,
                    mf_frag1,
                    adduct_frag1,
                    mz,
                    mztol_abs,
                    mztol_rel,
                    precursor_mz,
                    precursor_mztol,
                )
                id2id2fcorr[id1][id2] = f_corr
    return id2id2fcorr


def get_sam_correction_factor_dict(
    id2tuple_sam, id2std_tuple, dist_table, mztol_abs, mztol_rel, precursor_mz_tol
):
    # import pdb; pdb.set_trace()
    id2id2fcorr = defaultdict(dict)
    for key, tuples1 in id2std_tuple.items():
        for tuple1 in tuples1:
            sid = tuple1[-1]
            for stuple in id2tuple_sam[key]:
                mf, adduct, mf_frag, adduct_frag, sid1 = stuple
                is_ms1 = all([col is None for col in [mf_frag, adduct_frag]])
                is_ms2 = all([mf_frag, adduct_frag])
                if is_ms1 and _is_ms1_level(dist_table):
                    mz = _get_mz(mf, adduct)
                    cand = dist_table.filter(
                        (dist_table.std_id == key)
                        & dist_table.mz.approx_equal(mz, mztol_abs, mztol_rel),
                        keep_view=True,
                    )
                    for row in cand.rows:
                        id2id2fcorr[sid][row.id] = row.abundance
                elif is_ms2 and _is_ms2_level(dist_table):
                    mz = _get_mz(mf_frag, adduct_frag)
                    precursor_mz = _get_mz(mf, adduct)
                    cand = dist_table.filter(
                        (dist_table.std_id == key)
                        & dist_table.mz.approx_equal(mz, mztol_abs, mztol_rel)
                        & dist_table.precursor_mz.approx_equal(
                            precursor_mz, precursor_mz_tol, 0
                        ),
                        keep_view=True,
                    )
                    print(mz, precursor_mz, mztol_abs, mztol_rel, precursor_mz_tol)
                    # cand.print_()
                    for row in cand.rows:
                        id2id2fcorr[sid][row.id] = row.abundance
                # handle missing standards
                if not sid1 in id2id2fcorr[sid]:
                    id2id2fcorr[sid][sid1] = 0

    return id2id2fcorr


def _is_ms1_level(t):
    if t is None:
        return False
    if "precursor_mz" in t.col_names:
        return t.precursor_mz.count_not_none() == 0
    return True


def _is_ms2_level(t):
    if t is None:
        return False
    return t.precursor_mz.count_not_none() == len(t)


# ------
# def _calculate_correction_factor_ms1(mf, adduct, mz, mztol_abs, mztol_rel):
#     t_dis = _build_isotope_table(mf, adduct)
#     t_dis = t_dis.filter(t_dis.mz.approx_equal(mz, mztol_abs, mztol_rel))
#     return sum(t_dis.abundance)


def _calculate_correction_factor_ms2(
    mf,
    adduct,
    mf_frag,
    adduct_frag,
    mz,
    mztol_abs,
    mztol_rel,
    precursor_mz,
    precursor_mztol,
):
    el2mono = _element_to_monoisotopic_mass_number()
    t_dis = _build_isotope_table(mf, adduct)
    t_dis = t_dis.filter(t_dis.mz.approx_equal(precursor_mz, precursor_mztol, 0))
    t_dis_frag = _build_isotope_table(mf_frag, adduct_frag).consolidate()
    t_dis_frag = t_dis_frag.filter(t_dis_frag.mz.approx_equal(mz, mztol_abs, mztol_rel))
    comb = t_dis.join(t_dis_frag)
    comb.add_column(
        "p_ms2",
        comb.apply(_calc_propability, comb.mf, comb.mf__0, el2mono),
        float,
        format_="%.2e",
    )
    return float(
        np.nansum(np.array(comb.abundance.to_list()) * np.array(comb.p_ms2.to_list()))
    )


def _parent_mf_includes_fragment_mf(t, mf_col, mf_fragment_col, compound_col):
    if mf_fragment_col is None:
        return
    # _consistent_mf_frag(t, compound_col, mf_fragment_col)
    t.add_or_replace_column(
        "covered",
        t.apply(_mf1_includes_mf2, t[mf_col], t[mf_fragment_col], ignore_nones=False),
        bool,
    )
    d = defaultdict(list)
    for compound, mf, mf_frag, covered in set(
        zip(t.compound, t[mf_col], t[mf_fragment_col], t.covered)
    ):
        if not covered:
            d[compound_col].append(compound)
            d[mf_col].append(mf)
            d[mf_fragment_col].append(mf_frag)

    df = pd.DataFrame.from_dict(d)
    covered = t.covered.to_list()
    t.drop_columns("covered")
    msg = f"parent formulas of following compounda do not cover corresponding fragment formulas \n {df.to_string()}"
    assert all(covered), msg


# def _consistent_mf_frag(t, compound_col, mf_fragment_col):
#     # we replace None by ''
#     t.replace_column(mf_fragment_col, t[mf_fragment_col].is_none().then_else('', t[mf_fragment_col]), str)
#     d = defaultdict(list)
#     inconsistent = []
#     for comp, frag in set(zip(t[compound_col], t[mf_fragment_col])):
#         d[comp].append(frag)
#     for key, values in d.items():
#         try:
#             cond1 = all([v=='' for v in values])
#             cond2 = all([emzed.mf(v).mass() > 0 for v in values])
#         except:
#             cond1 = False
#             cond2 = False
#         if cond1 or cond2:
#             pass
#         else:
#             inconsistent.append(key)
#     msg = f"Following compoumnds are not consistent with formula correction: {', '.join(inconsistent)}"
#     assert not len(inconsistent), msg


def _mf1_includes_mf2(mf1, mf2):
    mf2 = "" if mf2 is None else mf2
    y = (emzed.mf(mf1) - emzed.mf(mf2)).as_dict()
    return all(np.array(list(y.values())) >= 0)


def _get_mz(mf, adduct):
    mf_ion, z_sign = _get_mf_ion(mf, adduct)
    return (emzed.mass.of(mf_ion) + z_sign * emzed.mass.e) / abs(z_sign)


def _element_to_monoisotopic_mass_number():
    t = elements.consolidate()
    t.add_column(
        "monoisotopic_mass_number",
        t.group_by(t.symbol).aggregate(_mono, t.mass_number, t.abundance),
        int,
    )
    return dict(zip(t.symbol, t.monoisotopic_mass_number))


def _mono(mass_numbers, abundances):
    return max(zip(mass_numbers, abundances), key=lambda v: v[1])[0]


def _build_isotope_table(mf, adduct, replace=True):
    mf_ion, z_sign = _get_mf_ion(mf, adduct)
    t_dis = chemistry.compute_centroids(mf_ion, 0.9999)
    t_dis.add_column("mz", (t_dis.m0 + z_sign * mass.e) / abs(z_sign), MzType)
    # we normalize to the monoisotopic peak
    if replace:
        t_dis.replace_column(
            "abundance", t_dis.abundance / max(t_dis.abundance), float, format_="%.3f"
        )
    return t_dis


def _calc_propability(mf, mf_frag, el2mono):
    par_dict = emzed.mf(_update_isotope(mf, el2mono)).as_dict()
    frag_dict = emzed.mf(_update_isotope(mf_frag, el2mono)).as_dict()
    el2num_par = _el2num(par_dict)
    el2num_frag = _el2num(frag_dict)
    probabilities = []

    ### hypergeometric density function
    # source https://en.wikipedia.org/wiki/Hypergeometric_distribution
    # (binom(M, x) * binom(N-M, n-x))/binom(N, n)
    # with M: number of el with specific isotop in parent,N: total number of element in parent x: number of isotopes in fragment ion,
    # n; number of element in fragment ion
    for el in el2num_frag.keys():
        par_isotopes = {key: par_dict[key] for key in par_dict.keys() if key[0] == el}
        frag_isotopes = {
            key: frag_dict[key] for key in frag_dict.keys() if key[0] == el
        }
        for key in frag_isotopes:
            M = par_isotopes[key] if key in par_isotopes else 0
            x = frag_isotopes[key]
            N = el2num_par[el]
            n = el2num_frag[el]
            probabilities.append((binom(M, x) * binom(N - M, n - x)) / binom(N, n))
    return prod(probabilities)


def _el2num(mf_dict):
    el2num = defaultdict(int)
    for key, num in mf_dict.items():
        el, iso = key
        el2num[el] += num
    return el2num


def _update_isotope(mf, el2mon_no):
    d = emzed.mf(mf).as_dict()
    fields = []
    for pair, no in d.items():
        atom, atom_number = pair
        atom_number = atom_number if atom_number else el2mon_no[atom]
        no = "" if no == 1 else str(no)
        fields.append(f"[{atom_number}]{atom}{no}")
    return "".join(fields)


def _get_mf_ion(mf, adduct):
    t_add = _get_adduct_table(adduct)
    z_sign = t_add.sign_z.unique_value() * t_add.z.unique_value()
    mf_add = t_add.adduct_add.unique_value()
    mf_sub = t_add.adduct_sub.unique_value()
    mf_ion = emzed.mf(mf) + emzed.mf(mf_add) - emzed.mf(mf_sub)
    return mf_ion.as_string(), z_sign


def _get_adduct_table(adduct_name):
    name2key = _adduct_name2key()
    key = name2key[adduct_name]
    return adducts.__dict__[key]


def _adduct_name2key():
    d = {
        "M-3H": "M_minus_3H",
        "M-2H": "M_minus_2H",
        "M-": "M_minus_",
        "M-H": "M_minus_H",
        "M-H2O-H": "M_minus_H2O_minus_H",
        "M+Na-2H": "M_plus_Na_minus_2H",
        "M+Cl": "M_plus_Cl",
        "M+K-2H": "M_plus_K_minus_2H",
        "M+KCl-H": "M_plus_KCl_minus_H",
        "M+FA-H": "M_plus_FA_minus_H",
        "M+F": "M_plus_F",
        "M+Hac-H": "M_plus_Hac_minus_H",
        "M+Br": "M_plus_Br",
        "M+TFA-H": "M_plus_TFA_minus_H",
        "2M-H": "2M_minus_H",
        "2M+FA-H": "2M_plus_FA_minus_H",
        "2M+Hac-H": "2M_plus_Hac_minus_H",
        "3M-H": "3M_minus_H",
        "M": "M",
        "M+": "M_plus_",
        "M+H": "M_plus_H",
        "M+NH4": "M_plus_NH4",
        "M+Na": "M_plus_Na",
        "M+H-2H2O": "M_plus_H_minus_2H2O",
        "M+H-H2O": "M_plus_H_minus_H2O",
        "M+K": "M_plus_K",
        "M+ACN+H": "M_plus_ACN_plus_H",
        "M+2ACN+H": "M_plus_2ACN_plus_H",
        "M+ACN+Na": "M_plus_ACN_plus_Na",
        "M+2Na-H": "M_plus_2Na_minus_H",
        "M+Li": "M_plus_Li",
        "M+CH3OH+H": "M_plus_CH3OH_plus_H",
        "M+2K-H": "M_plus_2K_minus_H",
        "M+IsoProp+H": "M_plus_IsoProp_plus_H",
        "M+IsoProp+Na+H": "M_plus_IsoProp_plus_Na_plus_H",
        "M+DMSO+H": "M_plus_DMSO_plus_H",
        "2M+H": "2M_plus_H",
        "2M+NH4": "2M_plus_NH4",
        "2M+Na": "2M_plus_Na",
        "2M+K": "2M_plus_K",
        "2M+ACN+H": "2M_plus_ACN_plus_H",
        "2M+ACN+Na": "2M_plus_ACN_plus_Na",
        "M+H+NH4": "M_plus_H_plus_NH4",
        "M+2ACN+2H": "M_plus_2ACN_plus_2H",
        "M+3ACN+2H": "M_plus_3ACN_plus_2H",
        "M+ACN+2H": "M_plus_ACN_plus_2H",
        "M+2H": "M_plus_2H",
        "M+H+Na": "M_plus_H_plus_Na",
        "M+H+K": "M_plus_H_plus_K",
        "M+2Na": "M_plus_2Na",
        "M+3H": "M_plus_3H",
        "M+2H+Na": "M_plus_2H_plus_Na",
        "M+3Na": "M_plus_3Na",
        "M+2Na+H": "M_plus_2Na_plus_H",
    }
    return d


# ----------------------------------------------------------------------


def get_source_id2area_corrs(
    id_sample2id_std2fcorr,
    id_std2id_sample2fcorr,
    source_id2model,
    norm_id2ids,
    std_id2ids,
    sources,
):
    # import pdb; pdb.set_trace()
    source_id2area_corr = {}
    for source in sources:
        for norm_id, ids_sam in norm_id2ids.items():

            models_sam = [source_id2model[(source, id_)] for id_ in ids_sam]
            ids_std = std_id2ids[norm_id]
            models_std = [source_id2model[(source, id_)] for id_ in ids_std]
            # source -> target -> fcorr
            # std_id -> sample_id -> fcorr
            fcorrs_sam = _group_fcors(ids_std, ids_sam, id_std2id_sample2fcorr)
            # sample_id -> std_id -_> f_corr
            fcorrs_std = _group_fcors(ids_sam, ids_std, id_sample2id_std2fcorr)
            areas_corr_std, areas_corr_sam = _solve_overlapping_areas(
                models_std, models_sam, fcorrs_std, fcorrs_sam
            )
            _update_areas_corr(source_id2area_corr, source, ids_std, areas_corr_std)
            _update_areas_corr(source_id2area_corr, source, ids_sam, areas_corr_sam)
    return source_id2area_corr


def _group_fcors(ids1, ids2, id12id2fcorr):
    mat = np.ones((len(ids1), len(ids2)))
    for i in range(len(ids1)):
        for j in range(len(ids2)):
            mat[i][j] = id12id2fcorr[ids1[i]][ids2[j]]
    return mat


def _update_areas_corr(d, source, ids, areas_corr):
    assert len(ids) == len(areas_corr)
    for id_, area_corr in zip(ids, areas_corr):
        key = source, id_
        assert key not in d.keys()
        d[key] = area_corr[0]


# -----
def _solve_overlapping_areas(models_is, models, fs_is, fs_nl):
    # we subtract the isotopologues
    no_is = len(models_is)
    no_nl = len(models)
    c_is = all([_check_model(m) for m in models_is])
    c_sam = all([_check_model(m) for m in models])
    # import pdb; pdb.set_trace()
    if c_is and c_sam:
        mat = np.zeros((no_is + no_nl, no_is + no_nl))
        res_vec = _result_vec(models, models_is)
        for i, model_is in enumerate(models_is):
            for j, model in enumerate(models):
                rts_is, ints_is = model_is.graph()
                rts, ints = model.graph()
                if len(rts) and len(rts_is):
                    # we determine the overalpping area in the
                    # resulting overlapping integration window regions:
                    ints_overlap = np.interp(rts_is, rts, ints, 0, 0) * fs_nl[j][i]
                    ints_is_overlap = (
                        np.interp(rts, rts_is, ints_is, 0, 0) * fs_is[i][j]
                    )
                    area_is_o = np.trapezoid(ints_is_overlap, rts)
                    area_nl_o = np.trapezoid(ints_overlap, rts_is)
                else:
                    area_is_o = area_nl_o = 0
                # we determine corrected overlapping fractions
                f_is = area_is_o / model_is.area if model_is.area else 0
                # f_is = fs_is[i][j] * fx
                dx = len(models_is)
                # since area_nl_o is a fraction of models[j].area
                f_nl = area_nl_o / models[j].area if models[j].area else 0
                # f_nl = fs_nl[j][i] * fx
                mat[i][i] = 1
                mat[dx + j][dx + j] = 1
                mat[i][dx + j] = f_is
                mat[j + dx][i] = f_nl
        areas_corr = solve(mat, res_vec)
        return areas_corr[:no_is], areas_corr[no_is:]
    return np.array([None] * no_is).reshape(-1, 1), np.array([None] * no_nl).reshape(
        -1, 1
    )


def _result_vec(models, models_is):
    no_eq = len(models) + len(models_is)
    res = np.zeros((no_eq)).reshape(-1, 1)
    for i, model_is in enumerate(models_is):
        res[i] = model_is.area
    for j, model in enumerate(models):
        res[len(models_is) + j] = model.area
    return res


def _check_model(model):
    if model is not None:
        return model.area is not None
    return model is not None


################################################


def _update_isotopologue_correction(t, pair2area_corr, filename_col):
    if not "original_area_chromatogram" in t.col_names:
        t.rename_columns(area_chromatogram="original_area_chromatogram")
        t.set_col_format("original_area_chromatogram", None)
    t.add_or_replace_column(
        "area_chromatogram",
        t.apply(
            _get_tuple_key, pair2area_corr, t[filename_col], t.id, ignore_nones=False
        ),
        float,
        format_="%.2e",
        insert_before="original_area_chromatogram",
    )
    t.add_or_replace_column(
        "isotopologue_overlay_correction",
        t.area_chromatogram.is_not_none().then_else(True, False),
        bool,
        insert_after="area_chromatogram",
    )
    t.replace_column(
        "area_chromatogram",
        t.area_chromatogram.if_not_none_else(t.original_area_chromatogram),
        float,
        format_="%.2e",
    )
