from importlib import resources
import logging
from pathlib import Path
from typing import Any, Union

import pandas as pd

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)


def get_filter_calibration_slopes(serial: str) -> pd.Series:
    logger.debug("reading filter calibration slopes file")
    with resources.files("beadclust").joinpath("data/seaflow_filter_slopes.csv").open("r", encoding="utf-8") as f:
        all_slopes = pd.read_csv(f)
    all_slopes["ins"] = all_slopes["ins"].astype(str)
    found = all_slopes[all_slopes["ins"] == serial]
    if len(found) == 0:
        raise ValueError(f"serial='{serial}' not found")
    if len(found) > 1:
        raise ValueError(f"duplicate slope entries for serial={serial}")
    slopes = found.squeeze()
    assert isinstance(slopes, pd.Series)
    return slopes


def read_config(config_file: Union[Path, str], template_data: dict[str, str]) -> tuple[str, dict[str, Any]]:
    p = Path(config_file)
    env = Environment(
        loader=FileSystemLoader(p.parents[0]),
        autoescape=select_autoescape()
    )
    template = env.get_template(p.name)
    template_text = template.render(template_data)
    return (template_text, yaml.safe_load(template_text))
