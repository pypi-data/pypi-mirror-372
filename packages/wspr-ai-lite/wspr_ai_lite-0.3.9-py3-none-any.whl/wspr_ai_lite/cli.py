from __future__ import annotations

"""
Click CLI for wspr-ai-lite.

Subcommands:
  - ingest : download/parse monthly archives and insert into DuckDB
  - ui     : launch the Streamlit app

This module must export `cli` for the project entry point:
  wspr-ai-lite = "wspr_ai_lite.cli:cli"
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Optional

import click
import duckdb

from . import __version__
from .ingest import ingest_month, month_range


# ----------------------------- helpers -----------------------------

def _app_path() -> Path:
    """
    Resolve the Streamlit app path.

    1) Packaged wheel: wspr_ai_lite/wspr_ai_lite.py (alongside this file)
    2) Dev fallback:   repo-root/app/wspr_ai_lite.py
    """
    packaged = Path(__file__).with_name("wspr_ai_lite.py")
    if packaged.exists():
        return packaged
    # dev fallback (useful when running from source)
    return Path(__file__).resolve().parents[2] / "app" / "wspr_ai_lite.py"


# ----------------------------- CLI root -----------------------------

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, "-V", "--version", prog_name="wspr-ai-lite")
def cli() -> None:
    """wspr-ai-lite command line interface."""
    # group entry point (no-op)
    pass


# ----------------------------- commands -----------------------------

@cli.command("ingest")
@click.option("--from", "start", required=True, help="Start month, YYYY-MM (e.g., 2014-07)")
@click.option("--to", "end", required=True, help="End month, YYYY-MM (inclusive)")
@click.option("--db", "db_path", default="data/wspr.duckdb", show_default=True, help="DuckDB file path")
@click.option("--cache", default=".cache", show_default=True, help="Directory to store/download monthly .csv.gz files")
@click.option("--offline", is_flag=True, default=False, help="Use cache only; do not download if missing")
def cmd_ingest(start: str, end: str, db_path: str, cache: str, offline: bool) -> None:
    """
    Ingest monthly WSPRNet archives into a local DuckDB.
    """
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    total = 0
    with duckdb.connect(db_path) as con:
        for y, m in month_range(start, end):
            total += ingest_month(con, y, m, cache_dir=cache, offline=offline)
    click.secho(f"[OK] inserted rows: {total:,}", fg="green")


@cli.command("ui")
@click.option("--db", "db_path", default="data/wspr.duckdb", show_default=True, help="DuckDB file path")
@click.option("--port", default=8501, show_default=True, type=int, help="Streamlit port")
def cmd_ui(db_path: str, port: int) -> None:
    """
    Launch the Streamlit UI against a DuckDB database.
    """
    app_path = _app_path()
    if not app_path.exists():
        click.secho(
            f"ERROR: cannot find Streamlit app at {app_path}\n"
            "The package app file may be missing from the install.",
            fg="red",
            err=True,
        )
        raise SystemExit(1)

    # set env for the app to pick up DB path
    env = os.environ.copy()
    env["WSPR_DB_PATH"] = db_path

    try:
        code = subprocess.call(
            [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(port)],
            env=env,
        )
    except ModuleNotFoundError:
        click.secho(
            "ERROR: Streamlit is not installed.\nInstall with:\n\n    pip install streamlit\n",
            fg="red",
            err=True,
        )
        raise SystemExit(1)

    raise SystemExit(code)


# ----------------------------- deprecated alias -----------------------------

def deprecated_entrypoint() -> None:
    """Shim for old command name `wspr-lite`."""
    click.secho(
        "WARNING: The `wspr-lite` entrypoint is deprecated.\n"
        "Please use the new command: `wspr-ai-lite`.\n",
        fg="yellow",
    )
    cli()  # delegate to the Click group


if __name__ == "__main__":
    cli()
