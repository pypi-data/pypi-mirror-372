from typing import Optional

import pandas as pd


def from_bead_coords(bead_coords: pd.DataFrame, slopes: pd.Series, width: float) -> pd.DataFrame:
    bead_coords = bead_coords.reset_index(drop=True)  # just in case we indexed on something like date
    inflection_point = pd.DataFrame(
        {
            "fsc": bead_coords.loc[0, ["fsc_small_1Q", "fsc_small_2Q", "fsc_small_3Q"]].to_numpy(),
            "D1": bead_coords.loc[0, ["D1_3Q", "D1_2Q", "D1_1Q"]].to_numpy(),
            "D2": bead_coords.loc[0, ["D2_3Q", "D2_2Q", "D2_1Q"]].to_numpy(),
        }
    )
    fp = from_ip(inflection_point, slopes, width)
    return fp


def from_ip(ip: pd.DataFrame, slopes: pd.Series, width: float = 5000) -> pd.DataFrame:
    """
    Convert inflection point dataframe to filtering params.

    Parameter
    ---------
    ip: pandas.DataFrame
        Inflection points for 1 micron beads. Should have three columns:
        fsc_small, D1, D2. Each column has three values for the three filtering
        quantiles of 2.5, 50, 97.5. For fsc_small these are the 25%, 50%, and
        75% quantile values for bead EVT points. For D1 and D2 the order is
        is reversed to 75%, 50%, 25% quantile values.
    slopes: pandas.Series
        Calibration slopes for SeaFlow filtering of one instrument.
    width: int, 5000
        Filtering parameter "width", tolerance in D1 D2 equality.

    Returns
    -------
    pandas.DataFrame
        Filtering parameter dataframe ready to be saved to a popcycle database.
        None if any values in ip are missing.
    """
    if ip.isnull().to_numpy().any():
        return make_empty_dataframe()

    params = []
    qs = [
        {"quant": 2.5, "suffix": "_2.5"},
        {"quant": 50.0, "suffix": ""},
        {"quant": 97.5, "suffix": "_97.5"},
    ]
    for i, q in enumerate(qs):
        suffix = q["suffix"]
        # Small particles
        offset_small_D1 = 0
        offset_small_D2 = 0
        notch_small_D1 = _round(ip.loc[i, "D1"] / ip.loc[i, "fsc"], 3)
        notch_small_D2 = _round(ip.loc[i, "D2"] / ip.loc[i, "fsc"], 3)

        # Large particles
        notch_large_D1 = _round(slopes[f"notch.large.D1{suffix}"], 3)
        notch_large_D2 = _round(slopes[f"notch.large.D2{suffix}"], 3)
        offset_large_D1 = _round(ip.loc[i, "D1"] - notch_large_D1 * ip.loc[i, "fsc"])
        offset_large_D2 = _round(ip.loc[i, "D2"] - notch_large_D2 * ip.loc[i, "fsc"])

        row = make_empty_dataframe(
            data=[
                [
                    pd.NaT,
                    q["quant"],
                    int(ip.loc[i, "fsc"]),
                    int(ip.loc[i, "D1"]),
                    int(ip.loc[i, "D2"]),
                    width,
                    notch_small_D1,
                    notch_small_D2,
                    notch_large_D1,
                    notch_large_D2,
                    offset_small_D1,
                    offset_small_D2,
                    offset_large_D1,
                    offset_large_D2,
                ]
            ],
        )
        params.append(row)

    return pd.concat(params)


def params2ip(params: pd.DataFrame):
    """
    Convert filtering parameters to inflection point data frame.
    """
    col_rename = {"beads_fsc_small": "fsc_small", "beads_D1": "D1", "beads_D2": "D2"}
    ip = params.rename(columns=col_rename)[["quantile", "fsc_small", "D1", "D2"]]
    ip = ip.sort_values(by=["quantile"])
    ip = ip.reset_index(drop=True)
    return ip


def make_empty_dataframe(data: Optional[list[list[float]]] = None) -> pd.DataFrame:
    columns = [
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
        "offset_large_D2",
    ]
    df = pd.DataFrame(columns=columns, data=data)
    # Make all numeric columns float64 to match db schema
    df = df.astype({c: "float64" for c in columns[1:]})
    df["date"] = pd.to_datetime(df["date"]).dt.tz_localize("UTC")
    return df


def _round(x: float, prec: int = 0):
    """Return x rounded to prec number of decimals."""
    if prec == 0:
        return int(x)
    return float("{1:.{0}f}".format(prec, x))
