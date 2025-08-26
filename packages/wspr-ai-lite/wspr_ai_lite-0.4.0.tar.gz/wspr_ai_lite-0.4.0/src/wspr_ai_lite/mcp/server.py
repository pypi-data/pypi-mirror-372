# src/wspr_ai_lite/mcp/server.py
from __future__ import annotations
"""
WSPR MCP server (tools) for wspr-ai-lite.

This module exposes a set of read-only tools over the canonical `spots` table.
It is designed to be imported and registered by an MCP-capable runtime.
Nothing is imported at package top-level that would force optional dependencies
beyond DuckDB and the Python stdlib.

Environment
-----------
- WSPR_DB (optional): path to the DuckDB file. Defaults to "data/wspr.duckdb".

Safety & Conventions
--------------------
- All queries are parameterized to avoid SQL injection.
- Inputs that represent callsigns are uppercased server-side.
- Time filters are expected as ISO-8601 strings (e.g., "2014-07-01T00:00:00Z").
  We accept a few common variants and normalize to UTC.
- Timestamps returned to clients are always ISO-8601 with "Z" (UTC).
- Return values are plain JSON-serializable dicts/lists.

Dependencies
------------
- `duckdb` (runtime)
- An MCP framework that provides a `@tool` decorator. We keep the import
  name `from mcp import tool` as in your snippet; replace if your framework
  uses a different import path.

Manifest loading
----------------
If you need to ship and serve a manifest, keep `manifest.json` in the same
subpackage and add this to pyproject:

    [tool.setuptools.package-data]
    "wspr_ai_lite.mcp" = ["manifest.json"]

Then use `load_manifest()` below to read it in a wheel-safe way.
"""

# stdlib
from pathlib import Path
from wspr_ai_lite.ingest import ensure_table  # reuse schema creator
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import json
import os
import signal
import subprocess
import sys
import time

# third-party
import duckdb
import click

from .. import __version__  # reuse package version

# --- Optional MCP decorator shim ---------------------------------
# Try the real MCP decorator; fall back to a no-op so the server/CLI
# can run even if `mcp` isn’t installed.
try:
    from mcp import tool  # real decorator
except Exception:  # pragma: no cover
    def tool(*args, **kwargs):
        def _wrap(fn):
            return fn
        return _wrap

# ---------------------------------------------------------------------
# Configuration / connection helpers
# ---------------------------------------------------------------------

DB_PATH = os.environ.get("WSPR_DB", "data/wspr.duckdb")
PID_FILE = Path(".wspr_mcp.pid")  # or Path(DB_PATH).with_suffix(".mcp.pid")

def conn(read_only: bool = True, init: bool = False) -> duckdb.DuckDBPyConnection:
    """
    Open a DuckDB connection to the configured database.

    Parameters
    ----------
    read_only : bool, default=True
        Open the database in read-only mode.
        If False, allows creating/writing tables.
    init : bool, default=False
        If True and the database is opened writable, ensure
        the canonical WSPR `spots` schema exists.

    Returns
    -------
    duckdb.DuckDBPyConnection
        The opened DuckDB connection.
    """
    if read_only and init:
        raise ValueError("Cannot request both read_only and init=True")

    con = duckdb.connect(DB_PATH, read_only=read_only)

    if init and not read_only:
        # Lazy import to avoid cycles
        from wspr_ai_lite.ingest import ensure_table
        ensure_table(con)
        print("[mcp] created/verified schema in database")

    return con

def load_manifest() -> Dict[str, Any]:
    """
    Load `manifest.json` shipped in this subpackage (wheel-safe).

    Returns
    -------
    dict
        Parsed JSON manifest as a Python dict.

    Raises
    ------
    FileNotFoundError
        If the manifest is not present in the installed package.
    json.JSONDecodeError
        If the manifest is not valid JSON.
    """
    p = files("wspr_ai_lite.mcp").joinpath("manifest.json")
    return json.loads(p.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------
# Utilities: time parsing / normalization / row conversion
# ---------------------------------------------------------------------

_ISO_INPUT_FORMATS: Tuple[str, ...] = (
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d",
)


def _parse_iso_utc(s: str) -> Optional[str]:
    """
    Parse an incoming ISO-ish string and normalize to UTC Z-string.

    Parameters
    ----------
    s : str
        Input time string.

    Returns
    -------
    Optional[str]
        Normalized ISO-8601 UTC string (e.g., "2014-07-01T00:00:00Z"),
        or None if parsing fails.
    """
    if not s or not isinstance(s, str):
        return None

    # Fast-path: already ends with Z and is parseable by fromisoformat?
    ss = s.strip()
    if ss.endswith("Z"):
        try:
            # Replace Z with +00:00 for fromisoformat
            dt = datetime.fromisoformat(ss.replace("Z", "+00:00"))
            dt = dt.astimezone(timezone.utc)
            return dt.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        except Exception:
            pass

    # Try a few explicit formats
    for fmt in _ISO_INPUT_FORMATS:
        try:
            dt = datetime.strptime(ss, fmt)
            # Assume naive -> UTC
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt.isoformat().replace("+00:00", "Z")
        except Exception:
            continue

    # Last resort: fromisoformat without Z, assume UTC
    try:
        dt2 = datetime.fromisoformat(ss)
        if dt2.tzinfo is None:
            dt2 = dt2.replace(tzinfo=timezone.utc)
        else:
            dt2 = dt2.astimezone(timezone.utc)
        return dt2.isoformat().replace("+00:00", "Z")
    except Exception:
        return None


def _df_records_iso(df) -> List[Dict[str, Any]]:
    """
    Convert a DuckDB DataFrame (fetchdf()) to JSON-serializable records with
    UTC ISO timestamps.

    Parameters
    ----------
    df : pandas.DataFrame

    Returns
    -------
    List[Dict[str, Any]]
    """
    if df.empty:
        return []

    recs: List[Dict[str, Any]] = df.to_dict(orient="records")
    for r in recs:
        ts = r.get("timestamp")
        if isinstance(ts, datetime):
            r["timestamp"] = ts.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
    return recs


# ---------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------

@tool(name="get_summary")
def get_summary() -> Dict[str, Any]:
    """
    Return a quick dataset summary.

    Returns
    -------
    dict
        {
            "rows": int,
            "time_min": str|None,  # ISO UTC
            "time_max": str|None,  # ISO UTC
            "bands": List[int],    # distinct band_code values
            "reporters": int,      # distinct RX callsigns
            "tx_calls": int        # distinct TX callsigns
        }
    """
    with conn() as c:
        rows = c.sql("SELECT COUNT(*) FROM spots").fetchone()[0]
        tmin, tmax = c.sql("SELECT MIN(timestamp), MAX(timestamp) FROM spots").fetchone()
        bands = [r[0] for r in c.sql("SELECT DISTINCT band_code FROM spots ORDER BY band_code").fetchall()]
        reporters = c.sql("SELECT COUNT(DISTINCT reporter) FROM spots").fetchone()[0]
        tx_calls = c.sql("SELECT COUNT(DISTINCT tx_call) FROM spots").fetchone()[0]

    return {
        "rows": int(rows),
        "time_min": tmin.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z") if isinstance(tmin, datetime) else None,
        "time_max": tmax.replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z") if isinstance(tmax, datetime) else None,
        "bands": bands,
        "reporters": int(reporters),
        "tx_calls": int(tx_calls),
    }


@tool(name="query_spots")
def query_spots(
    time_from: Optional[str] = None,
    time_to: Optional[str] = None,
    reporter: Optional[str] = None,
    tx_call: Optional[str] = None,
    band_code: Optional[int] = None,
    snr_min: Optional[int] = None,
    snr_max: Optional[int] = None,
    limit: int = 200,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Query the `spots` table with optional filters and pagination.

    Parameters
    ----------
    time_from, time_to : Optional[str]
        ISO-8601 strings. `time_to` is exclusive (<).
    reporter, tx_call : Optional[str]
        Callsigns (case-insensitive; normalized to uppercase).
    band_code : Optional[int]
        Canonical band code (-1 LF, 0 MF, else int(MHz)).
    snr_min, snr_max : Optional[int]
        SNR bounds in dB (inclusive).
    limit : int
        Max rows to return (1..1000). Defaults to 200.
    offset : int
        Pagination offset (>= 0).

    Returns
    -------
    dict
        {"rows": [ {spot}, ... ]}
    """
    limit = max(1, min(int(limit), 1000))
    offset = max(0, int(offset))

    where: List[str] = []
    params: List[Any] = []

    if time_from:
        tf = _parse_iso_utc(time_from)
        if tf:
            where.append("timestamp >= ?")
            params.append(tf.replace("Z", "+00:00"))
    if time_to:
        tt = _parse_iso_utc(time_to)
        if tt:
            where.append("timestamp < ?")
            params.append(tt.replace("Z", "+00:00"))

    if reporter:
        where.append("reporter = ?")
        params.append(reporter.upper().strip())
    if tx_call:
        where.append("tx_call = ?")
        params.append(tx_call.upper().strip())
    if band_code is not None:
        where.append("band_code = ?")
        params.append(int(band_code))
    if snr_min is not None:
        where.append("snr_db >= ?")
        params.append(int(snr_min))
    if snr_max is not None:
        where.append("snr_db <= ?")
        params.append(int(snr_max))

    base_sql = """
      SELECT spot_id, timestamp, reporter, reporter_grid, snr_db, freq_mhz,
             tx_call, tx_grid, power_dbm, drift_hz_per_min, distance_km,
             azimuth_deg, band_code, rx_version, code
        FROM spots
    """
    if where:
        base_sql += " WHERE " + " AND ".join(where)
    base_sql += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"

    params.extend([limit, offset])

    with conn() as c:
        df = c.execute(base_sql, params).fetchdf()

    return {"rows": _df_records_iso(df)}


@tool(name="top_reporters")
def top_reporters(
    time_from: Optional[str] = None,
    time_to: Optional[str] = None,
    band_code: Optional[int] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Top reporting RX stations by count.

    Parameters
    ----------
    time_from, time_to : Optional[str]
        ISO-8601 bounds. `time_to` is exclusive.
    band_code : Optional[int]
        Restrict to a single band.
    limit : int
        Number of rows (1..200). Defaults to 50.
    """
    limit = max(1, min(int(limit), 200))
    where: List[str] = []
    params: List[Any] = []

    if time_from:
        tf = _parse_iso_utc(time_from)
        if tf:
            where.append("timestamp >= ?")
            params.append(tf.replace("Z", "+00:00"))
    if time_to:
        tt = _parse_iso_utc(time_to)
        if tt:
            where.append("timestamp < ?")
            params.append(tt.replace("Z", "+00:00"))
    if band_code is not None:
        where.append("band_code = ?")
        params.append(int(band_code))

    sql = "SELECT reporter, COUNT(*) AS count FROM spots"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " GROUP BY reporter ORDER BY count DESC LIMIT ?"
    params.append(limit)

    with conn() as c:
        df = c.execute(sql, params).fetchdf()

    items = [{"reporter": str(r["reporter"]), "count": int(r["count"])} for _, r in df.iterrows()]
    return {"items": items}


@tool(name="top_heard")
def top_heard(
    time_from: Optional[str] = None,
    time_to: Optional[str] = None,
    band_code: Optional[int] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Top TX stations by number of distinct reporters (who heard them).

    Parameters
    ----------
    time_from, time_to : Optional[str]
        ISO-8601 bounds. `time_to` is exclusive.
    band_code : Optional[int]
        Restrict to a single band.
    limit : int
        Number of rows (1..200). Defaults to 50.
    """
    limit = max(1, min(int(limit), 200))
    where: List[str] = []
    params: List[Any] = []

    if time_from:
        tf = _parse_iso_utc(time_from)
        if tf:
            where.append("timestamp >= ?")
            params.append(tf.replace("Z", "+00:00"))
    if time_to:
        tt = _parse_iso_utc(time_to)
        if tt:
            where.append("timestamp < ?")
            params.append(tt.replace("Z", "+00:00"))
    if band_code is not None:
        where.append("band_code = ?")
        params.append(int(band_code))

    sql = """
      SELECT tx_call, COUNT(DISTINCT reporter) AS reporters
        FROM spots
    """
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " GROUP BY tx_call ORDER BY reporters DESC LIMIT ?"
    params.append(limit)

    with conn() as c:
        df = c.execute(sql, params).fetchdf()

    items = [{"tx_call": str(r["tx_call"]), "reporters": int(r["reporters"])} for _, r in df.iterrows()]
    return {"items": items}


@tool(name="band_activity")
def band_activity(
    time_from: Optional[str] = None,
    time_to: Optional[str] = None,
    by_day: bool = False,
) -> Dict[str, Any]:
    """
    Aggregate activity by band (optionally by day).

    Parameters
    ----------
    time_from, time_to : Optional[str]
        ISO-8601 bounds. `time_to` is exclusive.
    by_day : bool
        When True, also groups by CAST(timestamp AS DATE).

    Returns
    -------
    dict
        {"items": [{"band_code": int, "day": "YYYY-MM-DD"|None, "count": int}, ...]}
    """
    where: List[str] = []
    params: List[Any] = []

    if time_from:
        tf = _parse_iso_utc(time_from)
        if tf:
            where.append("timestamp >= ?")
            params.append(tf.replace("Z", "+00:00"))
    if time_to:
        tt = _parse_iso_utc(time_to)
        if tt:
            where.append("timestamp < ?")
            params.append(tt.replace("Z", "+00:00"))

    if by_day:
        sql = """
          SELECT band_code, CAST(timestamp AS DATE) AS day, COUNT(*) AS count
            FROM spots
        """
    else:
        sql = "SELECT band_code, NULL AS day, COUNT(*) AS count FROM spots"

    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " GROUP BY band_code" + (", day" if by_day else "") + " ORDER BY band_code, day"

    with conn() as c:
        df = c.execute(sql, params).fetchdf()

    items: List[Dict[str, Any]] = []
    for _, r in df.iterrows():
        day = r["day"]
        items.append(
            {
                "band_code": int(r["band_code"]),
                "day": day.isoformat() if hasattr(day, "isoformat") else None,
                "count": int(r["count"]),
            }
        )
    return {"items": items}


@tool(name="spot_by_id")
def spot_by_id(spot_id: int) -> Dict[str, Any]:
    """
    Fetch a single spot by its primary key.

    Parameters
    ----------
    spot_id : int
        Primary key of the spot.

    Returns
    -------
    dict
        {"row": {...}} or {"row": None}
    """
    sql = """
      SELECT spot_id, timestamp, reporter, reporter_grid, snr_db, freq_mhz,
             tx_call, tx_grid, power_dbm, drift_hz_per_min, distance_km,
             azimuth_deg, band_code, rx_version, code
        FROM spots
       WHERE spot_id = ?
    """

    with conn() as c:
        df = c.execute(sql, [int(spot_id)]).fetchdf()

    if df.empty:
        return {"row": None}

    rec = _df_records_iso(df)[0]
    return {"row": rec}


# ---------------------------------------------------------------------
# MCP: Service help functions implemented as of v.3.0.8
# ---------------------------------------------------------------------

def _read_pid() -> int | None:
    """Read the MCP Pid FIle"""
    try:
        return int(PID_FILE.read_text().strip())
    except Exception:
        return None

def _is_running(pid: int) -> bool:
    """Check if MCP service is running"""
    try:
        os.kill(pid, 0)  # POSIX check
        return True
    except Exception:
        # On Windows, os.kill with 0 isn’t reliable; try a psutil fallback if you want.
        return False

def _terminate_pid(pid: int, timeout: float = 10.0) -> bool:
    """Terminate the PID file"""
    try:
        if os.name == "posix":
            os.kill(pid, signal.SIGTERM)
        else:
            # best-effort cross-platform; you can add psutil for better control
            try:
                import psutil  # optional dep
                psutil.Process(pid).terminate()
            except Exception:
                # Fall back to taskkill on Windows
                if sys.platform.startswith("win"):
                    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], check=False)
        # wait a bit
        t0 = time.time()
        while time.time() - t0 < timeout:
            if not _is_running(pid):
                return True
            time.sleep(0.2)
    except Exception:
        pass
    return not _is_running(pid)

# ---------------------------------------------------------------------
# MCP: Control Groups Functions not implemented as of v.3.0.8
# ---------------------------------------------------------------------

# @click.group()
# def cli() -> None:
#     """wspr-ai-lite MCP server controller."""
#     pass

@cli.command()
@click.option("--db", "db_path", default="data/wspr.duckdb", show_default=True,
              help="Path to DuckDB database file.")
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8765, show_default=True, type=int)
@click.option("--init", is_flag=True, help="Initialize schema if missing (opens DB read-write once).")
def serve(db_path: str, host: str, port: int, init: bool) -> None:
    """Run the MCP server in the foreground (blocking)."""
    # (your existing open/ensure schema code)
    global DB_PATH
    DB_PATH = db_path
    mode = "rw" if init else "ro"
    click.echo(f"[mcp] Using database: {db_path} (mode={mode})")

    try:
        with conn(read_only=not init, init=init) as c:
            _ = c.execute("SELECT COUNT(*) FROM spots").fetchone()
    except Exception as e:
        click.echo(f"[mcp] Error opening database: {e}", err=True)
        raise SystemExit(1)

    # TODO: replace this stub with your real server (uvicorn or MCP runtime)
    click.echo(f"[mcp] Serving on {host}:{port} (Ctrl+C to stop)")
    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        click.echo("[mcp] Shutting down.")

@cli.command()
@click.option("--db", "db_path", default="data/wspr.duckdb", show_default=True)
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8765, show_default=True, type=int)
@click.option("--init", is_flag=True, help="Initialize schema before serving.")
def start(db_path: str, host: str, port: int, init: bool) -> None:
    """Start the MCP server in the background."""
    if PID_FILE.exists():
        pid = _read_pid()
        if pid and _is_running(pid):
            click.secho(f"[mcp] Already running (pid {pid}).", fg="yellow")
            return
        PID_FILE.unlink(missing_ok=True)

    cmd = [sys.executable, "-m", "wspr_ai_lite.mcp.server", "serve",
           "--db", db_path, "--host", host, "--port", str(port)]
    if init:
        cmd.append("--init")

    # Launch detached-ish process
    if os.name == "posix":
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                start_new_session=True)
    else:
        # Windows
        CREATE_NO_WINDOW = 0x08000000
        DETACHED_PROCESS = 0x00000008
        proc = subprocess.Popen(cmd, creationflags=DETACHED_PROCESS | CREATE_NO_WINDOW,
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    PID_FILE.write_text(str(proc.pid))
    click.secho(f"[mcp] Started (pid {proc.pid}).", fg="green")

@cli.command()
def stop() -> None:
    """Stop the MCP server."""
    pid = _read_pid()
    if not pid:
        click.secho("[mcp] Not running (no PID file).", fg="yellow")
        return
    if _terminate_pid(pid):
        PID_FILE.unlink(missing_ok=True)
        click.secho("[mcp] Stopped.", fg="green")
    else:
        click.secho("[mcp] Could not stop process.", fg="red")
        raise SystemExit(1)

@cli.command()
def status() -> None:
    """Show server status."""
    pid = _read_pid()
    if pid and _is_running(pid):
        click.secho(f"[mcp] Running (pid {pid}).", fg="green")
    else:
        click.secho("[mcp] Not running.", fg="yellow")

@cli.command()
@click.option("--db", "db_path", default="data/wspr.duckdb", show_default=True)
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8765, show_default=True, type=int)
@click.option("--init", is_flag=True)
def restart(db_path: str, host: str, port: int, init: bool) -> None:
    """Restart the MCP server."""
    try:
        cli.commands["stop"].callback()  # stop
    except Exception:
        pass
    cli.commands["start"].callback(db_path=db_path, host=host, port=port, init=init)

# ---------------------------------------------------------------------
# MCP: CLI entrypoint
# Run with: wspr-ai-lite-mcp --db data/wspr.duckdb --port 8765 [--init]
# ---------------------------------------------------------------------

@click.command()
@click.version_option(__version__, prog_name="wspr-ai-lite-mcp")
@click.option("--db", "db_path", default="data/wspr.duckdb", show_default=True,
              help="Path to DuckDB database file.")
@click.option("--port", type=int, default=8765, show_default=True,
              help="TCP port to serve the MCP API on.")
@click.option("--init", is_flag=True, default=False,
              help="Initialize database if missing and ensure schema exists.")
def cli(db_path: str, port: int, init: bool) -> None:
    """
    Run the wspr-ai-lite MCP server.

    Example:
        wspr-ai-lite-mcp --db data/wspr.duckdb --port 8765 --init
    """
    # Publish DB path to helper functions
    global DB_PATH
    DB_PATH = db_path

    mode = "rw" if init else "ro"
    click.echo(f"[mcp] Using database: {db_path} (mode={mode})")

    try:
        # Open connection; if --init, allow write and ensure schema
        with conn(read_only=not init, init=init) as c:  # conn() should accept (read_only, init)
            # sanity touch
            c.execute("SELECT COUNT(*) FROM spots").fetchone()
    except Exception as e:
        click.echo(f"[mcp] Error opening database: {e}", err=True)
        raise SystemExit(1)

    # TODO: swap for real server loop (uvicorn / MCP runtime)
    click.echo(f"[mcp] (stub) would start MCP server on port {port}")

if __name__ == "__main__":
    cli()
