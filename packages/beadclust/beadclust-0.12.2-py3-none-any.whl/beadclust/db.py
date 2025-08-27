from __future__ import annotations
import logging
import sqlite3
import uuid
from typing import TYPE_CHECKING, Union

import numpy as np
import pandas as pd
import seaflowpy as sfp

if TYPE_CHECKING:
    from pathlib import Path

logger = logging.getLogger(__name__)


def df_sql_insert(df: pd.DataFrame, table: str, con: sqlite3.Connection):
    values_str = ", ".join([":" + f for f in df.columns])
    sql_insert = f"INSERT OR REPLACE INTO {table} VALUES ({values_str})"
    values = df.to_dict("index").values()
    with con:
        con.executemany(sql_insert, values)


def save_filter_params(dbpath: Union[Path, str], fp: pd.DataFrame) -> pd.DataFrame:
    sfp.db.create_db(dbpath)

    cols = [
        "id",
        "date",
        "quantile",
        "beads_fsc_small",
        "beads_D1",
        "beads_D2",
        "width",
        "notch_small_D1",
        "notch_small_D2",
        "notch_large_D1",
        "notch_large_D2",
        "offset_small_D1",
        "offset_small_D2",
        "offset_large_D1",
        "offset_large_D2"
    ]
    # Prepare each timepoint for db insertion
    def add_date_id(x):
        x.insert(0, "id", str(uuid.uuid4()))
        x.insert(1, "date", x.name.isoformat(timespec="seconds"))
        return x

    fp_insert_df = (
        fp.groupby(level=0)
            .apply(add_date_id)
            .reset_index(drop=True)
    )
    # Insert into filter table
    with sqlite3.connect(dbpath) as con:
        df_sql_insert(fp_insert_df[cols], "filter", con)

    # Insert into filter_plan table
    plan_insert_df = fp_insert_df.query("quantile == 2.5")[["date", "id"]]
    plan_insert_df.rename({"date": "start_date", "id": "filter_id"}, inplace=True)
    with sqlite3.connect(dbpath) as con:
        df_sql_insert(plan_insert_df, "filter_plan", con)


def save_metadata(dbpath: Union[Path, str], cruise: str, serial: str):
    sfp.db.create_db(dbpath)
    with sqlite3.connect(dbpath) as con:
        df_sql_insert(
            pd.DataFrame({"cruise": [cruise], "inst": [serial]}),
            "metadata",
            con
        )


def copy_gating(dbpath_src: Union[Path, str], dbpath_dest: Union[Path, str]):
    """Copy gating, poly, gating_plan tables from db1 to db2"""
    sfp.db.create_db(dbpath_dest)
    with sqlite3.connect(dbpath_src) as con_src:
        with sqlite3.connect(dbpath_dest) as con_dest:
            # gating table
            df_sql_insert(
                pd.read_sql("SELECT * FROM gating ORDER BY ROWID", con_src),
                "gating",
                con_dest
            )
            # gating_plan table
            # Source may be an older DB without an explicit gating_plan table.
            # Create from implied plan in vct tables entries.
            try:
                gating_plan = pd.read_sql("SELECT * FROM gating_plan ORDER BY ROWID", con_src)
            except pd.errors.DatabaseError:
                gating_plan = gating_plan_from_vct(dbpath_src)
            df_sql_insert(
                gating_plan,
                "gating_plan",
                con_dest
            )
            # poly table
            df_sql_insert(
                pd.read_sql("SELECT * FROM poly ORDER BY ROWID", con_src),
                "poly",
                con_dest
            )


def gating_plan_from_vct(dbpath: Union[Path, str]) -> pd.DataFrame:
    with sqlite3.connect(dbpath) as con:
        vct_table = pd.read_sql(
            'select vct.file, sfl.date, vct.gating_id from vct INNER JOIN sfl on vct.file = sfl.file',
             con
        )
    vct_table = vct_table.sort_values(by=["date"])
    # Test that there's only one gating_id per date
    by_date = vct_table.groupby("date").apply(lambda x: len(x["gating_id"].unique()))
    # Indices where there are more than one gating_id per date
    too_many_gating_ids = np.flatnonzero(by_date > 1)
    if len(too_many_gating_ids) > 0:
        logger.warning(
            "%s dates have multiple gating IDs, first = %s",
            len(too_many_gating_ids), too_many_gating_ids[0]
        )
    gating_sections = (vct_table.gating_id != vct_table.gating_id.shift()).cumsum()
    plan = vct_table.groupby(gating_sections).agg(
        start_date=("date", "min"),
        gating_id=("gating_id", "first")
    )
    return plan


def copy_sfl(dbpath_src: Union[Path, str], dbpath_dest: Union[Path, str]):
    """Copy sfl table"""
    sfp.db.create_db(dbpath_dest)
    with sqlite3.connect(dbpath_src) as con_src:
        with sqlite3.connect(dbpath_dest) as con_dest:
            df_sql_insert(
                pd.read_sql("SELECT * FROM sfl ORDER BY date", con_src),
                "sfl",
                con_dest
            )


def get_serial(db_file: Union[Path, str]) -> str:
    """Return serial sqlite3 SeaFlow database"""
    with sqlite3.connect(db_file) as con:
        serial = str(pd.read_sql_query("SELECT inst FROM metadata", con).loc[0, "inst"])
    return serial


def get_filter_params(db_file: Union[Path, str]) -> pd.DataFrame:
    """Return filter parameters from sqlite3 SeaFlow database"""
    with sqlite3.connect(db_file) as con:
        db_filter_params = pd.read_sql_query("SELECT * FROM filter", con)
    return db_filter_params
