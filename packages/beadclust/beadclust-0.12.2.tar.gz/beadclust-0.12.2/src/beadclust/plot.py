import logging
from typing import Any, Literal, Optional

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.spatial import ConvexHull

from beadclust import cluster
from beadclust.particleops import log_particles, unlog_particles

logger = logging.getLogger(__name__)


def plot_bead_coords(
    results: cluster.ClusterResultCollection,
    hour: str = "",
    spread_metric: Literal["IQR", "range"] = "range",
    spread_cutoff: float = 2500,
    min_fsc: float = 0,
    min_pe: float = 0,
    min_chl: float = 0,
    filter_params: pd.DataFrame | None = None,
    only_good: bool = False
):
    coords = results.summary()
    if only_good:
        good = ~(pd.isna(coords["fsc_small_2Q"]) | pd.isna(coords["D1_2Q"]) | pd.isna(coords["D2_2Q"]) | pd.isna(coords["peak_pe_location"]))
        good = good & (coords[f"fsc_small_{spread_metric}"] < spread_cutoff)
        coords = coords[good]

    fig, axs = plt.subplots(7, 1, sharex=True, layout="constrained")
    fig.set_size_inches(6, 6)
    fig.suptitle("Bead locations")

    _plot_bead_coords_row(
        axs[0],
        coords,
        "fsc_small",
        spread_metric,
        spread_cutoff,
        show_spread=True,
        hour=hour,
        y_min=min_fsc,
        filter_params=filter_params,
    )
    _plot_bead_coords_row(
        axs[1], coords, "pe", spread_metric, spread_cutoff, show_spread=True, hour=hour, y_min=min_pe
    )
    _plot_bead_coords_row(
        axs[2], coords, "chl_small", spread_metric, spread_cutoff, show_spread=True, hour=hour, y_min=min_chl
    )
    _plot_pe_peak_row(axs[3], coords, hour=hour, y_min=min_pe)
    _plot_bead_coords_row(
        axs[4],
        coords,
        "D1",
        spread_metric,
        spread_cutoff,
        hour=hour,
        show_spread=False,
        y_min=None,
        filter_params=filter_params,
    )
    _plot_bead_coords_row(
        axs[5],
        coords,
        "D2",
        spread_metric,
        spread_cutoff,
        hour=hour,
        show_spread=False,
        y_min=None,
        filter_params=filter_params,
    )
    axs[6].plot(
        coords.index.to_numpy(),
        coords["peak_pe_chl_ratio_linear"],
        markersize=5,
        marker=".",
        linestyle="None",
        color="tab:purple"
    )
    if hour:
        try:
            coords_hour_row = coords.loc[hour]
        except KeyError:
            pass
        else:
            _highlight_hour(axs[6], pd.to_datetime(hour), coords_hour_row["peak_pe_chl_ratio_linear"])
    axs[6].set_ylabel("pe/chl")
    axs[6].xaxis.set_tick_params(rotation=45)

    return fig


def _plot_bead_coords_row(
    ax,
    coords: pd.DataFrame,
    col_prefix: str,
    spread_metric: Literal["IQR", "range"] = "range",
    spread_cutoff: float = 3000,
    show_spread: bool = True,
    y_min: float | None = 0,
    hour: str = "",
    filter_params: Optional[pd.DataFrame] = None,
):
    # Plot bead coordinates with spread error bar
    if spread_metric not in ["IQR", "range"]:
        raise ValueError(f"unsupported choice for spread_metric '{spread_metric}'")

    if show_spread:
        yerr = coords[f"{col_prefix}_{spread_metric}"].to_numpy() / 2
    else:
        yerr = None

    # Create colors for each point and error bar. Blue for good, pink for high
    # spread in fsc_small, and lower alpha if no pe peak was detected.
    blue = mpl.colors.to_rgba("tab:blue")
    pink = mpl.colors.to_rgba("tab:pink")
    colors = (
        (*blue[:3], 1),
        (*blue[:3], 0.2),
        (*pink[:3], 1),
        (*pink[:3], 0.2),
    )
    no_peak_bool = np.isnan(coords["peak_pe_location"].to_numpy())
    high_spread_bool = coords[f"fsc_small_{spread_metric}"].to_numpy() > spread_cutoff
    bool_idx = [
        (~high_spread_bool) & (~no_peak_bool),
        (~high_spread_bool) & (no_peak_bool),
        (high_spread_bool) & (~no_peak_bool),
        (high_spread_bool) & (no_peak_bool),
    ]
    for i, _ in enumerate(colors):
        if yerr is not None:
            ax.errorbar(
                coords[bool_idx[i]].index.to_numpy(),
                coords[bool_idx[i]][f"{col_prefix}_2Q"].to_numpy(),
                yerr=yerr[bool_idx[i]],
                markersize=5,
                marker=".",
                linestyle="None",
                c=colors[i],
            )
        else:
            ax.plot(
                coords[bool_idx[i]].index.to_numpy(),
                coords[bool_idx[i]][f"{col_prefix}_2Q"].to_numpy(),
                markersize=5,
                marker=".",
                linestyle="None",
                c=colors[i],
            )

    # Highlight one time point
    if hour:
        try:
            hour_row = coords.loc[hour]
        except KeyError:
            hour_row = None
        else:
            _highlight_hour(ax, pd.to_datetime(hour), hour_row[f"{col_prefix}_2Q"])

    # Draw traditional filter parameter line
    # Use 50% quantile since we're not showing filtering cutoffs, we're showing
    # db bead positions.
    if filter_params is not None:
        ax.axhline(
            filter_params.loc[filter_params["quantile"] == 50, f"beads_{col_prefix}"].squeeze(),
            alpha=0.5,
            color="tab:gray",
            linestyle="--",
        )
    
    if y_min is not None:
        ax.set_ylim(y_min, 2**16)

    # Plot attempted but failed clustering runs
    failed = coords[coords["fsc_small_2Q"].isna() | coords["D1_2Q"].isna() | coords["D2_2Q"].isna()]
    ax.plot(failed.index, np.repeat(ax.get_ylim()[0], failed.shape[0]), "o", color="tab:gray", alpha=0.2)
    
    ax.set_ylabel(col_prefix)


def _plot_pe_peak_row(
    ax,
    coords,
    hour: str = None,
    y_min: float = 0,
):
    ax.plot(
        coords.index,
        coords["peak_pe_location"],
        marker=".",
        markersize=5,
        alpha=0.5,
        color="tab:purple",
        linestyle="None",
    )
    if hour:
        try:
            coords_hour_row = coords.loc[hour]
        except KeyError:
            pass
        else:
            _highlight_hour(ax, pd.to_datetime(hour), coords_hour_row["peak_pe_location"])
    ax.set_ylim(y_min, 2**16)
    ax.set_ylabel("pe peaks")


def plot_peak_props(results: cluster.ClusterResultCollection, hour: str = ""):
    logger.info("plotting peak properties, highlighted hour = %s", hour)
    if hour:
        hour = pd.Timestamp(hour, tz="utc")

    summary = results.summary()

    def highlight_hour(ax, x):
        if x:
            ax.axvline(x, alpha=0.2, color="tab:gray")

    fig, axs = plt.subplots(8, 1, sharex=True, layout="constrained")
    fig.set_size_inches(6, 8)
    fig.suptitle("peak properties")
    axs[0].plot(
        summary.index, summary["peak_pe_location"],
        marker=".", markersize=5, alpha=0.5, color="tab:purple", linestyle="None"
    )
    axs[0].set_ylabel("peak pe")
    highlight_hour(axs[0], hour)

    axs[1].plot(
        summary.index,
        summary["peak_fsc_small_med"], marker=".", markersize=5, alpha=0.5, color="tab:purple", linestyle="None")
    axs[1].set_ylabel("fsc med")
    highlight_hour(axs[1], hour)

    axs[2].plot(
        summary.index,
        summary["peak_pe_med"], marker=".", markersize=5, alpha=0.5, color="tab:purple", linestyle="None")
    axs[2].set_ylabel("pe med")
    highlight_hour(axs[2], hour)

    axs[3].plot(
        summary.index,
        summary["peak_chl_small_med"], marker=".", markersize=5, alpha=0.5, color="tab:purple", linestyle="None")
    axs[3].set_ylabel("chl med")
    highlight_hour(axs[3], hour)

    axs[4].plot(
        summary.index,
        summary["peak_height"],
        marker=".", markersize=5, alpha=0.5, color="tab:purple", linestyle="None"
    )
    axs[4].set_ylabel("height")
    highlight_hour(axs[4], hour)

    axs[5].plot(
        summary.index,
        summary["peak_width"],
        marker=".", markersize=5, alpha=0.5, color="tab:purple", linestyle="None"
    )
    axs[5].set_ylabel("width")
    highlight_hour(axs[5], hour)

    axs[6].plot(
        summary.index,
        summary["peak_idx"],
        marker=".", markersize=5, alpha=0.5, color="tab:purple", linestyle="None"
    )
    axs[6].set_ylabel("peak_idx")
    highlight_hour(axs[6], hour)

    axs[7].plot(
        summary.index,
        summary["peak_count"],
        marker=".", markersize=5, alpha=0.5, color="tab:purple", linestyle="None"
    )
    axs[7].set_ylabel("peak count")
    highlight_hour(axs[7], hour)

    axs[7].xaxis.set_tick_params(rotation=45)

    return fig


def _highlight_hour(ax, x, y):
    ax.plot(x, y, "o", color="tab:green", linestyle="None", alpha=0.5)
    ax.axvline(x, alpha=0.2, color="tab:gray")


def plot_filtering_cytograms(
    res: cluster.ClusterResult,
    evt: pd.DataFrame,
    scatter=False,
    n=10000  # maximum particles to draw
):
    add_base_plot = _add_scatter if scatter else _add_hexbin

    logger.info("%d EVT events", len(evt))
    evt_ali = evt[res.filter_results.evt_ali]
    logger.info("%d EVT events after alignment", len(evt_ali))
    opp = evt[res.filter_results.opp]
    logger.info("%d OPP events", len(opp))

    fig, axs_ = plt.subplots(3, 2, layout="constrained")
    axs = list(axs_.flatten())
    axs.reverse()  # to pop last element off starting with 0, 0

    lims = _calc_lims(evt)
    # lims = {"fsc_small": (0, 1.05 * 2**16), "D1": (0, 1.05 * 2**16), "D2": (0, 1.05 * 2**16)}

    # EVT density with convex hull around aligned particles
    ax = axs.pop()
    aligned_hull = ConvexHull(evt_ali[["D1", "D2"]].to_numpy())
    aligned_hull_points = np.transpose(evt_ali.iloc[aligned_hull.vertices][["D1", "D2"]].values)
    aligned_hull_points = _close_poly(aligned_hull_points)
    add_base_plot(ax, cap(evt, n), ["D1", "D2"], "Raw EVT", lims=lims)
    ax.axline((0, 0), slope=1, color="gray", linestyle="dashed", alpha=0.5)
    ax.plot(aligned_hull_points[0], aligned_hull_points[1], color="tab:cyan", alpha=0.5)
    _set_aspect(ax, 1)

    # EVT density of just aligned particles
    ax = axs.pop()
    add_base_plot(ax, cap(evt_ali, n), ["D1", "D2"], "Aligned EVT", lims=lims)
    ax.axline((0, 0), slope=1, color="gray", linestyle="dashed", alpha=0.5)
    _set_aspect(ax, 1)

    ax = axs.pop()
    add_base_plot(ax, cap(evt_ali, n), ["fsc_small", "D1"], "Aligned EVT", lims=lims)
    if (res.conf.filter_params_by_date is not None) and (len(res.conf.filter_params_by_date) > 0):
        _add_filter_cutoff(ax, "D1", res.conf.filter_params_by_date)
    else:
        _add_roughfilter_cutoff(ax, evt_ali, "D1")
    _set_aspect(ax, 1)

    ax = axs.pop()
    add_base_plot(ax, cap(evt_ali, n), ["fsc_small", "D2"], "Aligned EVT", lims=lims)
    if (res.conf.filter_params_by_date is not None) and (len(res.conf.filter_params_by_date) > 0):
        _add_filter_cutoff(ax, "D2", res.conf.filter_params_by_date)
    else:
        _add_roughfilter_cutoff(ax, evt_ali, "D2")
    _set_aspect(ax, 1)

    ax = axs.pop()
    add_base_plot(ax, cap(opp, n), ["fsc_small", "D1"], "OPP", lims=lims)
    if (res.conf.filter_params_by_date is not None) and (len(res.conf.filter_params_by_date) > 0):
        _add_filter_cutoff(ax, "D1", res.conf.filter_params_by_date)
    else:
        _add_roughfilter_cutoff(ax, evt_ali, "D1")
    _set_aspect(ax, 1)

    ax = axs.pop()
    add_base_plot(ax, cap(opp, n), ["fsc_small", "D2"], "OPP ", lims=lims)
    if (res.conf.filter_params_by_date is not None) and (len(res.conf.filter_params_by_date) > 0):
        _add_filter_cutoff(ax, "D2", res.conf.filter_params_by_date)
    else:
        _add_roughfilter_cutoff(ax, evt_ali, "D2")
    _set_aspect(ax, 1)

    fig.set_figwidth(6)
    fig.set_figheight(10)

    return fig


def plot_bead_cytograms_evt(
    res: cluster.ClusterResult,
    evt: pd.DataFrame,
    scatter=False,
    show_cutoffs=False,
    apply_cutoffs=False,
    show_clusters=False,
    n=10000  # max particles to draw
):
    # Scatter or hexbin density
    add_base_plot = _add_scatter if scatter else _add_hexbin

    # Grab cutoffs
    pe_chl_cutoff = res.conf.pe_chl_cutoff
    min_fsc = res.conf.min_fsc
    min_pe = res.conf.min_pe
    min_chl= res.conf.min_chl

    # Draw cutoffs?
    draw_min_fsc = None
    draw_min_pe = None
    draw_min_chl = None
    draw_peaks = None
    pe_chl_cutoff_point_and_slope = None

    # Filter results
    filt_res = res.filter_results

    # Cluster data
    # FSC/PE EVT cluster points
    evt_cluster_points = res.dfs["fsc_pe"][["fsc_small", "pe"]].to_numpy()
    # Points from evt_cluster_points used as input to D1 clustering
    d1_pe_cluster_points = res.dfs["fsc_pe"][["fsc_small", "D1"]].to_numpy()
    # Points from evt_cluster_points used as input to D2 clustering
    d2_pe_cluster_points = res.dfs["fsc_pe"][["fsc_small", "D2"]].to_numpy()
    # FSC/D1 EVT cluster points
    d1_cluster_points = res.dfs["fsc_D1"][["fsc_small", "D1"]].to_numpy()
    # FSC/D2 EVT cluster points
    d2_cluster_points = res.dfs["fsc_D2"][["fsc_small", "D2"]].to_numpy()

    # Scatter point style configs
    pe_cluster_scatter_color = "tab:purple" if scatter else "tab:blue"
    d12_cluster_scatter_color = "tab:red" if scatter else "tab:red"
    cluster_scatter_markersize = 1
    cluster_scatter_alpha = 0.5

    logger.info("%d EVT events", filt_res.counts["evt"])
    logger.info("%d EVT events after alignment", filt_res.counts["evt_ali"])
    logger.info("%d OPP events", filt_res.counts["opp"])

    lims = _calc_lims(evt)

    if apply_cutoffs:
        opp = evt[filt_res.opp_cut_peaks]
        evt_cut = evt[filt_res.evt_cut_peaks]

        # lims["fsc_small"] = (min_fsc * 0.95, 2**16 * 1.05)
        # lims["pe"] = (min_pe * 0.95, 2**16 * 1.05)
        logger.info("%d OPP events after applying cutoffs", len(opp))
        logger.info("%d EVT events after applying cutoffs", len(evt_cut))
    else:
        opp = evt[filt_res.opp]
        evt_cut = evt[filt_res.evt_ali]

    peaks = filt_res.peaks

    if show_cutoffs:
        draw_min_fsc = min_fsc
        draw_min_pe = min_pe
        draw_min_chl = min_chl
        draw_peaks = peaks
        # Point that PE/CHL cutoff line must go through. Don't use (0, 0) as this
        # would extend the axis scales farther than desired.
        pe_chl_cutoff_point = (max(min_pe, evt["pe"].min()), max(min_pe, evt["pe"].min()) * pe_chl_cutoff)
        pe_chl_cutoff_point_and_slope = (pe_chl_cutoff_point, pe_chl_cutoff)

    fig, axs_ = plt.subplots(3, 2, layout="constrained")
    axs = list(axs_.flatten())
    axs.reverse()  # to pop last element off starting with 0, 0

    # EVT chl pe
    ax = axs.pop()
    add_base_plot(
        ax,
        cap(evt_cut, n),
        ["chl_small", "pe"],
        "Aligned EVT",
        lims=lims,
        x_cutoff=draw_min_chl,
        y_cutoff=draw_min_pe,
        peaks=draw_peaks,
        selected_peak=filt_res.selected_peak,
        pe_chl_cutoff_point_and_slope=pe_chl_cutoff_point_and_slope,
    )
    _set_aspect(ax, 1)

    # EVT fsc pe
    ax = axs.pop()
    add_base_plot(
        ax,
        cap(evt_cut, n),
        ["fsc_small", "pe"],
        "Aligned EVT",
        lims=lims,
        x_cutoff=draw_min_fsc,
        y_cutoff=draw_min_pe,
        peaks=draw_peaks,
        selected_peak=filt_res.selected_peak,
    )
    if show_clusters:
        ax.plot(
            *np.transpose(evt_cluster_points),
            marker="o",
            markersize=cluster_scatter_markersize,
            linestyle="None",
            color=pe_cluster_scatter_color,
            markeredgecolor="None",
            alpha=cluster_scatter_alpha,
        )
    _set_aspect(ax, 1)

    # OPP pe chl
    ax = axs.pop()
    add_base_plot(
        ax,
        cap(opp, n),
        ["chl_small", "pe"],
        "OPP",
        lims=lims,
        x_cutoff=draw_min_chl,
        y_cutoff=draw_min_pe,
        peaks=draw_peaks,
        selected_peak=filt_res.selected_peak,
        pe_chl_cutoff_point_and_slope=pe_chl_cutoff_point_and_slope,
    )
    _set_aspect(ax, 1)

    # OPP fsc pe
    ax = axs.pop()
    add_base_plot(
        ax,
        cap(opp, n),
        ["fsc_small", "pe"],
        "OPP",
        lims=lims,
        x_cutoff=draw_min_fsc,
        y_cutoff=draw_min_pe,
        peaks=draw_peaks,
        selected_peak=filt_res.selected_peak,
    )
    _set_aspect(ax, 1)

    # EVT fsc D1
    ax = axs.pop()
    add_base_plot(
        ax,
        cap(evt_cut, n),
        ["fsc_small", "D1"],
        "EVT",
        lims=lims,
        x_cutoff=draw_min_fsc
    )
    if show_clusters:
        # Plot points that came from initial FSC/PE cluster, and were used as
        # input to D1 clustering
        ax.plot(
            *np.transpose(d1_pe_cluster_points),
            marker="o",
            markersize=cluster_scatter_markersize,
            linestyle="None",
            color=pe_cluster_scatter_color,
            markeredgecolor="None",
            alpha=cluster_scatter_alpha,
        )
        # Plot FSC/D1 points clustered
        ax.plot(
            *np.transpose(d1_cluster_points),
            marker="o",
            markersize=cluster_scatter_markersize,
            linestyle="None",
            color=d12_cluster_scatter_color,
            markeredgecolor="None",
            alpha=cluster_scatter_alpha,
        )
    _set_aspect(ax, 1)

    # EVT fsc D2
    ax = axs.pop()
    add_base_plot(
        ax,
        cap(evt_cut, n),
        ["fsc_small", "D2"],
        "EVT",
        lims=lims,
        x_cutoff=draw_min_fsc
    )
    if show_clusters:
        # Plot points that came from initial FSC/PE cluster, and were used as
        # input to D2 clustering
        ax.plot(
            *np.transpose(d2_pe_cluster_points),
            marker="o",
            markersize=cluster_scatter_markersize,
            linestyle="None",
            color=pe_cluster_scatter_color,
            markeredgecolor="None",
            alpha=cluster_scatter_alpha,
        )
        # Plot FSC/D1 points clustered
        ax.plot(
            *np.transpose(d2_cluster_points),
            marker="o",
            markersize=cluster_scatter_markersize,
            linestyle="None",
            color=d12_cluster_scatter_color,
            markeredgecolor="None",
            alpha=cluster_scatter_alpha,
        )
    _set_aspect(ax, 1)

    fig.set_figwidth(6)
    fig.set_figheight(10)

    return fig


def _add_hexbin(
    ax,
    df,
    cols,
    title,
    lims=None,
    x_cutoff=None,
    y_cutoff=None,
    peaks=None,
    selected_peak=None,
    pe_chl_cutoff_point_and_slope=None,
    bins="log"
):
    ax.hexbin(df[cols[0]].values, df[cols[1]].values, cmap="inferno", bins=bins)
    ax.set_facecolor("black")
    _finish_ax(
        ax,
        cols,
        title,
        lims=lims,
        x_cutoff=x_cutoff,
        y_cutoff=y_cutoff,
        peaks=peaks,
        selected_peak=selected_peak,
        pe_chl_cutoff_point_and_slope=pe_chl_cutoff_point_and_slope,
    )


def _add_scatter(
    ax,
    df,
    cols,
    title,
    lims=None,
    x_cutoff=None,
    y_cutoff=None,
    peaks=None,
    selected_peak=None,
    pe_chl_cutoff_point_and_slope=None,
):
    ax.plot(df[cols[0]].values, df[cols[1]].values, alpha=0.1, marker="o", markersize=2, linestyle="None")
    _finish_ax(
        ax,
        cols,
        title,
        lims=lims,
        x_cutoff=x_cutoff,
        y_cutoff=y_cutoff,
        peaks=peaks,
        selected_peak=selected_peak,
        pe_chl_cutoff_point_and_slope=pe_chl_cutoff_point_and_slope,
    )


def _add_filter_cutoff(ax, dcol, filter_params):
    filter_params = filter_params[filter_params["quantile"] == 2.5]
    notch_small = filter_params[f"notch_small_{dcol}"].values[0]  # slope
    offset_small = filter_params[f"offset_small_{dcol}"].values[0]  # y-offset
    notch_large = filter_params[f"notch_large_{dcol}"].values[0]  # slope
    offset_large = filter_params[f"offset_large_{dcol}"].values[0]  # y-offset

    ax.axline((0, offset_small), slope=notch_small, color="tab:cyan", linestyle="dashed", alpha=0.5)
    ax.axline((0,  offset_large), slope=notch_large, color="tab:cyan", linestyle="dashed", alpha=0.5)


def _add_roughfilter_cutoff(ax, aligned, dcol):
    # Note that because of floating-point precision limitations during equality
    # testing, the "largest fsc_small with smallest D1 or D2" points may not
    # pass filtering. So to accurately identify these points we must use aligned
    # EVT particles, not OPP particles.
    fsc_max = aligned["fsc_small"].max()
    bigs = aligned[aligned["fsc_small"] == fsc_max]
    best_big = (fsc_max, bigs[dcol].min())
    ax.axline((0, 0), best_big, color="tab:cyan", linestyle="dashed", alpha=0.5)
    ax.scatter(*best_big, color="tab:pink", alpha=0.5, zorder=2.5)


def _finish_ax(
    ax, cols, title, lims=None, x_cutoff=None, y_cutoff=None, peaks=None,
    selected_peak=None, pe_chl_cutoff_point_and_slope=None
):
    cutoff_line_color = "gray"
    ax.set_title(title, fontsize=10)
    ax.set_xlabel(cols[0])
    ax.set_ylabel(cols[1])

    if lims is not None:
        ax.set_xlim(lims[cols[0]])
        ax.set_ylim(lims[cols[1]])

    if x_cutoff is not None:
        ax.axvline(x=x_cutoff, color=cutoff_line_color, alpha=0.5, linestyle="dotted")
        if x_cutoff > 0:
            ax.text(x_cutoff, ax.get_ylim()[0] + 1000, f"{x_cutoff}", color="gray", rotation=90)
    if y_cutoff is not None:
        ax.axhline(y=y_cutoff, color=cutoff_line_color, alpha=0.5, linestyle="dotted")
        if y_cutoff > 0:
            ax.text(ax.get_xlim()[0] + 1000, y_cutoff, f"{y_cutoff}", color="gray")
    if pe_chl_cutoff_point_and_slope is not None:
        ax.axline(
            pe_chl_cutoff_point_and_slope[0],
            slope=pe_chl_cutoff_point_and_slope[1],
            color="tab:red",
            alpha=0.5,
            linestyle="dotted",
        )
    if peaks and not peaks["found"].empty and selected_peak is not None:
        sel_peak = peaks["found"].iloc[selected_peak]
        ax.axhline(sel_peak["location"], color="tab:olive", alpha=0.2)
        ax.axhline(sel_peak["low_cutoff"], color="tab:olive", alpha=0.5, linestyle="dotted")
        ax.axhline(sel_peak["high_cutoff"], color="tab:olive", alpha=0.5, linestyle="dotted")


def _set_aspect(ax, ratio):
    xmin, xmax = ax.get_xlim()
    ymin, ymax = ax.get_ylim()
    ax.set_aspect(abs((xmax - xmin) / (ymax - ymin)) * ratio)


def _calc_lims(df):
    lims = dict()
    for col in df.select_dtypes(include=np.number).columns:
        lims[col] = (df[col].min() * 0.95, df[col].max() * 1.05)
    return lims


def _close_poly(points: np.ndarray):
    """Close a polygon defined by an ndarray of shape = (2, n_points)"""
    if (points.size > 0) and (points.shape[0] == 2) and (not np.array_equal(points[:, 0], points[:, -1])):
        logger.info("closing polygon, %s != %s", points[:, 0], points[:, -1])
        return np.append(points, points[:, :1], axis=1)
    return points


def cap(df, n):
    if not n or n >= len(df):
        return df
    return df.sample(n=n, random_state=12345)


def plot_peaks(
    particles: pd.DataFrame,
    peaks: dict[str, Any],
    selected_peak: Optional[int]=None
):
    fig = plt.figure(figsize=(7.5, 6))
    gs = fig.add_gridspec(nrows=1, ncols=2, width_ratios=[4, 1], wspace=0.05)
    ax_hex = fig.add_subplot(gs[0, 0])
    ax_hist = fig.add_subplot(gs[0, 1], sharey=ax_hex)
    ax_hist.tick_params(axis="y", labelleft=False)
    ax_hex.set_title("PE peak finding")

    ax_hex.hexbin(particles["fsc_small"], particles["pe"], cmap="inferno")
    if peaks:
        for i, p in peaks["found"].iterrows():
            if selected_peak is not None and i == selected_peak:
                ax_hex.axhline(peaks["bin_midpoints"][int(p["idx"])], color="tab:red", alpha=0.85)
                ax_hex.axhline(p["low_cutoff"], color="tab:olive", alpha=0.85)
                ax_hex.axhline(p["high_cutoff"], color="tab:olive", alpha=0.85)
            else:
                ax_hex.axhline(peaks["bin_midpoints"][int(p["idx"])], color="tab:red", alpha=0.4)

        bins = [x.left for x in peaks["bin_intervals"]]
        bins.append(peaks["bin_intervals"][-1].right)
        ax_hist.hist(peaks["bin_midpoints"], bins, weights=peaks["counts"], orientation="horizontal")
        ax_hist.plot(peaks["counts_ma"], peaks["bin_midpoints"], marker=None, color="tab:pink")
        for i, p in peaks["found"].iterrows():
            # Peak location x marker
            peaks_x = peaks["counts_ma"][int(p["idx"])]
            peaks_y = peaks["bin_midpoints"][int(p["idx"])]
            # Peak width
            extent_xs = (peaks_x, peaks_x)
            extent_ys = (
                peaks_y - (peaks["bin_size"] * p["width"] / 2),
                peaks_y + (peaks["bin_size"] * p["width"] / 2)
            )
            if selected_peak is not None and selected_peak == i:
                # Peak cutoffs and double/half for selected peak
                ax_hist.plot(peaks_x, peaks_y, "x", color="tab:red", alpha=0.85)
                ax_hist.axhline(p["low_cutoff"], color="tab:olive", alpha=0.85)
                ax_hist.axhline(p["high_cutoff"], color="tab:olive", alpha=0.85)
                ax_hist.axhline(p["double"], color="tab:gray", alpha=0.85)
                ax_hist.axhline(p["half"], color="tab:gray", alpha=0.85)
                ax_hist.plot(extent_xs, extent_ys, marker=None, linestyle="solid", color="tab:red", alpha=0.5)
                double_lower_bound = log_particles(unlog_particles(extent_ys[0]) * 2)
                double_curp_upper_bound = log_particles(unlog_particles(extent_ys[1]) * 2)
                ax_hist.plot(
                    extent_xs,
                    [double_lower_bound, double_curp_upper_bound],
                    marker=None, linestyle=":", color="tab:pink", alpha=0.5
                )
            else:
                ax_hist.plot(peaks_x, peaks_y, "x", color="tab:red", alpha=0.5)
                ax_hist.plot(extent_xs, extent_ys, marker=None, linestyle="solid", color="tab:red", alpha=0.25)

    return fig


def plot_timings(coords: pd.DataFrame, hour: str=""):
    fig, axs = plt.subplots(4, 1, layout="constrained", sharex=True)
    fig.set_size_inches(6, 4)
    plot_kwargs = {"markersize": 5, "marker": ".", "linestyle": "None"}
    cols = ["elapsed_filter", "elapsed_peak", "elapsed_cluster", "elapsed_total"]
    for i, col in enumerate(cols):
        axs[i].plot(coords.index, coords[col], **plot_kwargs)
        if hour:
            if len(coords.loc[hour]) > 0:
                axs[i].plot(pd.to_datetime(hour), coords.loc[hour][col], "o", color="tab:green", linestyle="None", alpha=0.5)
            axs[i].axvline(pd.to_datetime(hour), alpha=0.2, color="tab:gray")
        axs[i].set_title(col)
    axs[-1].xaxis.set_tick_params(rotation=45)


def plot_counts(coords: pd.DataFrame, hour: str=""):
    fig, axs = plt.subplots(11, 1, layout="constrained", sharex=True)
    fig.set_size_inches(6, 8)
    plot_kwargs = {"markersize": 5, "marker": ".", "linestyle": "None"}
    cols = [
        "evt_count", "opp_count",
        "evt_min_val_count", "evt_pe_chl_count", "evt_peak_count",
        "opp_min_val_count", "opp_pe_chl_count", "opp_peak_count",
        "fsc_pe_cluster_count", "fsc_d1_cluster_count", "fsc_d2_cluster_count"
    ]
    for i, col in enumerate(cols):
        axs[i].plot(coords.index, coords[col], **plot_kwargs)
        if hour:
            if len(coords.loc[hour]) > 0:
                axs[i].plot(pd.to_datetime(hour), coords.loc[hour][col], "o", color="tab:green", linestyle="None", alpha=0.5)
            axs[i].axvline(pd.to_datetime(hour), alpha=0.2, color="tab:gray")
        axs[i].set_title(col)
    axs[-1].xaxis.set_tick_params(rotation=45)
