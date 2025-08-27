import copy
import logging
import sys
from pathlib import Path
from importlib import metadata
from importlib import resources
from timeit import default_timer as timer
from shutil import copyfile

import click
import joblib
import numpy as np
import pandas as pd

from . import db
from .io import read_config
from . import cluster
from . import plot


@click.group(dict(help_option_names=['-h', '--help']))
def cli():
    pass


@cli.command(
    'run',
    context_settings=dict(
        ignore_unknown_options=True,
        allow_extra_args=True,
    )
)
@click.option("-c", "--config", "config_file", type=click.Path(exists=True), required=True, help="YAML config")
@click.option("-v", "--verbose", count=True, help="Print debug info.")
@click.pass_context
def run_cmd(ctx, config_file, verbose):
    """
    Find bead location and generate filtering parameters.
    """
    # Parse unknown options as config jinja2 template data
    i = 0
    template_data = {}
    while i < len(ctx.args) - 1:
        if ctx.args[i].startswith("--") and not ctx.args[i+1].startswith("--"):
            template_data[ctx.args[i][2:]] = ctx.args[i+1]
            i += 2
        else:
            i += 1

    if verbose == 0:
        loglevel = logging.INFO
    elif verbose == 1:
        loglevel = logging.DEBUG
    logger = logging.getLogger()
    logger.setLevel(loglevel)
    logging_ch = logging.StreamHandler()
    logging_ch.setFormatter(logging.Formatter(fmt="%(asctime)s: %(levelname)s: %(message)s"))
    logger.addHandler(logging_ch)

    logger.info("version = %s", metadata.version(__package__))

    # Read config
    if template_data:
        logger.info("using config template arguments: %s", template_data)
    logger.info("config file = %s", config_file)
    config_text, config = read_config(config_file, template_data)
    logger.info("loaded config data")
    print(config_text, file=sys.stderr)

    logger.info("input EVT file = %s", config["evt_file"])
    logger.info("output dir = %s", config["out_dir"])

    evt_df = pd.read_parquet(config["evt_file"])
    if len(evt_df) == 0:
        raise click.ClickException("no EVT data for bead finding")
    if "date" not in evt_df.columns:
        evt_df = evt_df.reset_index()  # maybe it's the index, don't drop
        if "date" not in evt_df.columns:
            raise click.ClickException("no date column in EVT dataframe")
    logger.info("%d particles in %s", len(evt_df), config["evt_file"])

    # Apply any date filters
    if config["start_date"] or config["end_date"]:
        date_selector = np.full(len(evt_df), True, dtype=bool)
        logger.info("apply date filter, %s to %s", config["start_date"], config["max_date"])
        if config["start_date"]:
            date_selector = evt_df["date"] >= config["start_date"]
            logger.info("%s after start_date filter", np.sum(date_selector))
        if config["end_date"]:
            date_selector = date_selector & (evt_df["date"] <= config["end_date"])
            logger.info("%s after max_date filter", np.sum(date_selector))
        evt_df = evt_df[date_selector]
        logger.info(
            "%s rows between %s and %s after date filter", len(evt_df), evt_df["date"].min(), evt_df["date"].max()
        )

    if config["db_file"]:
        serial = db.get_serial(config["db_file"])
        db_filter_params = db.get_filter_params(config["db_file"])
        if len(db_filter_params) == 0:
            db_filter_params = None
    else:
        db_filter_params = None
        serial = config["serial"]
    if not serial:
        raise click.ClickException("no serial defined")

    # Create output paths
    out_dir = Path(config["out_dir"])
    out_dir.mkdir(parents=True, exist_ok=True)
    evt_copy_path = out_dir / f"{config['name']}.input-evt.parquet"
    summary1_out_path = out_dir / f"{config['name']}.summary.round1.parquet"
    summary2_out_path = out_dir / f"{config['name']}.summary.round2.parquet"
    filter_params1_out_path = out_dir / f"{config['name']}.filter_params.round1.parquet"
    filter_params2_out_path = out_dir / f"{config['name']}.filter_params.round2.parquet"
    results1_out_path = out_dir / f"{config['name']}.results.round1.joblib"
    results2_out_path = out_dir / f"{config['name']}.results.round2.joblib"
    peaks1_plot_path = out_dir / f"{config['name']}.peaks-properties.round1.png"
    peaks2_plot_path = out_dir / f"{config['name']}.peaks-properties.round2.png"
    coords1_plot_path = out_dir / f"{config['name']}.coords.round1.png"
    coords2_plot_path = out_dir / f"{config['name']}.coords.round2.png"
    good_coords1_plot_path = out_dir / f"{config['name']}.coords-good.round1.png"
    good_coords2_plot_path = out_dir / f"{config['name']}.coords-good.round2.png"
    new_db_path = out_dir / f"{config['name']}.db"

    # ------------------------------------------------------------------------ #
    # Round 1
    # ------------------------------------------------------------------------ #
    t0 = timer()
    cconf = cluster.ClusterConfig(
        name=config["name"],
        serial=serial,
        time_res=config["time_resolution"],
        min_fsc=config["min_fsc"],
        min_pe=config["min_pe"],
        min_chl=config["min_chl"],
        pe_chl_cutoff=config["pe_chl_cutoff"],
        peak_finder_params={
            "peak_width": [config["peak_width_min"], config["peak_width_max"]],
            "bin_size": config["peak_bin_size"],
            "ma_window_size": config["peak_ma_window_size"],
            "peak_height_frac_max": config["peak_height_frac_max"]
        },
        filtering_width=config["filtering_width"],
        origin_align=config["origin_align"],
        max_cluster_input=config["max_cluster_input"],
        min_cluster_frac=config["min_cluster_frac"],
        spread_cutoff=config["spread_cutoff"],
        db_filter_params=db_filter_params,
        cluster_log=config["cluster_log"],
    )

    logging.info("Round 1 starting")
    results1 = cluster.cluster_cruise(evt_df, cconf, max_workers=config["workers"])
    summary1 = results1.summary()
    try:
        filter_params1 = results1.filter_params()
    except ValueError as e:
        logger.error(e)
        logger.error("No good round 1 bead locations found, will skip round 2")
        filter_params1 = None

    # Save results
    logger.info("Saving round 1 results")
    joblib.dump(results1, results1_out_path)
    copyfile(config["evt_file"], evt_copy_path)
    summary1.to_parquet(summary1_out_path)
    if filter_params1 is not None:
        filter_params1.to_parquet(filter_params1_out_path)
    # Save plots
    logger.info("Saving round 1 plots")
    plot.plot_peak_props(results1).savefig(peaks1_plot_path)
    plot.plot_bead_coords(
        results1, spread_cutoff=config["spread_cutoff"],
        min_fsc=config["min_fsc"], min_pe=config["min_pe"],
        filter_params=cconf.db_filter_params
    ).savefig(coords1_plot_path)
    plot.plot_bead_coords(
        results1, spread_cutoff=config["spread_cutoff"],
        min_fsc=config["min_fsc"], min_pe=config["min_pe"],
        filter_params=cconf.db_filter_params,
        only_good=True
    ).savefig(good_coords1_plot_path)

    t1 = timer()
    logger.info("Round 1 completed in %s sec", t1 - t0)

    if filter_params1 is None:
        logger.info("Exiting without round 2")
        return

    # Move filtering lines up to capture more OPP
    filter_params_for_round2 = results1.filter_params()
    filter_params_for_round2["offset_small_D1"] += config["filtering_offset"]
    filter_params_for_round2["offset_small_D2"] += config["filtering_offset"]
    filter_params_for_round2["offset_large_D1"] += config["filtering_offset"]
    filter_params_for_round2["offset_large_D2"] += config["filtering_offset"]

    # ------------------------------------------------------------------------ #
    # Round 2
    # ------------------------------------------------------------------------ #
    cconf2 = copy.copy(cconf)
    cconf2.filter_params_by_date = filter_params_for_round2

    logger.info("Round 2 starting")
    results2 = cluster.cluster_cruise(evt_df, cconf2, max_workers=config["workers"])
    summary2 = results2.summary()
    filter_params2 = results2.filter_params()

    # Save results
    logger.info("Saving round 2 results")
    joblib.dump(results2, results2_out_path)
    summary2.to_parquet(summary2_out_path)
    filter_params2.to_parquet(filter_params2_out_path)
    # Save plot
    logger.info("Saving round 2 plots")
    plot.plot_peak_props(results2).savefig(peaks2_plot_path)
    plot.plot_bead_coords(
        results2, spread_cutoff=config["spread_cutoff"],
        min_fsc=config["min_fsc"], min_pe=config["min_pe"],
        filter_params=cconf.db_filter_params
    ).savefig(coords2_plot_path)
    plot.plot_bead_coords(
        results2, spread_cutoff=config["spread_cutoff"],
        min_fsc=config["min_fsc"], min_pe=config["min_pe"],
        filter_params=cconf.db_filter_params,
        only_good=True
    ).savefig(good_coords2_plot_path)
    # Save new seaflowpy/popcycle DB
    logger.info("Saving new database file")
    db.save_metadata(new_db_path, cruise=config["name"], serial=serial)
    db.save_filter_params(new_db_path, results2.filter_params())
    if config["db_file"]:
        db.copy_gating(config["db_file"], new_db_path)
        db.copy_sfl(config["db_file"], new_db_path)

    t2 = timer()
    logger.info("Round 2 completed in %s sec", t2 - t1)

    logger.info("Bead finding completed in %s sec", t2 - t0)


@cli.command("config")
def config_cmd():
    config = resources.files("beadclust").joinpath("data/config-template.yml").read_text(encoding="utf-8")
    sys.stdout.write(config)


@cli.command("version")
def version_cmd():
    click.echo(metadata.version(__package__))
