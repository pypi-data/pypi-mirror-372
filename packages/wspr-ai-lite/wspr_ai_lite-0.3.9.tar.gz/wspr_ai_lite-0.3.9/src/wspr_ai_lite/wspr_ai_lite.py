from __future__ import annotations

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Streamlit UI for wspr-ai-lite.

Visualizes local WSPR data stored in DuckDB (``data/wspr.duckdb``).
Uses the canonical schema:

  spot_id, timestamp (UTC), reporter, reporter_grid, snr_db, freq_mhz,
  tx_call, tx_grid, power_dbm, drift_hz_per_min, distance_km, azimuth_deg,
  band_code, rx_version, code

All time-derived fields (year, month, hour) are computed via DuckDB EXTRACT().
Band filtering/display uses a band code → human label mapping.
"""

import math
import pathlib
from typing import List, Tuple, Optional

import duckdb
import pandas as pd
import streamlit as st

DB_PATH: str = "data/wspr.duckdb"


# ----------------------------- Maidenhead & Distance -----------------------------

def maidenhead_to_latlon(grid: str) -> Tuple[Optional[float], Optional[float]]:
    """Convert a 4/6-char Maidenhead grid to (lat, lon) center; return (None, None) if invalid."""
    if not grid or not isinstance(grid, str):
        return None, None
    g = grid.strip().upper()
    if len(g) not in (4, 6):
        return None, None
    try:
        # Field
        lon = (ord(g[0]) - ord('A')) * 20 - 180
        lat = (ord(g[1]) - ord('A')) * 10 - 90
        # Square
        lon += int(g[2]) * 2
        lat += int(g[3]) * 1

        if len(g) == 4:
            lon += 1.0
            lat += 0.5
            return lat, lon

        # Subsquare
        sub_lon = ord(g[4]) - ord('A')
        sub_lat = ord(g[5]) - ord('A')
        if not (0 <= sub_lon < 24 and 0 <= sub_lat < 24):
            return None, None
        lon += (sub_lon + 0.5) * (2.0 / 24.0)
        lat += (sub_lat + 0.5) * (1.0 / 24.0)
        return lat, lon
    except Exception:
        return None, None


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance between two WGS84 points in kilometers."""
    R = 6371.0088
    from math import radians, sin, cos, sqrt, atan2
    dphi = radians(lat2 - lat1)
    dl   = radians(lon2 - lon1)
    phi1 = radians(lat1)
    phi2 = radians(lat2)
    a = sin(dphi/2)**2 + cos(phi1)*cos(phi2)*sin(dl/2)**2
    return 2*R*atan2(math.sqrt(a), math.sqrt(1-a))


def grid_distance_km(tx_grid: str, rx_grid: str) -> Optional[float]:
    """Distance in km between grid centers; None if either invalid/missing."""
    lat1, lon1 = maidenhead_to_latlon(tx_grid) if tx_grid else (None, None)
    lat2, lon2 = maidenhead_to_latlon(rx_grid) if rx_grid else (None, None)
    if None in (lat1, lon1, lat2, lon2):
        return None
    return haversine_km(lat1, lon1, lat2, lon2)


# ----------------------------- Band helpers -----------------------------

_BAND_LABELS = {
    -1: "LF",
     0: "MF",
     1: "160m",   2: "160m",
     3: "80m",
     5: "60m",
     7: "40m",
    10: "30m",
    14: "20m",
    18: "17m",
    21: "15m",
    24: "12m",
    28: "10m",
    50: "6m",
    70: "4m",
   144: "2m",
   220: "1.25m",
   432: "70cm",
  1240: "23cm",
}

def band_label(code: int | None) -> str:
    """Map band_code to human label (e.g., 14 → '20m')."""
    if code is None:
        return "unknown"
    return _BAND_LABELS.get(int(code), f"{int(code)} MHz")

def band_code_from_label(label: str) -> int | None:
    """Map human label back to band_code."""
    for k, v in _BAND_LABELS.items():
        if v.lower() == label.lower():
            return k
    if label.lower().endswith("mhz"):
        try:
            return int(label[:-3].strip())
        except Exception:
            pass
    return None


# ----------------------------- Query helpers (canonical schema) -----------------------------

def get_distinct_years(con: duckdb.DuckDBPyConnection) -> List[int]:
    """List of years present (derived from `timestamp`)."""
    return [
        r[0] for r in con.execute(
            "SELECT DISTINCT CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER) AS yr "
            "FROM spots ORDER BY yr"
        ).fetchall()
    ]


def get_distinct_bands(con: duckdb.DuckDBPyConnection, year: int) -> List[str]:
    """Band labels for a given year (derived from band_code)."""
    codes = [
        r[0] for r in con.execute(
            "SELECT DISTINCT band_code "
            "FROM spots WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? "
            "ORDER BY band_code",
            [year],
        ).fetchall()
    ]
    return [band_label(c) for c in codes]


def get_total_spots(con: duckdb.DuckDBPyConnection, year: int, band_label_str: str) -> int:
    """Total rows for selected year + band label."""
    code = band_code_from_label(band_label_str)
    return con.execute(
        "SELECT COUNT(*) FROM spots "
        "WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?",
        [year, code],
    ).fetchone()[0]


def get_snr_histogram(con: duckdb.DuckDBPyConnection, year: int, band_label_str: str) -> pd.DataFrame:
    """Histogram of snr_db counts for year+band."""
    code = band_code_from_label(band_label_str)
    return con.execute(
        """
        SELECT snr_db AS snr, COUNT(*) AS n
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?
        GROUP BY snr_db
        ORDER BY snr_db
        """,
        [year, code],
    ).fetchdf()


def get_monthly_counts(con: duckdb.DuckDBPyConnection, year: int, band_label_str: str) -> pd.DataFrame:
    """Monthly counts for year+band."""
    code = band_code_from_label(band_label_str)
    return con.execute(
        """
        SELECT CAST(EXTRACT(MONTH FROM timestamp) AS INTEGER) AS month, COUNT(*) AS n
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?
        GROUP BY month
        ORDER BY month
        """,
        [year, code],
    ).fetchdf()


def get_top_reporters(con: duckdb.DuckDBPyConnection, year: int, band_label_str: str, limit: int = 50) -> pd.DataFrame:
    """Top RX callsigns by count for year+band."""
    code = band_code_from_label(band_label_str)
    return con.execute(
        """
        SELECT reporter, COUNT(*) AS n
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?
        GROUP BY reporter
        ORDER BY n DESC
        LIMIT ?
        """,
        [year, code, limit],
    ).fetchdf()


def get_most_heard_tx(con: duckdb.DuckDBPyConnection, year: int, band_label_str: str, limit: int = 50) -> pd.DataFrame:
    """Most-heard TX callsigns for year+band."""
    code = band_code_from_label(band_label_str)
    return con.execute(
        """
        SELECT
          tx_call AS tx,
          COUNT(*) AS n,
          COUNT(DISTINCT reporter) AS unique_rx
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?
        GROUP BY tx_call
        ORDER BY n DESC
        LIMIT ?
        """,
        [year, code, limit],
    ).fetchdf()


def get_geographic_spread(con: duckdb.DuckDBPyConnection, year: int, band_label_str: str) -> pd.DataFrame:
    """Unique grid counts (RX/TX) for year+band."""
    code = band_code_from_label(band_label_str)
    return con.execute(
        """
        SELECT
          COUNT(DISTINCT reporter_grid) AS unique_rx_grids,
          COUNT(DISTINCT tx_grid)       AS unique_tx_grids
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?
        """,
        [year, code],
    ).fetchdf()


def get_avg_snr_by_month(con: duckdb.DuckDBPyConnection, year: int, band_label_str: str) -> pd.DataFrame:
    """Average snr_db by month for year+band."""
    code = band_code_from_label(band_label_str)
    return con.execute(
        """
        SELECT CAST(EXTRACT(MONTH FROM timestamp) AS INTEGER) AS month, AVG(snr_db) AS avg_snr
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?
        GROUP BY month
        ORDER BY month
        """,
        [year, code],
    ).fetchdf()


def get_activity_by_hour_month(con: duckdb.DuckDBPyConnection, year: int, band_label_str: str) -> pd.DataFrame:
    """Counts by (hour, month) for year+band."""
    code = band_code_from_label(band_label_str)
    return con.execute(
        """
        SELECT
          CAST(EXTRACT(HOUR  FROM timestamp) AS INTEGER) AS hour,
          CAST(EXTRACT(MONTH FROM timestamp) AS INTEGER) AS month,
          COUNT(*) AS n
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?
        GROUP BY month, hour
        ORDER BY month, hour
        """,
        [year, code],
    ).fetchdf()


def get_unique_counts_by_year(con: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    """Distinct RX/TX counts per year (derived from timestamp)."""
    return con.execute(
        """
        SELECT
          CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER) AS year,
          COUNT(DISTINCT reporter) AS unique_rx,
          COUNT(DISTINCT tx_call)  AS unique_tx
        FROM spots
        GROUP BY year
        ORDER BY year
        """
    ).fetchdf()


# -------- Station-centric helpers (TX/RX stats + reciprocal heard) --------

def my_tx_heard(con, year: int, band_label_str: str, my: str, by_rx: Optional[str]) -> tuple[int, pd.DataFrame]:
    """As TX: how often I (my callsign) was heard, optionally by a specific RX."""
    my = my.upper().strip()
    code = band_code_from_label(band_label_str)
    params = [year, code, my]
    rx_filter = ""
    if by_rx and by_rx.strip():
        rx_filter = " AND reporter = ? "
        params.append(by_rx.upper().strip())

    total = con.execute(
        f"""
        SELECT COUNT(*) FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=? AND tx_call=? {rx_filter}
        """,
        params,
    ).fetchone()[0]

    df = con.execute(
        f"""
        SELECT reporter AS rx, COUNT(*) AS n
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=? AND tx_call=? {rx_filter}
        GROUP BY reporter
        ORDER BY n DESC
        LIMIT 100
        """,
        params,
    ).fetchdf()
    return total, df


def my_rx_heard(con, year: int, band_label_str: str, my: str, of_tx: Optional[str]) -> tuple[int, pd.DataFrame]:
    """As RX: how often I (my callsign) heard others, optionally a specific TX."""
    my = my.upper().strip()
    code = band_code_from_label(band_label_str)
    params = [year, code, my]
    tx_filter = ""
    if of_tx and of_tx.strip():
        tx_filter = " AND tx_call = ? "
        params.append(of_tx.upper().strip())

    total = con.execute(
        f"""
        SELECT COUNT(*) FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=? AND reporter=? {tx_filter}
        """,
        params,
    ).fetchone()[0]

    df = con.execute(
        f"""
        SELECT tx_call AS tx, COUNT(*) AS n
        FROM spots
        WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=? AND reporter=? {tx_filter}
        GROUP BY tx_call
        ORDER BY n DESC
        LIMIT 100
        """,
        params,
    ).fetchdf()
    return total, df


def reciprocal_heard(con, a: str, b: str, window_min: int,
                     require_same_band: bool,
                     year_filter: Optional[int],
                     band_filter_label: Optional[str]) -> pd.DataFrame:
    """QSO-like: A heard B and B heard A within a time window (minutes)."""
    a = a.upper().strip()
    b = b.upper().strip()
    where = [
        "s1.reporter = ?",
        "s1.tx_call  = ?",
        "s2.reporter = ?",
        "s2.tx_call  = ?",
        "ABS(DATEDIFF('minute', s1.timestamp, s2.timestamp)) <= ?",
    ]
    params: list = [a, b, b, a, window_min]

    if year_filter is not None:
        where += [
            "CAST(EXTRACT(YEAR FROM s1.timestamp) AS INTEGER) = ?",
            "CAST(EXTRACT(YEAR FROM s2.timestamp) AS INTEGER) = ?",
        ]
        params += [year_filter, year_filter]
    if band_filter_label is not None:
        bc = band_code_from_label(band_filter_label)
        where += ["s1.band_code = ?", "s2.band_code = ?"]
        params += [bc, bc]
    if require_same_band:
        where.append("s1.band_code = s2.band_code")

    sql = f"""
        SELECT
            s1.timestamp AS ts_a, s1.band_code AS band_a, s1.snr_db AS snr_a,
            s2.timestamp AS ts_b, s2.band_code AS band_b, s2.snr_db AS snr_b,
            ABS(DATEDIFF('minute', s1.timestamp, s2.timestamp)) AS dt_min
        FROM spots s1
        JOIN spots s2 ON 1=1
        WHERE {' AND '.join(where)}
        ORDER BY dt_min ASC, ts_a ASC
        LIMIT 200
    """
    df = con.execute(sql, params).fetchdf()
    if not df.empty:
        df["band_a"] = df["band_a"].map(band_label)
        df["band_b"] = df["band_b"].map(band_label)
    return df


# --------------------------- Page & Sidebar UI ---------------------------

st.set_page_config(page_title="wspr-ai-lite", layout="wide")

# Sidebar: optional help
show_help = st.sidebar.checkbox("Show Help / Instructions", value=False)

st.title("wspr-ai-lite")

with st.expander("About this app"):
    st.markdown(
        """
**wspr-ai-lite** is a lightweight viewer for WSPR (Weak Signal Propagation Reporter) spots.
It uses a local DuckDB file and Streamlit.

**How to use**
1. Ingest data (once or as needed):

       wspr-ai-lite ingest --from 2014-07 --to 2014-07 --db data/wspr.duckdb

2. Run this UI:

       wspr-ai-lite ui --db data/wspr.duckdb --port 8501
        """
    )

# Ensure DB exists
db_file = pathlib.Path(DB_PATH)
if not db_file.exists():
    st.warning("Database not found. Run the ingest script first.")
    st.stop()

# Open connection (read-only)
con = duckdb.connect(DB_PATH, read_only=True)

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    years = get_distinct_years(con)
    if not years:
        st.info("No data yet — please run the ingest script.")
        st.stop()
    year = st.selectbox("Year", years, index=0)

    bands = get_distinct_bands(con, year)
    if not bands:
        st.info("No bands available for the selected year.")
        st.stop()
    band = st.selectbox("Band", bands, index=0)

    st.markdown("---")
    st.header("Station Analysis")
    my_callsign = st.text_input("My Callsign (TX/RX)", value="", placeholder="e.g., KI7MT").upper().strip()
    counterparty = st.text_input("Counterparty (optional)", value="", placeholder="e.g., K1JT").upper().strip()

    st.markdown("**QSO Finder Options**")
    qso_window = st.number_input("QSO Window (Minutes)", min_value=1, max_value=180, value=4, step=1)
    qso_across_all_years = st.checkbox("Search Across All Years (Ignore Year Filter)", value=False)
    qso_across_all_bands = st.checkbox("Search Across All Bands (Ignore Band Filter)", value=False)
    qso_same_band_only = st.checkbox("Require Same Band (QSO)", value=True)

    st.markdown("---")
    st.header("Distance Options")
    max_rows_distance = st.number_input(
        "Max Rows for Distance Calculations",
        min_value=1000,
        max_value=1_000_000,
        value=100_000,
        step=10_000,
    )

# ---------------------- Overview panels ----------------------

col1, col2, col3 = st.columns(3)

with col1:
    total = get_total_spots(con, year, band)
    st.metric("Total Spots", f"{total:,}")

with col2:
    st.subheader("SNR Distribution by Count")
    df_snr = get_snr_histogram(con, year, band)
    if not df_snr.empty:
        df_snr = df_snr.rename(columns={"snr": "SNR (dB)", "n": "Count"})
        st.bar_chart(df_snr.set_index("SNR (dB)"))
    else:
        st.info("No SNR data for the selected filters.")

with col3:
    st.subheader("Monthly Spot Counts")
    df_month = get_monthly_counts(con, year, band)
    if not df_month.empty:
        df_month = df_month.rename(columns={"month": "Month", "n": "Count"})
        st.bar_chart(df_month.set_index("Month"))
    else:
        st.info("No monthly data for the selected filters.")

# ---------------------- Top reporters & uniques ----------------------

st.subheader("Top Reporting Stations")

unique_rx = con.execute(
    "SELECT COUNT(DISTINCT reporter) FROM spots "
    "WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?",
    [year, band_code_from_label(band)],
).fetchone()[0]
unique_tx = con.execute(
    "SELECT COUNT(DISTINCT tx_call) FROM spots "
    "WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?",
    [year, band_code_from_label(band)],
).fetchone()[0]

c1, c2 = st.columns(2)
with c1:
    st.metric("Unique RX Stations", f"{unique_rx:,}")
with c2:
    st.metric("Unique TX Stations", f"{unique_tx:,}")

df_rep = get_top_reporters(con, year, band, limit=50)
if not df_rep.empty:
    df_rep = df_rep.rename(columns={"reporter": "Reporter", "n": "Count"})
st.dataframe(df_rep, use_container_width=True)

# ---------------------- Most heard TX stations ----------------------

st.subheader("Most Heard TX Stations")
df_most_tx = get_most_heard_tx(con, year, band, limit=50)
if not df_most_tx.empty:
    df_most_tx = df_most_tx.rename(columns={"tx": "TX Station", "n": "Count", "unique_rx": "Unique RX Stations"})
st.dataframe(df_most_tx, use_container_width=True)

# ---------------------- Geographic spread ----------------------

st.subheader("Geographic Spread (Unique Grids)")
df_gs = get_geographic_spread(con, year, band)
if not df_gs.empty:
    df_gs = df_gs.rename(columns={"unique_rx_grids": "Unique RX Grids", "unique_tx_grids": "Unique TX Grids"})
st.dataframe(df_gs, use_container_width=True)

# ---------------------- Station-centric panels ----------------------

st.markdown("---")
st.header("Station-Centric Analysis")

if my_callsign:
    # Panel A: My TX heard by others
    a1, a2 = st.columns(2)
    with a1:
        st.subheader("My TX Heard by Others")
        total_tx, df_tx = my_tx_heard(con, year, band, my_callsign, counterparty or None)
        st.metric("Total (I Was TX, Heard as RX)", f"{total_tx:,}")
        if not df_tx.empty:
            df_tx = df_tx.rename(columns={"rx": "RX Station", "n": "Count"})
            st.dataframe(df_tx, use_container_width=True, height=300)
        else:
            st.info("No matches for TX perspective with current filters.")

    # Panel B: My RX heard others
    with a2:
        st.subheader("My RX Heard Others")
        total_rx, df_rx = my_rx_heard(con, year, band, my_callsign, counterparty or None)
        st.metric("Total (I Was RX, Heard a TX)", f"{total_rx:,}")
        if not df_rx.empty:
            df_rx = df_rx.rename(columns={"tx": "TX Station", "n": "Count"})
            st.dataframe(df_rx, use_container_width=True, height=300)
        else:
            st.info("No matches for RX perspective with current filters.")

    # TX/RX Balance
    st.subheader("TX/RX Balance for My Callsign")
    st.markdown(f"- **TX Spots (as transmitter):** {total_tx:,}")
    st.markdown(f"- **RX Spots (as receiver):** {total_rx:,}")

    # Reciprocal heard (QSO-like) and success rate
    if counterparty:
        st.subheader(f"Reciprocal Heard (QSO-Like): {my_callsign} ↔ {counterparty}")
        yr_filter = None if qso_across_all_years else year
        bd_filter = None if qso_across_all_bands else band
        df_qso = reciprocal_heard(con, my_callsign, counterparty, int(qso_window), qso_same_band_only, yr_filter, bd_filter)
        if not df_qso.empty:
            df_qso = df_qso.rename(columns={
                "ts_a": "Time A",
                "band_a": "Band A",
                "snr_a": "SNR A (dB)",
                "ts_b": "Time B",
                "band_b": "Band B",
                "snr_b": "SNR B (dB)",
                "dt_min": "Δt (min)",
            })
            st.dataframe(df_qso, use_container_width=True, height=320)

            # Heuristic QSO success rate
            tx_to_cp, _ = my_tx_heard(con, year, band, my_callsign, counterparty)
            rx_from_cp, _ = my_rx_heard(con, year, band, my_callsign, counterparty)
            denom = max(1, tx_to_cp + rx_from_cp)
            qsr = 100.0 * len(df_qso) / denom
            st.metric("QSO Success Rate (Heuristic)", f"{qsr:.1f}%")
        else:
            st.info("No reciprocal-heard matches within the time window for current settings.")
else:
    st.info("Enter **My Callsign** in the sidebar to enable station-centric analysis.")

# ---------------------- Distance & DX ----------------------

st.markdown("---")
st.header("Distance & DX")

df_dist_src = con.execute(
    """
    SELECT timestamp, band_code, snr_db, reporter, reporter_grid, tx_call, tx_grid
    FROM spots
    WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=? AND band_code=?
    LIMIT ?
    """,
    [year, band_code_from_label(band), int(max_rows_distance)],
).fetchdf()

if df_dist_src.empty:
    st.info("No rows available for distance calculation with current filters.")
else:
    dists = df_dist_src.apply(lambda r: grid_distance_km(r["tx_grid"], r["reporter_grid"]), axis=1)
    df_dist = df_dist_src.assign(distance_km=dists).dropna(subset=["distance_km"])

    if df_dist.empty:
        st.info("No valid grid pairs for distance calculation (missing or invalid grids).")
    else:
        # Distribution
        bins = [0, 500, 2000, 10000]
        labels = ["≤500 km", "500–2000 km", ">2000 km"]
        df_dist["bin"] = pd.cut(df_dist["distance_km"], bins=bins, labels=labels, include_lowest=True, right=True)
        df_bins = df_dist.groupby("bin", observed=True)["distance_km"].count().reset_index(name="Count")

        st.subheader("Distance Distribution (km)")
        st.bar_chart(df_bins.set_index("bin"))

        # Longest DX
        idx_max = df_dist["distance_km"].idxmax()
        row_max = df_dist.loc[idx_max]
        band_text = band_label(row_max["band_code"])
        st.markdown(
            f"**Longest DX (sampled):** {row_max['distance_km']:.1f} km — "
            f"TX `{row_max['tx_call']}` ({row_max['tx_grid']}) → "
            f"RX `{row_max['reporter']}` ({row_max['reporter_grid']}) on {band_text}"
        )

        # Best DX per Band (within selected year)
        df_all_bands = con.execute(
            """
            SELECT timestamp, band_code, snr_db, reporter, reporter_grid, tx_call, tx_grid
            FROM spots
            WHERE CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER)=?
            LIMIT 100000
            """,
            [year],
        ).fetchdf()

        if not df_all_bands.empty:
            d2 = df_all_bands.copy()
            d2["distance_km"] = d2.apply(lambda r: grid_distance_km(r["tx_grid"], r["reporter_grid"]), axis=1)
            d2 = d2.dropna(subset=["distance_km"])
            if not d2.empty:
                idx = d2.groupby("band_code")["distance_km"].idxmax()
                df_best = d2.loc[idx, ["band_code", "tx_call", "tx_grid", "reporter", "reporter_grid", "distance_km"]].copy()
                df_best["Band"] = df_best["band_code"].map(band_label)
                df_best = df_best.rename(columns={
                    "tx_call": "TX Station",
                    "tx_grid": "TX Grid",
                    "reporter": "RX Station",
                    "reporter_grid": "RX Grid",
                    "distance_km": "Best Distance (km)",
                }).drop(columns=["band_code"]).sort_values("Band")
                st.subheader("Best DX per Band (sampled)")
                st.dataframe(df_best, use_container_width=True)

# ---------------------- SNR trends ----------------------

st.markdown("---")
st.subheader("Average SNR by Month")

df_avg_snr = get_avg_snr_by_month(con, year, band)
if not df_avg_snr.empty:
    df_avg_snr = df_avg_snr.rename(columns={"month": "Month", "avg_snr": "Average SNR (dB)"})
    st.line_chart(df_avg_snr.set_index("Month"))
else:
    st.info("No data available to compute average SNR by month.")

# ---------------------- Activity heatmap-like table ----------------------

st.markdown("---")
st.subheader("Activity by Hour × Month (Spot Counts)")

df_hm = get_activity_by_hour_month(con, year, band)
if not df_hm.empty:
    df_hm = df_hm.rename(columns={"hour": "Hour (UTC)", "month": "Month", "n": "Count"})
    pivot = df_hm.pivot(index="Month", columns="Hour (UTC)", values="Count").fillna(0).astype(int)
    st.dataframe(pivot, use_container_width=True)
else:
    st.info("No activity data for heatmap.")

# ---------------------- Unique stations trend ----------------------

st.markdown("---")
st.subheader("Unique Stations by Year")

df_unique_trend = get_unique_counts_by_year(con)
if not df_unique_trend.empty:
    df_unique_trend = df_unique_trend.rename(columns={"year": "Year", "unique_rx": "Unique RX", "unique_tx": "Unique TX"})
    st.line_chart(df_unique_trend.set_index("Year")[["Unique RX", "Unique TX"]])
else:
    st.info("No data available to compute yearly unique station counts.")

# -------------------------- Footer / Ingest Status --------------------------

st.markdown("---")
st.subheader("Database / Ingest Status")

latest = con.execute(
    "SELECT "
    "  CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER) AS y, "
    "  CAST(EXTRACT(MONTH FROM timestamp) AS INTEGER) AS m "
    "FROM spots ORDER BY y DESC, m DESC LIMIT 1"
).fetchone()

df_year_counts = con.execute(
    "SELECT CAST(EXTRACT(YEAR FROM timestamp) AS INTEGER) AS year, COUNT(*) AS n "
    "FROM spots GROUP BY year ORDER BY year"
).fetchdf()
if not df_year_counts.empty:
    df_year_counts = df_year_counts.rename(columns={"year": "Year", "n": "Spot Count"})

if latest:
    st.markdown(
        f"- **Latest Month Present:** `{latest[0]:04d}-{latest[1]:02d}`  \n"
        f"- **Database File:** `{DB_PATH}`"
    )
else:
    st.info("No data has been ingested yet.")

if not df_year_counts.empty:
    st.markdown("**Rows per Year:**")
    st.dataframe(df_year_counts, use_container_width=True)
else:
    st.caption("No year-level counts available.")

st.caption("wspr-ai-lite • local DuckDB + Streamlit • Ingest via CLI, explore in the UI.")
