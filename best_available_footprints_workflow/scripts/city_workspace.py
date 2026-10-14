"""Shared helpers for locating a prepared city's data under a user-controlled root."""

from __future__ import annotations

import argparse
import json
import os
import re
import unicodedata
from dataclasses import dataclass
from pathlib import Path


DATA_ROOT_ENV_VAR = "BAFW_DATA_ROOT"


def slugify(value: str) -> str:
    text = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-zA-Z0-9]+", "_", text).strip("_").lower()


def resolve_data_root(cli_value: str | None) -> Path:
    value = cli_value or os.environ.get(DATA_ROOT_ENV_VAR)
    if not value:
        raise SystemExit(
            f"No data root configured. Pass --data-root or set {DATA_ROOT_ENV_VAR}."
        )
    return Path(value).expanduser().resolve()


def add_data_root_arg(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--data-root",
        help=f"Root directory for prepared city data (or set {DATA_ROOT_ENV_VAR})",
    )


@dataclass
class CityPaths:
    slug: str
    data_root: Path
    city_dir: Path
    inputs_dir: Path
    sources_dir: Path
    outputs_dir: Path
    metadata: dict


def load_city(slug: str, data_root: Path) -> CityPaths:
    city_dir = data_root / slug
    metadata_path = city_dir / "inputs/metadata.json"
    if not metadata_path.exists():
        raise SystemExit(
            f"No prepared city at {city_dir}. Run prepare_city.py --city-slug {slug} "
            f"--data-root {data_root} first."
        )
    metadata = json.loads(metadata_path.read_text())
    return CityPaths(
        slug=slug,
        data_root=data_root,
        city_dir=city_dir,
        inputs_dir=city_dir / "inputs",
        sources_dir=city_dir / "sources",
        outputs_dir=city_dir / "outputs",
        metadata=metadata,
    )


def skip_existing(path: Path, force: bool) -> bool:
    if path.exists() and not force:
        print(f"Existing: {path}")
        return True
    return False
