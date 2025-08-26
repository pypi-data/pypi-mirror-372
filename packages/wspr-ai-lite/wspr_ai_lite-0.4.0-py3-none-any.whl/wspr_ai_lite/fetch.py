from __future__ import annotations
"""
Offline fetcher for WSPR monthly archives.

Library usage:
  from wspr_ai_lite.fetch import fetch_range, fetch_one

Optional module-local CLI (for convenience):
  python -m wspr_ai_lite.fetch --from 2014-07 --to 2014-09 --cache .cache/wspr --skip-existing
"""

from pathlib import Path
from typing import List
import requests
import click

from .ingest import month_range, archive_url  # reuse shared helpers


def cache_path(cache_dir: Path, year: int, month: int) -> Path:
    """Return the canonical cache path for a given year-month; ensure directory exists."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"wsprspots-{year:04d}-{month:02d}.csv.gz"


def fetch_one(year: int, month: int, cache_dir: Path, skip_existing: bool = True) -> Path:
    """
    Download one monthly archive into cache_dir.

    Respects skip_existing to avoid re-downloading.
    Returns the local path.
    """
    path = cache_path(cache_dir, year, month)
    if skip_existing and path.exists():
        print(f"[skip] {path.name} (exists)")
        return path

    url = archive_url(year, month)
    print(f"GET {url}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path.write_bytes(r.content)
    print(f"[ok]  {path.name} ({len(r.content):,} bytes)")
    return path


def fetch_range(start: str, end: str, cache_dir: Path, skip_existing: bool = True) -> List[Path]:
    """
    Fetch a continuous inclusive [start..end] range like '2014-07' to '2014-09'
    into cache_dir. Returns list of downloaded file paths (existing + new).
    """
    paths: List[Path] = []
    for y, m in month_range(start, end):
        paths.append(fetch_one(y, m, cache_dir, skip_existing=skip_existing))
    return paths


# ----------------------------
# Optional Click CLI (module-local)
# ----------------------------

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--from", "start", required=True, help="Start month (YYYY-MM)")
@click.option("--to", "end", required=True, help="End month (YYYY-MM)")
@click.option("--cache", type=click.Path(path_type=Path), default=Path(".cache"), show_default=True)
@click.option("--skip-existing/--force", default=True, show_default=True,
              help="Skip files that already exist in cache (or force re-download)")
@click.version_option(version=__version__, prog_name="wspr-ai-lite")
def cli(start: str, end: str, cache: Path, skip_existing: bool) -> None:
    """Download monthly .csv.gz archives into a cache directory."""
    paths = fetch_range(start, end, cache, skip_existing=skip_existing)
    click.secho(f"[done] staged {len(paths)} file(s) in {cache}", fg="green")


if __name__ == "__main__":
    cli()
