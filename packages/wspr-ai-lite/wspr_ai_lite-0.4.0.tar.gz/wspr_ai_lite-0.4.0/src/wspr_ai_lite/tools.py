from __future__ import annotations
"""
Utility CLI (Click-based) for wspr-ai-lite.

This module provides a Click command group you can extend with small, focused
tools (e.g., `stats`, `verify`, future `dump`, `top`, etc.).

Usage examples (once registered as an entry point):
    wspr-ai-lite-tools --db data/wspr.duckdb stats
    wspr-ai-lite-tools --db data/wspr.duckdb verify --strict
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

import sys
import click
import duckdb

# Reuse the canonical schema creator
from .ingest import ensure_table as ensure_spots_table


# ----------------------------
# CLI context
# ----------------------------

@dataclass
class Ctx:
    db: Path
    read_only: bool


pass_ctx = click.make_pass_decorator(Ctx)


def _open_conn(db: Path, read_only: bool) -> duckdb.DuckDBPyConnection:
    """Open a DuckDB connection with the desired access mode."""
    if read_only:
        return duckdb.connect(str(db), read_only=True)
    # Ensure parent exists when writable
    db.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db), read_only=False)
    ensure_spots_table(con)
    return con


# ----------------------------
# Click group
# ----------------------------

@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--db",
    type=click.Path(path_type=Path),
    default=Path("data/wspr.duckdb"),
    show_default=True,
    help="Path to the DuckDB file.",
)
@click.option(
    "--read-only/--rw",
    default=True,
    show_default=True,
    help="Open the database in read-only (default) or read-write mode.",
)
@click.version_option(message="%(prog)s %(version)s")
@click.pass_context
def cli(ctx: click.Context, db: Path, read_only: bool) -> None:
    """
    wspr-ai-lite utility commands.

    Add new subcommands below with @cli.command().
    """
    ctx.obj = Ctx(db=db, read_only=read_only)


# ----------------------------
# stats
# ----------------------------

@cli.command()
@pass_ctx
def stats(ctx: Ctx) -> None:
    """Show quick dataset stats (rows, time range, distinct stations, bands)."""
    try:
        with _open_conn(ctx.db, ctx.read_only) as con:
            # Basic presence
            tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
            if "spots" not in tables:
                click.echo("spots table not found.", err=True)
                sys.exit(2)

            rows = con.execute("SELECT COUNT(*) FROM spots").fetchone()[0]
            tmin, tmax = con.execute(
                "SELECT MIN(timestamp), MAX(timestamp) FROM spots"
            ).fetchone()

            num_rx = con.execute(
                "SELECT COUNT(DISTINCT reporter) FROM spots"
            ).fetchone()[0]
            num_tx = con.execute(
                "SELECT COUNT(DISTINCT tx_call) FROM spots"
            ).fetchone()[0]
            bands = [
                r[0]
                for r in con.execute(
                    "SELECT DISTINCT band_code FROM spots ORDER BY band_code"
                ).fetchall()
            ]

        click.echo(f"DB: {ctx.db}")
        click.echo(f"Rows: {rows:,}")
        click.echo(f"Time range: {tmin} → {tmax}")
        click.echo(f"Distinct reporters: {num_rx:,}")
        click.echo(f"Distinct tx_calls: {num_tx:,}")
        click.echo(f"Band codes: {bands}")

    except Exception as e:
        click.echo(f"[stats] error: {e}", err=True)
        sys.exit(1)


# ----------------------------
# verify
# ----------------------------

@cli.command()
@click.option("--strict/--no-strict", default=True, show_default=True,
              help="Require exact presence of canonical columns.")
@click.option("--explain", is_flag=True, help="Print discovered column names.")
@pass_ctx
def verify(ctx: Ctx, strict: bool, explain: bool) -> None:
    """
    Verify the 'spots' table matches the canonical schema.

    - In strict mode: fails if any canonical column is missing.
    - Prints helpful diagnostics when schema looks legacy/numeric.
    """
    canonical = {
        "spot_id","timestamp","reporter","reporter_grid","snr_db","freq_mhz",
        "tx_call","tx_grid","power_dbm","drift_hz_per_min","distance_km",
        "azimuth_deg","band_code","rx_version","code"
    }
    legacy_hint = {"ts","band","txcall","snr","freq","year","month"}

    with _open_conn(ctx.db, read_only=True) as con:
        # Ensure table exists
        tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
        if "spots" not in tables:
            click.echo("verify: FAIL\n - table 'spots' not found", err=True)
            raise SystemExit(2)

        info = con.execute("PRAGMA table_info('spots')").fetchall()
        # DuckDB: (column_id, column_name, column_type, null, key, default, extra)
        colnames = [row[1] for row in info]
        colset = set(colnames)

        if explain:
            click.echo(f"[verify] found columns: {colnames}")

        # Canonical?
        if canonical.issubset(colset):
            if strict:
                # Could also check for unexpected columns, but schema allows extras.
                click.echo("verify: OK")
            else:
                click.echo("verify: OK (non-strict)")
            return

        # Obvious legacy/numeric hints
        if not legacy_hint.isdisjoint(colset):
            missing = sorted(list(canonical - colset))
            click.echo("verify: FAIL", err=True)
            click.echo(" - schema appears to be legacy (named cols like ts/band/txcall).", err=True)
            click.echo(f" - missing canonical columns: {missing}", err=True)
            click.echo(" - run: wspr-ai-lite-tools migrate", err=True)
            raise SystemExit(3)

        if all(str(n).isdigit() for n in colnames):
            click.echo("verify: FAIL", err=True)
            click.echo(" - schema appears to be numeric/positional (columns named '0','1',...)", err=True)
            click.echo(" - run: wspr-ai-lite-tools migrate", err=True)
            raise SystemExit(3)

        # Generic failure: show what we found vs. expected
        missing = sorted(list(canonical - colset))
        click.echo("verify: FAIL", err=True)
        click.echo(f" - missing columns: {missing}", err=True)
        click.echo(f" - found columns: {colnames}", err=True)
        raise SystemExit(3)


@cli.command()
@click.option("--backup/--no-backup", default=True, show_default=True,
              help="Create a file copy '<db>.bak' before migrating.")
@pass_ctx
def migrate(ctx: Ctx, backup: bool) -> None:
    """
    Migrate an existing 'spots' table to the canonical schema.

    Handles:
      1) Canonical (no-op)
      2) Legacy named columns (ts/band/txcall/snr/freq/year/month)
      3) Numeric/positional columns ('0','1',...,'14') from headerless inserts

    Strategy: read into pandas, normalize, recreate table with canonical columns.
    """
    db = ctx.db

    if backup:
        bak = db.with_suffix(db.suffix + ".bak")
        try:
            bak.write_bytes(db.read_bytes())
            click.echo(f"[migrate] backup created: {bak}")
        except Exception as e:
            click.echo(f"[migrate] backup skipped ({e})")

    with _open_conn(db, read_only=False) as con:
        tables = {r[0] for r in con.execute("SHOW TABLES").fetchall()}
        if "spots" not in tables:
            click.echo("No table named 'spots' found.", err=True)
            raise SystemExit(2)

        info = con.execute("PRAGMA table_info('spots')").fetchall()
        # DuckDB PRAGMA table_info cols: (cid, name, type, etc.). Name is at index 1.
        colnames = [row[1] for row in info]
        colset = set(colnames)

        canonical = {
            "spot_id","timestamp","reporter","reporter_grid","snr_db","freq_mhz",
            "tx_call","tx_grid","power_dbm","drift_hz_per_min","distance_km",
            "azimuth_deg","band_code","rx_version","code"
        }
        legacy_hint = {"ts","band","txcall","snr","freq","year","month"}

        # 1) Already canonical
        if canonical.issubset(colset):
            click.echo("Already in canonical schema. Nothing to do.")
            return

        # Helper: build canonical DataFrame from various old shapes
        import pandas as pd
        from .ingest import band_code_from_freq_mhz  # reuse your canonical helper

        def _from_legacy_named(df: pd.DataFrame) -> pd.DataFrame:
            # Expected legacy names present: ts, band, txcall, snr, freq, reporter, reporter_grid, tx_grid
            out = pd.DataFrame()
            out["spot_id"] = pd.Series(pd.NA, dtype="Int64")  # generate later
            out["timestamp"] = pd.to_datetime(df["ts"], utc=True).dt.tz_localize(None)
            out["reporter"] = df["reporter"].astype("string").str.strip().str.upper()
            out["reporter_grid"] = df["reporter_grid"].astype("string").str.strip().str.upper()
            out["snr_db"] = df["snr"].astype("Int64")
            out["freq_mhz"] = df["freq"].astype("float64")
            out["tx_call"] = df["txcall"].astype("string").str.strip().str.upper()
            out["tx_grid"] = df["tx_grid"].astype("string").str.strip().str.upper()
            out["power_dbm"] = pd.Series(pd.NA, dtype="Int64")
            out["drift_hz_per_min"] = pd.Series(pd.NA, dtype="Int64")
            out["distance_km"] = pd.Series(pd.NA, dtype="Int64")
            out["azimuth_deg"] = pd.Series(pd.NA, dtype="Int64")
            out["band_code"] = out["freq_mhz"].map(band_code_from_freq_mhz).astype("Int64")
            out["rx_version"] = pd.Series(pd.NA, dtype="string")
            out["code"] = pd.Series(0, dtype="Int64")
            # generate spot_id as a stable row number (not true original IDs, but OK for legacy data)
            out["spot_id"] = pd.RangeIndex(1, len(out) + 1, dtype="Int64")
            return out

        def _from_numeric_positional(df: pd.DataFrame) -> pd.DataFrame:
            # Map by position based on historical CSV order:
            #  0: spot_id
            #  1: unixtime (sec)
            #  2: tx_call
            #  3: tx_grid
            #  4: snr
            #  5: freq_mhz
            #  6: reporter
            #  7: reporter_grid
            #  8: power_dbm (optional)
            #  9: drift_hz_per_min (optional)
            # 10: distance_km (optional)
            # 11: azimuth_deg (optional)
            # 12: band_archive (ignored)
            # 13: rx_version (optional)
            # 14: code (optional)
            out = pd.DataFrame()
            # Access numeric columns safely (they will be strings like "0","1",... in pandas)
            g = lambda i: str(i) if str(i) in df.columns else None

            # spot_id (may be missing or NA)
            c0 = g(0)
            if c0:
                out["spot_id"] = df[c0].astype("Int64")
            else:
                out["spot_id"] = pd.RangeIndex(1, len(df) + 1, dtype="Int64")

            # timestamp from Unix seconds in col 1
            c1 = g(1)
            if c1:
                out["timestamp"] = pd.to_datetime(df[c1], unit="s", utc=True).dt.tz_localize(None)
            else:
                out["timestamp"] = pd.NaT

            # Strings -> uppercase
            def _upper_safe(s):
                return s.astype("string").str.strip().str.upper()

            c6 = g(6); out["reporter"] = _upper_safe(df[c6]) if c6 else pd.Series(pd.NA, dtype="string")
            c7 = g(7); out["reporter_grid"] = _upper_safe(df[c7]) if c7 else pd.Series(pd.NA, dtype="string")
            c4 = g(4); out["snr_db"] = df[c4].astype("Int64") if c4 else pd.Series(pd.NA, dtype="Int64")
            c5 = g(5); out["freq_mhz"] = df[c5].astype("float64") if c5 else pd.Series(pd.NA, dtype="float64")
            c2 = g(2); out["tx_call"] = _upper_safe(df[c2]) if c2 else pd.Series(pd.NA, dtype="string")
            c3 = g(3); out["tx_grid"] = _upper_safe(df[c3]) if c3 else pd.Series(pd.NA, dtype="string")
            c8 = g(8); out["power_dbm"] = df[c8].astype("Int64") if c8 else pd.Series(pd.NA, dtype="Int64")
            c9 = g(9); out["drift_hz_per_min"] = df[c9].astype("Int64") if c9 else pd.Series(pd.NA, dtype="Int64")
            c10 = g(10); out["distance_km"] = df[c10].astype("Int64") if c10 else pd.Series(pd.NA, dtype="Int64")
            c11 = g(11); out["azimuth_deg"] = df[c11].astype("Int64") if c11 else pd.Series(pd.NA, dtype="Int64")
            # band_code recomputed from freq
            out["band_code"] = out["freq_mhz"].map(band_code_from_freq_mhz).astype("Int64")
            c13 = g(13); out["rx_version"] = df[c13].astype("string").str.strip().replace({"": pd.NA}) if c13 else pd.Series(pd.NA, dtype="string")
            c14 = g(14); out["code"] = df[c14].fillna(0).astype("Int64") if c14 else pd.Series(0, dtype="Int64")

            # final order
            out = out[[
                "spot_id","timestamp","reporter","reporter_grid","snr_db","freq_mhz",
                "tx_call","tx_grid","power_dbm","drift_hz_per_min","distance_km",
                "azimuth_deg","band_code","rx_version","code"
            ]]
            # drop obvious invalid rows
            out = out.dropna(subset=["timestamp"])
            return out

        # — Detect & load
        df_src = con.execute("SELECT * FROM spots").fetchdf()

        if canonical.issubset(colset):
            click.echo("Already in canonical schema. Nothing to do.")
            return
        elif not legacy_hint.isdisjoint(colset):
            click.echo("[migrate] legacy named schema detected → converting …")
            df_canon = _from_legacy_named(df_src)
        elif all(name.isdigit() for name in colnames):
            click.echo("[migrate] numeric/positional schema detected → converting …")
            df_canon = _from_numeric_positional(df_src)
        else:
            click.echo(
                "Schema is not recognized as legacy, numeric, or canonical.\n"
                f"Found columns: {sorted(colnames)}",
                err=True
            )
            raise SystemExit(3)

        # Recreate table in canonical shape
        from .ingest import ensure_table as ensure_spots_table
        con.execute("DROP TABLE spots")
        ensure_spots_table(con)

        con.register("tmp_spots_df", df_canon)
        con.execute("INSERT INTO spots SELECT * FROM tmp_spots_df")
        con.unregister("tmp_spots_df")

        click.echo(f"[migrate] done. Inserted {len(df_canon):,} rows into canonical 'spots'.")

# ----------------------------
# main
# ----------------------------



if __name__ == "__main__":
    cli()
