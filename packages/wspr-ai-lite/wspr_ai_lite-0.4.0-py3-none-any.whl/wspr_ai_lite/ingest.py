from __future__ import annotations

"""Ingest utilities for wspr-ai-lite (packaged version).

This module is self-contained so the PyPI-installed CLI works without relying
on the repo-local `pipelines/ingest.py`.

Functions provided:
- month_range(start, end): iterate (year, month) inclusive for YYYY-MM inputs
- archive_url(year, month): WSPRNet monthly CSV.GZ URL
- download_month(year, month, cache_dir): returns raw bytes (cached)
- band_from_freq_mhz(freq_mhz): map float MHz → human band label (legacy helper)
- band_code_from_freq_mhz(freq_mhz): map float MHz → canonical band_code (int)
- ensure_table(con): create canonical DuckDB table if missing
- ingest_month(con, year, month, cache_dir, offline): parse & insert (canonical schema)

This file also provides an optional Click CLI (fetch/ingest) behind
`if __name__ == "__main__":` for convenience; the canonical CLI remains `cli.py`.
"""

# standard libs
from pathlib import Path
from typing import Generator, Tuple
from datetime import timezone
import io
import gzip
import zipfile

# 3rd party libs
import duckdb
import pandas as pd
import requests
# import click

# Canonical column order (must match inserts)
_CANON_COLS = [
    "spot_id",
    "timestamp",
    "reporter",
    "reporter_grid",
    "snr_db",
    "freq_mhz",
    "tx_call",
    "tx_grid",
    "power_dbm",
    "drift_hz_per_min",
    "distance_km",
    "azimuth_deg",
    "band_code",
    "rx_version",
    "code",
]

# ----------------------------
# Helpers & core functionality
# ----------------------------

def month_range(start: str, end: str) -> Generator[Tuple[int, int], None, None]:
    """Yield (year, month) pairs inclusive between YYYY-MM strings."""
    sy, sm = (int(start[0:4]), int(start[5:7]))
    ey, em = (int(end[0:4]), int(end[5:7]))
    y, m = sy, sm
    while (y < ey) or (y == ey and m <= em):
        yield y, m
        m += 1
        if m > 12:
            y += 1
            m = 1


def archive_url(year: int, month: int) -> str:
    """Return the wsprnet.org monthly archive URL for a given year-month."""
    return f"https://wsprnet.org/archive/wsprspots-{year:04d}-{month:02d}.csv.gz"


def _cache_path(cache_dir: Path, year: int, month: int) -> Path:
    """Return cache path for a given year-month; ensure directory exists."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / f"wsprspots-{year:04d}-{month:02d}.csv.gz"


def _cache_candidates(cache_dir: Path, year: int, month: int) -> list[Path]:
    """Return possible cached filenames for a given year/month (.gz or .zip)."""
    base = f"wsprspots-{year:04d}-{month:02d}.csv"
    return [cache_dir / f"{base}.gz", cache_dir / f"{base}.zip"]


def _find_cached(cache_dir: Path, year: int, month: int) -> Path | None:
    cache_dir.mkdir(parents=True, exist_ok=True)
    for p in _cache_candidates(cache_dir, year, month):
        if p.exists():
            return p
    return None


def download_month(year: int, month: int, cache_dir: str | Path = ".cache") -> bytes:
    """Fetch from wsprnet (gz). Always saves as .gz."""
    cache_dir = Path(cache_dir)
    path_gz = cache_dir / f"wsprspots-{year:04d}-{month:02d}.csv.gz"
    if path_gz.exists():
        return path_gz.read_bytes()
    url = archive_url(year, month)
    print(f"GET {url}")
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    path_gz.write_bytes(r.content)
    return r.content

def band_from_freq_mhz(freq_mhz: float) -> str:
    """Map a frequency in MHz to a WSPR band label (human string; legacy helper)."""
    f = float(freq_mhz)
    bands = [
        (0.136, 0.139, "2200m"),
        (0.472, 0.479, "630m"),
        (1.8,   2.0,   "160m"),
        (3.5,   4.0,   "80m"),
        (5.0,   6.0,   "60m"),
        (7.0,   7.3,   "40m"),
        (10.0,  10.2,  "30m"),
        (14.0,  14.35, "20m"),
        (18.068,18.168,"17m"),
        (21.0,  21.45, "15m"),
        (24.89, 24.99, "12m"),
        (28.0,  29.7,  "10m"),
        (50.0,  54.0,  "6m"),
        (70.0,  71.0,  "4m"),
        (144.0, 148.0, "2m"),
        (220.0, 225.0, "1.25m"),
        (432.0, 438.0, "70cm"),
        (1240.0,1300.0,"23cm"),
    ]
    for lo, hi, label in bands:
        if lo <= f <= hi:
            return label
    return "unknown"


def band_code_from_freq_mhz(freq: float) -> int | None:
    """Map frequency in MHz → canonical band_code (int). -1 LF, 0 MF, else round(MHz)."""
    if freq is None:
        return None
    try:
        f = float(freq)
    except Exception:
        return None
    if f < 0.3:
        return -1  # LF
    if f < 3.0:
        return 0   # MF
    return int(round(f))    # crude but consistent with legacy rule

# ----------------------------
# DuckDB schema management
# ----------------------------

def ensure_table(con: duckdb.DuckDBPyConnection) -> None:
    """Create canonical DuckDB table `spots` if missing (UTC semantics for timestamp)."""
    con.execute(
        """
        CREATE TABLE IF NOT EXISTS spots (
            spot_id           BIGINT PRIMARY KEY,
            timestamp         TIMESTAMP,        -- stored as UTC (tz-naive); keep UTC semantics
            reporter          VARCHAR,
            reporter_grid     VARCHAR,
            snr_db            SMALLINT,
            freq_mhz          DOUBLE,
            tx_call           VARCHAR,
            tx_grid           VARCHAR,
            power_dbm         SMALLINT,
            drift_hz_per_min  SMALLINT,
            distance_km       INTEGER,
            azimuth_deg       SMALLINT,
            band_code         SMALLINT,         -- -1 LF, 0 MF, else int(MHz)
            rx_version        VARCHAR,
            code              INTEGER
        )
        """
    )

# ----------------------------
# CSV → DataFrame normalization
# ----------------------------

def _extract_csv_bytes(raw: bytes) -> bytes:
    """
    Return CSV bytes regardless of container:
      - gz:           gunzip
      - zip:          read first member's bytes
      - plain bytes:  return as-is
    """
    # gzip magic
    if len(raw) >= 2 and raw[:2] == b"\x1f\x8b":
        return gzip.decompress(raw)

    # zip?
    bio = io.BytesIO(raw)
    if zipfile.is_zipfile(bio):
        with zipfile.ZipFile(bio) as zf:
            # pick the first non-dir entry
            for name in zf.namelist():
                if not name.endswith("/"):
                    with zf.open(name) as f:
                        return f.read()
        raise ValueError("ZIP archive had no file entries")

    # otherwise assume it's already CSV
    return raw

def _read_month_to_df(raw_bytes: bytes) -> pd.DataFrame:
    """Read a WSPR monthly CSV.GZ into a canonical-schema DataFrame.

    The wsprnet monthly archives are typically headerless and may include
    additional trailing columns. We read up to the first 15 positions (when present)
    and normalize into the canonical layout:

      0: spot_id (int)                  -> spot_id
      1: unixtime (sec)                 -> timestamp (UTC)
      2: tx_call (str)                  -> tx_call
      3: tx_grid (str)                  -> tx_grid
      4: snr (dB, int)                  -> snr_db
      5: freq (MHz, float)              -> freq_mhz
      6: reporter (str)                 -> reporter
      7: reporter_grid (str)            -> reporter_grid
      8: power_dbm (int, optional)      -> power_dbm
      9: drift_hz_per_min (int, opt)    -> drift_hz_per_min
     10: distance_km (int, opt)         -> distance_km
     11: azimuth_deg (int, opt)         -> azimuth_deg
     12: band_archive (int, opt)        -> (ignored; we recompute band_code)
     13: rx_version (str, opt)          -> rx_version
     14: code (int, opt)                -> code

    Returns a pandas.DataFrame with canonical columns in canonical order.
    """

    csv_bytes = _extract_csv_bytes(raw_bytes)
    buf = io.BytesIO(csv_bytes)
    df = pd.read_csv(
        buf,
        header=None,
        usecols=list(range(0, 15)),
        names=[
            "spot_id","unixtime","tx_call","tx_grid",
            "snr_db","freq_mhz","reporter","reporter_grid",
            "power_dbm","drift_hz_per_min","distance_km","azimuth_deg",
            "band_archive","rx_version","code",
        ],
        dtype={
            "spot_id": "Int64","unixtime": "Int64","tx_call": "string","tx_grid": "string",
            "snr_db": "Int64","freq_mhz": "float64","reporter": "string","reporter_grid": "string",
            "power_dbm": "Int64","drift_hz_per_min": "Int64","distance_km": "Int64","azimuth_deg": "Int64",
            "band_archive": "Int64","rx_version": "string","code": "Int64",
        },
        low_memory=False,
    )

    # Timestamp → UTC (store tz-naive but UTC semantics)
    ts = pd.to_datetime(df["unixtime"], unit="s", utc=True).dt.tz_localize(None)
    df["timestamp"] = ts
    df.drop(columns=["unixtime"], inplace=True, errors="ignore")

    # Normalize callsigns & grids (uppercase; leave empty as NA)
    for c in ("reporter", "tx_call", "reporter_grid", "tx_grid"):
        if c in df.columns:
            df[c] = df[c].astype("string").str.strip().str.upper().replace({"": pd.NA})

    # Compute canonical band_code from freq_mhz (ignore band_archive)
    df["band_code"] = df["freq_mhz"].map(band_code_from_freq_mhz).astype("Int64")

    # rx_version can be missing historically; keep as NA if blank
    if "rx_version" in df.columns:
        df["rx_version"] = df["rx_version"].astype("string").str.strip().replace({"": pd.NA})
    else:
        df["rx_version"] = pd.Series(pd.NA, dtype="string")

    # code may be absent; default to 0 if NA/missing
    if "code" in df.columns:
        df["code"] = df["code"].fillna(0).astype("Int64")
    else:
        df["code"] = pd.Series(0, dtype="Int64")

    # Ensure all canonical columns exist
    for col in _CANON_COLS:
        if col not in df.columns:
            df[col] = pd.NA

    out = df[_CANON_COLS].copy()

    # Drop rows without spot_id or timestamp
    out = out.dropna(subset=["spot_id", "timestamp"])

    # Cast to compact dtypes for DuckDB
    casts = {
        "spot_id": "Int64",
        "snr_db": "Int16",
        "power_dbm": "Int16",
        "drift_hz_per_min": "Int16",
        "distance_km": "Int32",
        "azimuth_deg": "Int16",
        "band_code": "Int16",
        "code": "Int32",
        "freq_mhz": "float64",
        "reporter": "string",
        "reporter_grid": "string",
        "tx_call": "string",
        "tx_grid": "string",
        "rx_version": "string",
    }
    out = out.astype({k: v for k, v in casts.items() if k in out.columns})

    return out

# ----------------------------
# Byte loading (offline/online)
# ----------------------------

def load_month_bytes(year: int, month: int, cache_dir: str | Path = ".cache", offline: bool = False) -> bytes:
    """
    Return **decompressed CSV bytes**.
    - If .gz in cache: gunzip and return CSV bytes.
    - If .zip in cache: read inner .csv and return bytes.
    - If not cached:
        * offline=True -> error
        * offline=False -> download .gz, gunzip, return CSV bytes
    """
    cache_dir = Path(cache_dir)
    existing = _find_cached(cache_dir, year, month)
    if existing:
        if existing.suffix == ".gz":
            return gzip.decompress(existing.read_bytes())
        if existing.suffix == ".zip":
            with zipfile.ZipFile(existing, "r") as zf:
                names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
                if not names:
                    raise ValueError(f"No .csv inside {existing}")
                return zf.read(names[0])
        raise ValueError(f"Unsupported archive type: {existing}")

    if offline:
        raise FileNotFoundError(f"Missing cached file: {cache_dir}/wsprspots-{year:04d}-{month:02d}.csv.[gz|zip]")

    # network: download gz, then return decompressed CSV bytes
    raw_gz = download_month(year, month, cache_dir)
    return gzip.decompress(raw_gz)

# ----------------------------
# Ingest one month (canonical)
# ----------------------------

def ingest_month(
    con: duckdb.DuckDBPyConnection,
    year: int,
    month: int,
    cache_dir: str | Path = ".cache",
    offline: bool = False,
) -> int:
    """
    Download (or read cached), parse, and insert one month into DuckDB
    using the canonical schema. Returns the number of rows inserted.

    De-dupes on primary key (spot_id) so re-ingesting the same month is safe.
    """
    # Correct variable: get the monthly bytes
    raw_bytes = load_month_bytes(year, month, cache_dir, offline=offline)

    # Parse into the canonical DataFrame
    df = _read_month_to_df(raw_bytes)

    # Ensure target table exists
    ensure_table(con)

    # Insert only rows whose spot_id is not already present
    con.register("spots_df", df)
    con.execute(
        """
        INSERT INTO spots
        SELECT *
        FROM spots_df s
        WHERE NOT EXISTS (
            SELECT 1 FROM spots t WHERE t.spot_id = s.spot_id
        )
        """
    )
    con.unregister("spots_df")

    print(f"[OK] {year:04d}-{month:02d} ({len(df):,} rows)")
    return int(len(df))
