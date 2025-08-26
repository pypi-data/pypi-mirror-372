from __future__ import annotations

import click
import duckdb
from pathlib import Path

VIEW_SQL = r"""
CREATE VIEW IF NOT EXISTS spots_v AS
SELECT
  spot_id,
  timestamp,
  CAST(EXTRACT(YEAR  FROM timestamp) AS INTEGER) AS year,
  CAST(EXTRACT(MONTH FROM timestamp) AS INTEGER) AS month,
  CAST(EXTRACT(HOUR  FROM timestamp) AS INTEGER) AS hour,
  reporter,
  reporter_grid,
  snr_db,
  freq_mhz,
  tx_call,
  tx_grid,
  power_dbm,
  drift_hz_per_min,
  distance_km,
  azimuth_deg,
  band_code,
  CASE band_code
    WHEN -1 THEN 'LF'
    WHEN  0 THEN 'MF'
    WHEN  1 THEN '160m'
    WHEN  2 THEN '160m'
    WHEN  3 THEN '80m'
    WHEN  5 THEN '60m'
    WHEN  7 THEN '40m'
    WHEN 10 THEN '30m'
    WHEN 14 THEN '20m'
    WHEN 18 THEN '17m'
    WHEN 21 THEN '15m'
    WHEN 24 THEN '12m'
    WHEN 28 THEN '10m'
    WHEN 50 THEN '6m'
    WHEN 70 THEN '4m'
    WHEN 144 THEN '2m'
    WHEN 220 THEN '1.25m'
    WHEN 432 THEN '70cm'
    WHEN 1240 THEN '23cm'
    ELSE CAST(band_code AS VARCHAR) || ' MHz'
  END AS band_label,
  rx_version,
  code
FROM spots;
"""

@click.command()
@click.option("--db", "db_path", type=click.Path(path_type=Path), default="data/wspr.duckdb", show_default=True,
              help="Path to DuckDB file")
def main(db_path: Path) -> None:
    """Create or refresh computed views (idempotent)."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(db_path))
    try:
        con.execute(VIEW_SQL)
        click.echo(f"[views] created/kept: spots_v in {db_path}")
    finally:
        con.close()

if __name__ == "__main__":
    main()
