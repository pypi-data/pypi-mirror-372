import copy
import logging
# import multiprocessing as mp

from dataclasses import dataclass, field
from functools import cached_property
# from time import sleep
from timeit import default_timer as timer
from typing import cast, Any, Optional

import hdbscan
import matplotlib.path
import numpy as np
import numpy.typing as npt
import pandas as pd
from joblib import Parallel, delayed
from scipy.spatial import ConvexHull

from beadclust import filter
from beadclust import filter_params
from beadclust.errors import BeadFinderError
from beadclust.io import get_filter_calibration_slopes
from beadclust.particleops import unlog_particles

logger = logging.getLogger(__name__)


def make_default_filter_params_by_date_dataframe() -> pd.DataFrame:
    return filter_params.make_empty_dataframe().set_index("date")


def make_default_timestamp() -> pd.Timestamp:
    return pd.Timestamp.now()


def make_default_summary_dataframe() -> pd.DataFrame:
    df = pd.DataFrame(
        columns=[
            "fsc_small_pe_count",
            "fsc_small_range",
            "fsc_small_std",
            "fsc_small_1Q",
            "fsc_small_2Q",
            "fsc_small_3Q",
            "fsc_small_IQR",
            "pe_range",
            "pe_std",
            "pe_1Q",
            "pe_2Q",
            "pe_3Q",
            "pe_IQR",
            "peak_count",
            "peak_idx",
            "peak_pe_location",
            "peak_prominence",
            "peak_height",
            "peak_width",
            "peak_pe_chl_ratio_linear",
            "peak_fsc_small_med",
            "peak_pe_med",
            "peak_chl_small_med",
            "chl_small_range",
            "chl_small_std",
            "chl_small_1Q",
            "chl_small_2Q",
            "chl_small_3Q",
            "chl_small_IQR",
            "D1_count",
            "D1_range",
            "D1_std",
            "D1_1Q",
            "D1_2Q",
            "D1_3Q",
            "D1_IQR",
            "D2_count",
            "D2_range",
            "D2_std",
            "D2_1Q",
            "D2_2Q",
            "D2_3Q",
            "D2_IQR",
            "evt_count",
            "evt_min_val_count",
            "evt_pe_chl_count",
            "evt_peak_count",
            "opp_count",
            "opp_min_val_count",
            "opp_pe_chl_count",
            "opp_peak_count",
            "fsc_pe_cluster_count",
            "fsc_d1_cluster_count",
            "fsc_d2_cluster_count",
            "elapsed_filter",
            "elapsed_peak",
            "elapsed_cluster",
            "elapsed_total",
            "date",
        ],
        dtype=float,
    )
    df["date"] = pd.to_datetime(df["date"], utc=True)
    return df


@dataclass
class ClusterConfig:
    """Configuration for bead finding

    Attributes
    ----------
    name :
        Cruise name.
    serial :
        SeaFlow instrument serial number to use for calibrated filtering slopes
        lookup.
    time_res :
        Pandas time window alias used to bin EVT data, e.g. 1H for 1 hour.
    min_fsc :
        ``fsc_small`` minimum cutoff to use when identifying beads clusters.
    min_pe :
        ``pe`` minimum cutoff to use when identifying beads clusters.
    min_chl :
        ``chl`` minimum cutoff to use when identifying beads clusters.
    pe_chl_cutoff :
        ``pe`` to ``chl_small`` ratio below which particles will be removed.
        Used to broadly discriminate beads from crocosphaera.
    peak_finder_params :
        Keyword arguments to find_bead_peaks(), to find the first bead peak
        in OPP PE data in original log form.
    min_cluster_frac :
        Minimum fraction of points passed to HDBSCAN that should be in the
        cluster.
    filtering_width :
        Tolerance for alignment equality between D1 and D2.
    origin_align :
        Adjust for difference in sensitivity between D1 and D2 by median
        difference when selecting aligned particles.
    filter_params_by_date :
        Filtering parameters indexed by time bin timestamp. Will be used to
        filter EVT data using `filter.mark_focused` rather than
        `filter.roughfilter`.
    spread_cutoff :
        Cutoff for the `fsc_small` cluster range that identifies "good"
        cluster results.
    cluster_log :
        Cluster with raw log SeaFlow data. Otherwise cluster unlogged data.

    Properties:
    ----------
    instrument_slopes :
        SeaFlow instrument-calibrated filtering slopes for the instrument
        identified by `serial`. File reads are cached.
    """

    name: str = field(default="")
    serial: str = field(default="")
    time_res: str = field(default="1H")
    min_fsc: float = field(default=32000)
    min_pe: float = field(default=38000)
    min_chl: float = field(default=25000)
    pe_chl_cutoff: float = field(default=0.9)
    peak_finder_params: dict[str, Any] = field(default_factory=dict)
    max_cluster_input: int = field(default=5000)
    min_cluster_frac: float = field(default=0.33)
    filtering_width: float = field(default=10000)
    origin_align: bool = field(default=True)
    filter_params_by_date: pd.DataFrame = field(default_factory=make_default_filter_params_by_date_dataframe)
    db_filter_params: pd.DataFrame = field(default_factory=pd.DataFrame)
    spread_cutoff: float = field(default=300)
    cluster_log: bool = field(default=True)

    @cached_property
    def instrument_slopes(self) -> pd.Series:
        try:
            slopes = get_filter_calibration_slopes(self.serial)
        except ValueError as e:
            logger.warning(e)
            slopes = pd.Series([])
        return slopes


@dataclass
class ClusterResult:
    """Bead finding results for one time bin"""

    conf: ClusterConfig
    date: pd.Timestamp = field(default_factory=make_default_timestamp)
    error_message: str = ""
    filter_results: filter.FilterResults = field(default_factory=filter.FilterResults)
    summary: pd.DataFrame = field(default_factory=make_default_summary_dataframe)
    cluster_centers: dict[str, Optional[tuple[int, int]]] = field(default_factory=dict)
    dfs: dict[str, pd.DataFrame] = field(default_factory=dict)
    derived_filter_params: pd.DataFrame = field(default_factory=filter_params.make_empty_dataframe)
    elapsed_total: float = field(default=0.0)
    elapsed_cluster: float = field(default=0.0)


class ClusterResultCollection(dict[pd.Timestamp, ClusterResult]):
    """Collection of related bead finding results"""
    def __init__(self, *args, **kwargs):
        self.conf = kwargs.pop("conf", None)
        super().__init__(*args, **kwargs)

    def as_list(self) -> list[ClusterResult]:
        return sorted(self.values(), key=lambda d: d.date)

    def summary(self) -> pd.DataFrame:
        return pd.concat([r.summary for r in self.as_list()], ignore_index=True).set_index("date")

    def filter_params(self, spread_cutoff: float = 3000) -> pd.DataFrame:
        fp = pd.concat(
            [r.derived_filter_params for r in self.as_list()],
            ignore_index=True
        ).set_index("date")
        closest_good = self._closest_good_bead_coords(spread_cutoff=spread_cutoff)
        if closest_good["closest_good_index"].isna().any():
            raise ValueError("no good bead locations available for filter parameters")
        # Add filter params for unsuccessful time points by using params from the
        # closest time point with good params
        fp_by_date = fp.copy()
        # Put date in its own column to track which date the filter params came from
        fp_by_date["source_filter_params_date"] = fp_by_date.index.to_numpy()
        # Create dataframe of filter params for closest good bead location for each
        # date
        fp_by_date = fp_by_date.loc[closest_good["closest_good_index"]]
        # Set the date index to the original dates, replacing the dates of the original filter_params_df
        # Must repeat each date three times for the three filtering quantiles
        # This can now be used to get the correct filter parameters for each date
        fp_by_date.set_index(np.repeat(closest_good.index.to_numpy(), 3), inplace=True)

        return fp_by_date

    def _closest_good_bead_coords(self, spread_cutoff: float = 3000) -> pd.DataFrame:
        coords = self.summary()
        good_idx = (
            (~coords["peak_pe_location"].isna())
            & (~coords["fsc_small_2Q"].isna())
            & (~coords["D1_2Q"].isna())
            & (~coords["D2_2Q"].isna())
            & (coords["fsc_small_range"] <= spread_cutoff)
        )
        coords["good"] = False
        coords.loc[good_idx, "good"] = True

        last_good = pd.NaT
        prev_good_list = []
        next_good_list = []
        # Find closest good entry going forward (prev) and backward (next) in the
        # dataframe
        for index, good in coords["good"].items():
            if good:
                last_good = index
            prev_good_list.append(last_good)
        last_good = pd.NaT
        for index, good in coords["good"][::-1].items():
            if good:
                last_good = index
            next_good_list.append(last_good)
        coords["prev_good"] = pd.to_datetime(prev_good_list, utc=True)
        coords["next_good"] = pd.to_datetime(next_good_list[::-1], utc=True)
        coords["dist_to_prev_good"] = pd.NA
        coords["dist_to_next_good"] = pd.NA
        if coords["prev_good"].notna().sum():
            idx = coords["prev_good"].notna()
            dist_to_prev_good = coords.loc[idx, "prev_good"] - coords.loc[idx].index
            coords.loc[idx, "dist_to_prev_good"] = dist_to_prev_good
        if coords["next_good"].notna().sum():
            idx = coords["next_good"].notna()
            dist_to_next_good = coords.loc[idx, "next_good"] - coords.loc[idx].index
            coords.loc[idx, "dist_to_next_good"] = dist_to_next_good
        closest_offset_list = []
        for index, row in coords.iterrows():
            if pd.isna(row["dist_to_next_good"]):
                closest_offset_list.append(row["dist_to_prev_good"])
            elif pd.isna(row["dist_to_prev_good"]):
                closest_offset_list.append(row["dist_to_next_good"])
            elif np.abs(row["dist_to_next_good"]) < np.abs(row["dist_to_prev_good"]):
                closest_offset_list.append(row["dist_to_next_good"])
            else:
                closest_offset_list.append(row["dist_to_prev_good"])
        coords["closest_good_offset"] = closest_offset_list
        coords["closest_good_index"] = pd.NaT
        coords["closest_good_index"] = pd.to_datetime(coords["closest_good_index"], utc=True)
        idx = coords["closest_good_offset"].notna()
        if idx.sum():
            coords.loc[idx, "closest_good_index"] = coords.loc[idx].index.to_series() + coords.loc[idx, "closest_good_offset"]
        return coords


def cluster_cruise(
    df: pd.DataFrame, conf: ClusterConfig, max_workers: Optional[int] = 1
) -> ClusterResultCollection:
    # Only keep relevant columns
    df = df[["date", "D1", "D2", "fsc_small", "pe", "chl_small"]]
    grouped = df.groupby(df["date"].dt.floor(conf.time_res))
    logger.info("%d %s groups total", len(grouped), conf.time_res)

    results: ClusterResultCollection = ClusterResultCollection(conf=conf)

    # Construct args for each time point to find beads in
    job_args = []
    for group_key, group in grouped:
        group_key = cast(pd.Timestamp, group_key)
        group_df = group.reset_index(drop=True)
        # Add group specific filtering parameters if available
        if not conf.filter_params_by_date.empty:
            fp = conf.filter_params_by_date.loc[group_key]
            assert isinstance(fp, pd.DataFrame)
        else:
            fp = None
        subconf = copy.copy(conf)
        subconf.filter_params_by_date = fp
        job_args.append((group_df, subconf, group_key))

    # Find beads in all time points
    parallel = Parallel(n_jobs=max_workers, backend="multiprocessing")
    for clustres in parallel(delayed(find_beads)(*a) for a in job_args):
        if clustres.error_message:
            logger.warning("%s: %s", clustres.date, clustres.error_message)
        results[clustres.date] = clustres
        logger.info("%s complete", clustres.date)

    # if max_workers == 1:
    #     mapgen = map(
    #         find_beads,
    #         (a[0] for a in job_args),
    #         (a[1] for a in job_args),
    #         (a[2] for a in job_args)
    #     )
    #     for clustres in mapgen:
    #         if clustres.error_message:
    #             logger.warning("%s: %s", clustres.date, clustres.error_message)
    #         results[clustres.date] = clustres
    # else:
    #     with mp.get_context("spawn").Pool(processes=max_workers) as pool:
    #         futures = []
    #         received = {}
    #         for args in job_args:
    #             futures.append(pool.apply_async(find_beads, args))
    #         while len(results) < len(futures):
    #             for i, fut in enumerate(futures):
    #                 if i not in received:
    #                     clustres = fut.get()
    #                     received[i] = True
    #                     if clustres.error_message:
    #                         logger.warning("%s: %s", clustres.date, clustres.error_message)
    #                     results[clustres.date] = clustres
    #             sleep(0.1)

    return results


def find_beads(
    evt: pd.DataFrame,
    conf: ClusterConfig,
    date: Optional[pd.Timestamp] = None
) -> ClusterResult:
    """
    Find bead coordinates with DBSCAN clustering.

    Raises
    ------
    BeadFinderError
    """
    t0 = timer()
    logger.info("starting find_beads for %s", date)
    q_levels = [0.25, 0.5, 0.75]

    filt_res = filter.pipeline(evt, conf)
    peaks = filt_res.peaks
    particle_counts = filt_res.counts

    # Message for first error encountered during clustering, and our signal for
    # success. Any errors should populate this string.
    err_msg = ""

    t1 = timer()

    # Always cluster fsc/pe, even if there's no peak
    # Limiting input to HDBSCAN clustering has the largest impact on
    # processing time
    evt = evt[filt_res.evt_cut_peaks].sample(
        n=min(conf.max_cluster_input, filt_res.evt_cut_peaks.sum()),
        random_state=12345
    )

    # ----------------------------
    # Find initial fsc vs pe beads
    # ----------------------------
    logger.debug("clustering FSC/PE for %s, with selected_peak = %s", date, filt_res.selected_peak)
    columns = ["fsc_small", "pe"]
    fsc_pe_cluster_hull_points = pd.DataFrame(dtype="float64")
    fsc_pe_cluster_points = pd.DataFrame(dtype="float64")
    fsc_pe_cluster_center = None
    pe_df = pd.DataFrame(columns=evt.columns, dtype="float64")
    fsc_q = np.full(len(q_levels), np.nan)
    pe_q = np.full(len(q_levels), np.nan)
    chl_q = np.full(len(q_levels), np.nan)
    fsc_range = None
    pe_range = None
    chl_range = None
    fsc_std = None
    pe_std = None
    chl_std = None
    try:
        if conf.cluster_log:
            cluster_idx = cluster(evt[columns].to_numpy(), min_cluster_frac=conf.min_cluster_frac)
        else:
            cluster_idx = cluster(
                evt[columns].apply(unlog_particles).to_numpy(),
                min_cluster_frac=conf.min_cluster_frac
            )
        if len(cluster_idx) == 0:
            err_msg = "could not find points for FSC/PE cluster"
        else:
            fsc_pe_cluster_points = evt.iloc[cluster_idx, :].reset_index(drop=True)
            fsc_pe_cluster_center = (
                int(fsc_pe_cluster_points["fsc_small"].median()),
                int(fsc_pe_cluster_points["pe"].median())
            )
    except BeadFinderError as e:
        err_msg = str(e)

    if not err_msg:
        pe_df = fsc_pe_cluster_points
        fsc_q = quantiles(pe_df["fsc_small"].to_numpy(), q_levels)
        pe_q = quantiles(pe_df["pe"].to_numpy(), q_levels)
        chl_q = quantiles(pe_df["chl_small"].to_numpy(), q_levels)
        fsc_range = pe_df["fsc_small"].max() - pe_df["fsc_small"].min()
        pe_range = (pe_df["pe"].max() - pe_df["pe"].min(),)
        chl_range = (pe_df["chl_small"].max() - pe_df["chl_small"].min(),)
        fsc_std = pe_df["fsc_small"].std()
        pe_std = pe_df["pe"].std()
        chl_std = pe_df["chl_small"].std()
    else:
        # Something went wrong clustering this peak, try next
        logger.warning("FSC/PE clustering failed: %s", err_msg)

    # ------------------------------------------
    # Find fsc vs D1 beads as subset of pe beads
    # ------------------------------------------
    columns = ["fsc_small", "D1"]
    fsc_d1_cluster_points = pd.DataFrame(dtype="float64")
    fsc_d1_cluster_center = None
    d1_df = pd.DataFrame(columns=evt.columns, dtype="float64")
    d1_q = np.full(len(q_levels), np.nan)
    d1_range = None
    d1_std = None
    if not err_msg:
        logger.debug("clustering FSC/D1 for %s", date)
        try:
            if conf.cluster_log:
                cluster_idx = cluster(pe_df[columns].to_numpy(), min_cluster_frac=conf.min_cluster_frac)
            else:
                cluster_idx = cluster(
                    pe_df[columns].apply(unlog_particles).to_numpy(),
                    min_cluster_frac=conf.min_cluster_frac
                )
            fsc_d1_cluster_points = pe_df.iloc[cluster_idx, :].reset_index(drop=True)
            fsc_d1_cluster_center = (
                int(fsc_d1_cluster_points["fsc_small"].median()),
                int(fsc_d1_cluster_points["D1"].median())
            )
        except BeadFinderError as e:
            err_msg = str(e)
            logger.warning(err_msg)
        else:
            # Just the fsc D1 cluster points
            d1_df = fsc_d1_cluster_points
            if d1_df.empty:
                err_msg = "could not find points for FSC/D1 cluster"
                logger.warning(err_msg)
            else:
                d1_q = quantiles(d1_df["D1"].to_numpy(), q_levels)
                d1_range = d1_df["D1"].max() - d1_df["D1"].min()
                d1_std = d1_df["D1"].std()

    # ------------------------------------------
    # Find fsc vs D2 beads as subset of pe beads
    # ------------------------------------------
    columns = ["fsc_small", "D2"]
    fsc_d2_cluster_points = pd.DataFrame(dtype="float64")
    fsc_d2_cluster_center = None
    d2_df = pd.DataFrame(columns=evt.columns, dtype="float64")
    d2_q = np.full(len(q_levels), np.nan)
    d2_range = None
    d2_std = None
    if not err_msg:
        logger.debug("clustering FSC/D2 for %s", date)
        try:
            if conf.cluster_log:
                cluster_idx = cluster(pe_df[columns].to_numpy(), min_cluster_frac=conf.min_cluster_frac)
            else:
                cluster_idx = cluster(
                    pe_df[columns].apply(unlog_particles).to_numpy(),
                    min_cluster_frac=conf.min_cluster_frac
                )
            fsc_d2_cluster_points = pe_df.iloc[cluster_idx, :].reset_index(drop=True)
            fsc_d2_cluster_center = (
                int(fsc_d2_cluster_points["fsc_small"].median()),
                int(fsc_d2_cluster_points["D2"].median())
            )
        except BeadFinderError as e:
            err_msg = str(e)
            logger.warning(err_msg)
        else:
            # Just the fsc D2 cluster points
            d2_df = fsc_d2_cluster_points
            if d2_df.empty:
                err_msg = "could not find points for FSC/D2 cluster"
                logger.warning(err_msg)
            else:
                d2_q = quantiles(d2_df["D2"].to_numpy(), q_levels)
                d2_range = d2_df["D2"].max() - d2_df["D2"].min()
                d2_std = d2_df["D2"].std()

    t2 = timer()

    if peaks and (not peaks["found"].empty) and filt_res.selected_peak is not None:
        peak_pe_location = peaks["found"].iloc[filt_res.selected_peak]["location"]
        peak_prom = peaks["found"].iloc[filt_res.selected_peak]["prominence"]
        peak_height = peaks["found"].iloc[filt_res.selected_peak]["height"]
        peak_width = peaks["found"].iloc[filt_res.selected_peak]["width"]
        peak_pe_chl_ratio_linear = peaks["found"].iloc[filt_res.selected_peak]["pe_chl_ratio_linear"]
        peak_fsc_med = peaks["found"].iloc[filt_res.selected_peak]["fsc_small_med"]
        peak_pe_med = peaks["found"].iloc[filt_res.selected_peak]["pe_med"]
        peak_chl_med = peaks["found"].iloc[filt_res.selected_peak]["chl_small_med"]
        peak_count = len(peaks["found"])
    else:
        peak_pe_location = None
        peak_prom = None
        peak_height = None
        peak_width = None
        peak_pe_chl_ratio_linear = None
        peak_fsc_med = None
        peak_pe_med = None
        peak_chl_med = None
        peak_count = 0

    summary = pd.DataFrame(
        {
            "fsc_small_pe_count": len(pe_df),
            "fsc_small_range": fsc_range,
            "fsc_small_std": fsc_std,
            "fsc_small_1Q": fsc_q[0],
            "fsc_small_2Q": fsc_q[1],
            "fsc_small_3Q": fsc_q[2],
            "fsc_small_IQR": fsc_q[2] - fsc_q[0],
            "pe_range": pe_range,
            "pe_std": pe_std,
            "pe_1Q": pe_q[0],
            "pe_2Q": pe_q[1],
            "pe_3Q": pe_q[2],
            "pe_IQR": pe_q[2] - pe_q[0],
            "peak_count": peak_count,
            "peak_idx": filt_res.selected_peak,
            "peak_pe_location": peak_pe_location,
            "peak_prominence": peak_prom,
            "peak_height": peak_height,
            "peak_width": peak_width,
            "peak_pe_chl_ratio_linear": peak_pe_chl_ratio_linear,
            "peak_fsc_small_med": peak_fsc_med,
            "peak_pe_med": peak_pe_med,
            "peak_chl_small_med": peak_chl_med,
            "chl_small_range": chl_range,
            "chl_small_std": chl_std,
            "chl_small_1Q": chl_q[0],
            "chl_small_2Q": chl_q[1],
            "chl_small_3Q": chl_q[2],
            "chl_small_IQR": chl_q[2] - chl_q[0],
            "D1_count": len(d1_df),
            "D1_range": d1_range,
            "D1_std": d1_std,
            "D1_1Q": d1_q[0],
            "D1_2Q": d1_q[1],
            "D1_3Q": d1_q[2],
            "D1_IQR": d1_q[2] - d1_q[0],
            "D2_count": len(d2_df),
            "D2_range": d2_range,
            "D2_std": d2_std,
            "D2_1Q": d2_q[0],
            "D2_2Q": d2_q[1],
            "D2_3Q": d2_q[2],
            "D2_IQR": d2_q[2] - d2_q[0],
            "evt_count": particle_counts["evt"],
            "evt_min_val_count": particle_counts["evt_min_val"],
            "evt_pe_chl_count": particle_counts["evt_pe_chl"],
            "evt_peak_count": particle_counts["evt_peak"],
            "opp_count": particle_counts["opp"],
            "opp_min_val_count": particle_counts["opp_min_val"],
            "opp_pe_chl_count": particle_counts["opp_pe_chl"],
            "opp_peak_count": particle_counts["opp_peak"],
            "fsc_pe_cluster_count": len(fsc_pe_cluster_points),
            "fsc_d1_cluster_count": len(fsc_d1_cluster_points),
            "fsc_d2_cluster_count": len(fsc_d2_cluster_points),
            "elapsed_filter": None,
            "elapsed_peak": None,
            "elapsed_cluster": None,
            "elapsed_total": None,
            "date": None,
        },
        index=[0],
        dtype="float64",
    )
    summary["date"] = pd.to_datetime(summary["date"]).dt.tz_localize("UTC")
    summary["date"] = date
    template_summary = make_default_summary_dataframe()
    try:
        assert template_summary.columns.equals(summary.columns)
    except AssertionError:
        raise ValueError("Incorrect summary columns. Expected '%s', got '%s'", str(template_summary.columns), str(summary.columns))
    try:
        # Normalize timestamp resolution first
        summary_tmp = summary.copy()
        summary_tmp["date"] = summary_tmp["date"].astype('datetime64[ns, UTC]')
        assert template_summary.dtypes.equals(summary_tmp.dtypes)
    except AssertionError:
        raise ValueError("Incorrect summary dtypes. Expected '%s', got '%s'.", str(template_summary.dtypes), str(summary.dtypes))

    res = ClusterResult(
        date=date,
        conf=conf,
        error_message=err_msg,
        filter_results=filt_res,
        summary=summary,
        cluster_centers={
            "fsc_pe": fsc_pe_cluster_center,
            "fsc_d1": fsc_d1_cluster_center,
            "fsc_d2": fsc_d2_cluster_center
        },
        dfs={
            # These are the actual points that are beads from EVT data
            "fsc_pe": pe_df,  # points identified as beads by fsc pe
            "fsc_D1": d1_df,  # points identified as beads by fsc D1
            "fsc_D2": d2_df,  # points identified as beads by fsc D2
            "fsc_pe_cluster_points": fsc_pe_cluster_points,            # fsc pe hdbscan cluster points
            "fsc_pe_cluster_hull_points": fsc_pe_cluster_hull_points,  # fsc pe hdbscan cluster hull points
            "fsc_d1_cluster_points": fsc_d1_cluster_points,            # fsc d1 hdbscan cluster points
            "fsc_d2_cluster_points": fsc_d2_cluster_points             # fsc d2 hdbscan cluster points
        },
    )
    if not conf.instrument_slopes.empty:
        res.derived_filter_params = filter_params.from_bead_coords(summary, conf.instrument_slopes, conf.filtering_width)
    res.derived_filter_params["date"] = date if not res.derived_filter_params.empty else [date]

    res.elapsed_total = timer() - t0
    res.elapsed_cluster = t2 - t1
    summary["elapsed_filter"] = res.filter_results.elapsed_total
    summary["elapsed_peak"] = res.filter_results.elapsed_peak
    summary["elapsed_cluster"] = res.elapsed_cluster
    summary["elapsed_total"] = res.elapsed_total

    return res


def cluster(
    points: npt.NDArray[np.float64],
    min_cluster_frac: float,
    min_points: int = 50
) -> npt.NDArray:
    """
    Find a 2d cluster of points with HDBSCAN. Clustering has been tuned to work
    well for SeaFlow bead clusters.

    Parameters
    ----------
    points: numpy.ndarray
        2D array input to clusterer. An array of 2D points.
    min_cluster_frac: float
        Minimum fraction of points that should be in  the cluster. Passed to
        HDBSCAN's clusterer as min_cluster_size.
    min_points: int
        Raise errors.ClustererError if input dataframe has fewer than this many rows.

    Returns
    -------
    dict
        A dictionary of clustering results.

    Raises:
    -------
    BeadFinderError if more than one cluster or no cluster is found or input is too small.
    """
    if points.shape[0] < min_points:
        raise BeadFinderError(f"< {min_points} to cluster")
    logger.debug("clustering %d points", points.shape[0])
    min_cluster_size = int(points.shape[0] * min_cluster_frac)
    clusterer = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        allow_single_cluster=True,
        cluster_selection_method="eom",
    ).fit(points)
    nclust = len(set(clusterer.labels_))
    if nclust > 2:
        raise BeadFinderError(f"too many clusters found: {nclust}")
    if nclust == 0:
        raise BeadFinderError("no clusters found")
    idx = (clusterer.labels_ >= 0).nonzero()[0]
    return idx


def convex_hull(points: npt.NDArray[np.float64]) -> npt.NDArray[np.int64]:
    """Return an ndarray of convex hull point row indices"""
    if points.shape[0] < 3:
        raise BeadFinderError("cluster too small to find convex hull")
    try:
        hull = ConvexHull(points)
    except Exception as e:
        if type(e).__name__ == "QhullError":
            raise BeadFinderError("could not find convex hull") from e
        raise e
    return hull.vertices


def quantiles(a: npt.NDArray[np.float64], q_levels: list[float]) -> npt.NDArray[np.float64]:
    """Return tuple of quantiles q_levels for a."""
    qs = np.asarray([np.quantile(a, q) for q in q_levels])
    return qs


def points_in_polygon(
    poly_points: npt.NDArray[np.float64], points: npt.NDArray[np.float64]
) -> npt.NDArray[np.int64]:
    """
    Find indexes of points within the the polygon defined by poly_points.
    poly_points and points are 2d numpy arrays defining the bounding polygon and
    the points to test. The polygon defined by points will automatically close,
    meaning the first point doesn't need to be repeated as the last point.
    """
    if len(poly_points) < 3:
        return np.array([], dtype=int)
    poly = matplotlib.path.Path(poly_points)
    return poly.contains_points(points).nonzero()[0]
