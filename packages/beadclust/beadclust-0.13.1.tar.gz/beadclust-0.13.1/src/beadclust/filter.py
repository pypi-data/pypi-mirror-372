from __future__ import annotations

import logging
from dataclasses import dataclass, field
from timeit import default_timer as timer
from typing import Any, Optional, TYPE_CHECKING

import numpy as np
import pandas as pd
import seaflowpy as sfp
from scipy.signal import find_peaks

from beadclust.errors import BeadFinderError
from beadclust.particleops import log_particles, unlog_particles

# Avoid circular import
if TYPE_CHECKING:
    from beadclust.cluster import ClusterConfig


logger = logging.getLogger(__name__)


@dataclass
class FilterResults:
    evt_ali: Optional[np.ndarray] = field(default=None)
    evt_cut_min: Optional[np.ndarray] = field(default=None)
    evt_cut_pechl: Optional[np.ndarray] = field(default=None)
    evt_cut_peaks: Optional[np.ndarray] = field(default=None)
    opp: Optional[np.ndarray] = field(default=None)
    opp_cut_min: Optional[np.ndarray] = field(default=None)
    opp_cut_pechl: Optional[np.ndarray] = field(default=None)
    opp_cut_peaks: Optional[np.ndarray] = field(default=None)
    peaks: dict[str, Any] = field(default_factory=dict)
    selected_peak: Optional[int] = field(default=None)
    counts: dict[str, int] = field(default_factory=dict)
    elapsed_total: float = field(default=0.0)
    elapsed_peak: float = field(default=0.0)


def pipeline(evt: pd.DataFrame, conf: ClusterConfig) -> FilterResults:
    t0 = timer()
    particle_counts = {
        "evt": len(evt),
        "evt_ali": 0,
        "opp": 0,
        "opp_min_val": 0,
        "opp_pe_chl": 0,
        "opp_peak": 0,
        "evt_min_val": 0,
        "evt_pe_chl": 0,
        "evt_peak": 0,
    }
    evt = evt.reset_index(drop=True)

    evt_ali = align(evt, conf.filtering_width, origin_align=conf.origin_align)
    particle_counts["evt_ali"] = evt_ali.sum()
    logger.debug("%d events after alignment", evt_ali.sum())

    if (conf.filter_params_by_date is None) or len(conf.filter_params_by_date) == 0:
        logger.debug("Using rough filter to create OPP")
        try:
            opp = roughfilter(evt, aligned=evt_ali, width=conf.filtering_width, origin_align=conf.origin_align)
        except BeadFinderError as e:
            opp = np.zeros(len(evt), dtype=bool)
            logger.warning(f"no OPP, {e}")

    else:
        logger.debug("Using supplied filter parameters to create OPP")
        assert len(conf.filter_params_by_date) == 3
        fp = conf.filter_params_by_date.copy().reset_index(drop=True)
        fp["width"] = conf.filtering_width
        mark = mark_focused(evt, fp, aligned=evt_ali, origin_align=conf.origin_align)
        opp = mark["q2.5"].to_numpy()
    particle_counts["opp"] = opp.sum()
    logger.debug("%d OPP events", opp.sum())

    # Min value filter
    opp_cut_min = apply_min_cutoffs(evt, opp, conf.min_pe, conf.min_fsc, conf.min_chl)
    evt_cut_min = apply_min_cutoffs(evt, evt_ali, conf.min_pe, conf.min_fsc, conf.min_chl)
    particle_counts["opp_min_val"] = opp_cut_min.sum()
    particle_counts["evt_min_val"] = evt_cut_min.sum()
    logger.debug(
        "%d opp events after min_pe:min_fsc %d:%d cutoff applied", opp_cut_min.sum(), conf.min_pe, conf.min_fsc
    )
    logger.debug(
        "%d evt events after min_pe:min_fsc %d:%d cutoff applied", evt_cut_min.sum(), conf.min_pe, conf.min_fsc
    )

    # Apply PE/CHL croco cutoff
    evt_all_cut_pechl = (evt["pe"].to_numpy() / evt["chl_small"].to_numpy()) >= conf.pe_chl_cutoff
    opp_cut_pechl = opp_cut_min & evt_all_cut_pechl
    evt_cut_pechl = evt_cut_min & evt_all_cut_pechl
    particle_counts["opp_pe_chl"] = opp_cut_pechl.sum()
    particle_counts["evt_pe_chl"] = evt_cut_pechl.sum()
    logger.debug("%d opp events after applying pe/chl >= %.02f", opp_cut_pechl.sum(), conf.pe_chl_cutoff)
    logger.debug("%d evt events after applying pe/chl >= %.02f", evt_cut_pechl.sum(), conf.pe_chl_cutoff)

    # Bead peak filter to exclude sticky bead doublet/triplet/etc clusters and
    # to exclude any synecho particles
    # Create OPP and EVT dataframes selected for particles for each PE peak found
    t1 = timer()
    peaks = find_bead_peaks(evt[opp_cut_pechl], col="pe", **conf.peak_finder_params)
    if "found" in peaks:
        logger.debug("%d peaks found", len(peaks["found"]))
    selected_peak = pick_peak(peaks, **conf.peak_picker_params)
    if selected_peak is not None:
        p = peaks["found"].iloc[selected_peak]
        logger.debug(
            "chose primary peak at pe=%.02f, pe/chl=%.02f",
            p["pe_med"],
            p["pe_chl_ratio_linear"],
        )
        # Remove all data below double this peek and see if any new peaks
        # get picked up with better pe/chl ratio. If there are bead doublet
        # and triplets, etc any new peaks detected will have the same pe/chl
        # ratio. If this is a syn peak, then beads should be the next peak
        # detected.
        # opp2 = opp_cut_pechl & (evt["pe"] > p["double"])
        opp2 = opp_cut_pechl & (evt["pe"] > (p["pe_med"] + 15000))
        peaks2 = find_bead_peaks(evt[opp2], col="pe", **conf.peak_finder_params)
        if "found" in peaks2:
            logger.debug("%d peaks found after removing first selected peak", len(peaks["found"]))
        selected_peak2 = pick_peak(peaks2, **conf.peak_picker_params)
        if selected_peak2 is not None:
            p2 = peaks2["found"].iloc[selected_peak2]
            logger.debug(
                "chose secondary peak at pe=%.02f, pe/chl=%.02f",
                p2["pe_med"],
                p2["pe_chl_ratio_linear"],
            )
            # If old peak pe/chl is not equal to new peak (with 20% tolerance)
            # choose new peak
            # TODO: lift his magic number to constant and/or func param default
            if p["pe_chl_ratio_linear"] < ((1 - conf.peak_picker_params["pe_chl_tol"]) * p2["pe_chl_ratio_linear"]):
                p = p2
                peaks = peaks2
                selected_peak = selected_peak2
                logger.debug("secondary peak has significantly higher pe/chl, will be used")

        opp_cut_peaks = opp_cut_pechl & (evt["pe"].values >= p["low_cutoff"])
        opp_cut_peaks = opp_cut_peaks & (evt["pe"].values <= p["high_cutoff"])
        evt_cut_peaks = evt_cut_pechl & (evt["pe"].values >= p["low_cutoff"])
        evt_cut_peaks = evt_cut_peaks & (evt["pe"].values <= p["high_cutoff"])
    else:
        logger.debug("no PE peaks found")
        # Still put dataframes in *_cut_peaks even if there are no peaks
        opp_cut_peaks = opp_cut_pechl
        evt_cut_peaks = evt_cut_pechl
    t2 = timer()

    particle_counts["opp_peak"] = opp_cut_peaks.sum()
    particle_counts["evt_peak"] = evt_cut_peaks.sum()
    logger.debug("%s opp events after bead peak filter applied", particle_counts["opp_peak"])
    logger.debug("%s evt events after bead peak filter applied", particle_counts["evt_peak"])

    res = FilterResults(
        evt_ali=evt_ali,
        evt_cut_min=evt_cut_min,
        evt_cut_pechl=evt_cut_pechl,
        evt_cut_peaks=evt_cut_peaks,
        opp=opp,
        opp_cut_min=opp_cut_min,
        opp_cut_pechl=opp_cut_pechl,
        opp_cut_peaks=opp_cut_peaks,
        peaks=peaks,
        selected_peak=selected_peak,
        counts=particle_counts,
        elapsed_total = t2 - t0,
        elapsed_peak = t2 - t1
    )
    return res


def align(df: pd.DataFrame, width: float | int, origin_align: bool=True) -> np.ndarray:
    # Return boolean selection for aligned, non-noise, non-saturated particles
    # Aligned particles (D1 = D2), with correction for D1 D2 sensitivity
    # difference.
    noise = sfp.particleops.mark_noise(df)
    sat = sfp.particleops.mark_saturated(df) # D1 and D2 saturation
    sat_fsc = df["fsc_small"].to_numpy() == df["fsc_small"].max()
    if origin_align:
        origin = np.median(df["D2"].to_numpy() - df["D1"].to_numpy())
    else:
        origin = 0
    # Filter aligned particles (D1 = D2), with correction for D1 D2
    # sensitivity difference.
    alignedD1 = (df["D1"].to_numpy() + origin) < (df["D2"].to_numpy() + width)
    alignedD2 = df["D2"].to_numpy() < (df["D1"].to_numpy() + origin + width)
    aligned = (~noise) & (~sat) & (~sat_fsc) & alignedD1 & alignedD2
    return aligned


def apply_min_cutoffs(df, prev_sel, min_pe, min_fsc, min_chl):
    if prev_sel is not None:
        min_indexer = prev_sel
    else:
        min_indexer = np.full(len(df.index), True)
    if min_pe:
        min_indexer = min_indexer & (df["pe"].values >= min_pe)
    if min_fsc:
        min_indexer = min_indexer & (df["fsc_small"].values >= min_fsc)
    if min_chl:
        min_indexer = min_indexer & (df["chl_small"].values >= min_chl)
    return min_indexer


def mark_focused(
        df: pd.DataFrame,
        params: pd.DataFrame,
        aligned: np.ndarray | pd.Series | None=None,
        origin_align: bool=True):
    # Check parameters
    param_keys = [
        "width",
        "notch_small_D1",
        "notch_small_D2",
        "notch_large_D1",
        "notch_large_D2",
        "offset_small_D1",
        "offset_small_D2",
        "offset_large_D1",
        "offset_large_D2",
        "quantile",
    ]
    if params is None:
        raise ValueError("Must provide filtering parameters")
    for k in param_keys:
        if not k in params.columns:
            raise ValueError(f"Missing filter parameter {k} in mark_focused")
    assert len(params["width"].unique()) == 1  # may as well check
    # Make sure params have 0-based indexing
    params = params.reset_index(drop=True)

    mark = pd.DataFrame()
    if aligned is None:
        # Apply noise, saturation, alignment filter
        aligned = align(df, params.loc[0, "width"], origin_align=origin_align)
        logger.debug("%d EVT events after alignment", np.sum(aligned))

    for q in params["quantile"].sort_values():
        p = params[params["quantile"] == q].iloc[0]  # get first row of dataframe as series
        # Filter focused particles
        # Using underlying numpy arrays (values) to construct boolean
        # selector is about 10% faster than using pandas Series
        small_D1 = df["D1"].to_numpy() <= (
            (df["fsc_small"].to_numpy() * p["notch_small_D1"]) + p["offset_small_D1"]
        )
        small_D2 = df["D2"].to_numpy() <= (
            (df["fsc_small"].to_numpy() * p["notch_small_D2"]) + p["offset_small_D2"]
        )
        large_D1 = df["D1"].to_numpy() <= (
            (df["fsc_small"].to_numpy() * p["notch_large_D1"]) + p["offset_large_D1"]
        )
        large_D2 = df["D2"].to_numpy() <= (
            (df["fsc_small"].to_numpy() * p["notch_large_D2"]) + p["offset_large_D2"]
        )
        opp_selector = aligned & ((small_D1 & small_D2) | (large_D1 & large_D2))
        # Mark focused particles
        colname = f"q{sfp.util.quantile_str(q)}"
        mark[colname] = opp_selector

    mark.set_index(df.index.copy())  # match the index of df

    return mark


def roughfilter(
        df: pd.DataFrame,
        aligned: np.ndarray | pd.Series | None=None,
        width: float | int=5000,
        origin_align: bool=True) -> np.ndarray:
    if width is None:
        raise ValueError("Must supply width to roughfilter")
    # Prevent potential integer division bugs
    width = float(width)

    if len(df) == 0:
        return np.zeros(0, dtype=bool)

    if aligned is None:
        # Apply noise, saturation, alignment filter
        aligned = align(df, width, origin_align=origin_align)
        logger.debug("%d EVT events after alignment", aligned.sum())

    # Find fsc/d ratio (slope) for best large fsc particle
    fsc_small_max = df.loc[aligned, "fsc_small"].max()
    fsc_small_max_idx = (
        aligned &
        (df["fsc_small"].to_numpy() == fsc_small_max) &
        (df["D1"] > 0) &
        (df["D2"] > 0)
    )
    if fsc_small_max_idx.sum() == 0:
        raise BeadFinderError("no fsc_small.max() particles with D1 and D2 > 0")

    # Smallest D1 with maximum fsc_small
    min_d1 = df.loc[fsc_small_max_idx, "D1"].min()
    slope_d1 = fsc_small_max / min_d1
    # Smallest D2 with maximum fsc_small
    min_d2 = df.loc[fsc_small_max_idx, "D2"].min()
    slope_d2 = fsc_small_max / min_d2

    # Filter focused particles
    # Better fsc/d signal than best large fsc particle
    # oppD1 = (aligned_df["fsc_small"].to_numpy() / aligned_df["D1"].to_numpy()) >= slope_d1
    # oppD2 = (aligned_df["fsc_small"].to_numpy() / aligned_df["D2"].to_numpy()) >= slope_d2
    # Do this instead of avoid divide by zero
    oppD1 = df["fsc_small"].to_numpy() >= (df["D1"].to_numpy() * slope_d1)
    oppD2 = df["fsc_small"].to_numpy() >= (df["D2"].to_numpy() * slope_d2)
    return (aligned & oppD1 & oppD2)


def find_bead_peaks(
    df: pd.DataFrame,
    col: str="pe",
    bin_size: int=250,
    ma_window_size: int=8,
    peak_width: Optional[int]=None,
    peak_height: int=5,
    peak_height_frac_max: float=0.8,
    cutoff_scalar: float=0.4,
) -> dict[str, Any]:

    if peak_width is None:
        peak_width = [2, 30]
    s = df[col]
    if s.empty:
        return {}
    bins = int((s.max() - s.min()) / bin_size) + 1
    hist = s.groupby(pd.cut(s.to_numpy(), bins), observed=False).size()
    bin_labels = hist.index.to_numpy()
    bin_bounds = pd.DataFrame(
        {"left": [x.left for x in bin_labels], "right": [x.right for x in bin_labels]}
    )
    bin_mids = bin_bounds.mean(axis=1)
    hist = hist.reset_index(drop=True)
    # Set NaN to 0 as find_peaks warns about including NaN
    hist_ma = hist.rolling(ma_window_size, center=True).mean().fillna(0)
    # Start return dictionary
    r = {
        "counts": hist.to_numpy(),
        "counts_ma": hist_ma.to_numpy(),
        "bin_midpoints": bin_mids,
        "bin_intervals": bin_labels,
        "bin_size": bin_size
    }
    height = max(peak_height, hist_ma.max() * peak_height_frac_max)
    peaks, properties = find_peaks(hist_ma.values, height=height, width=peak_width)

    found = []
    for i, peak_bin in enumerate(peaks):
        f = {
            "idx": peak_bin,
            "location": bin_mids[peak_bin],
            "high_cutoff": log_particles(unlog_particles(bin_mids[peak_bin]) * (1 + cutoff_scalar)),
            "low_cutoff": log_particles(unlog_particles(bin_mids[peak_bin]) * (1 - cutoff_scalar)),
            "double": log_particles(unlog_particles(bin_mids[peak_bin]) * 2),
            "half": log_particles(unlog_particles(bin_mids[peak_bin]) / 2),
            "prominence": properties["prominences"][i],
            "height": properties["peak_heights"][i],
            "width": properties["widths"][i]
        }
        lwr = f["location"] - (bin_size * f["width"] / 2)
        upr = f["location"] + (bin_size * f["width"] / 2)
        peak_df = df[(df["pe"] >= lwr) & (df["pe"] <= upr)]
        f["pe_chl_ratio_linear"] = (unlog_particles(peak_df["pe"]) / unlog_particles(peak_df["chl_small"])).median()
        f["fsc_small_med"] = peak_df["fsc_small"].median()
        f["pe_med"] = peak_df["pe"].median()
        f["chl_small_med"] = peak_df["chl_small"].median()
        found.append(f)
    if found:
        r["found"] = pd.DataFrame(found).sort_values("location").reset_index(drop=True)
    else:
        r["found"] = pd.DataFrame()

    return r


def pick_peak(
    peaks: dict[str, Any],
    pe_chl_tol: float=0.25,
    height_tol: float=0.5
) -> int | None:
    """
    Pick the likely bead peak.

    Select peaks within 100% * pe_chl_tol of the max peak pe/chl, and from that
    group keep peaks within 100% * height_tol of the tallest peak in the group.
    Then choose the lowest peak.

    If peaks is None or empty, or if no peaks are chosen, return None.
    """
    if (not peaks) or peaks["found"].empty:
        return None
    found = peaks["found"]
    logger.debug("peak linear pe/chl ratios are %s", found["pe_chl_ratio_linear"].to_list())
    logger.debug("peak heights are are %s", found["height"].to_list())
    pe_chl_cutoff = found["pe_chl_ratio_linear"].max() * (1 - pe_chl_tol)
    pe_chl_select = found["pe_chl_ratio_linear"] >= pe_chl_cutoff
    height_cutoff = found[pe_chl_select]["height"].max() * (1 - height_tol)
    height_select = found["height"] >= height_cutoff
    likely_beads = np.flatnonzero(pe_chl_select & height_select)
    if len(likely_beads) > 0:
        logger.debug("likely bead peaks are %s", likely_beads)
        # Return first (lowest) "likely bead" peak
        logger.debug("chosen peak is %s", likely_beads[0])
        return likely_beads[0]
    return None
