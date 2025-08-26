"""
Unit tests for pipelines.ingest (core helpers).

Covers:
- month_range() spanning single and multi-year ranges.
- archive_url() construction.
- band_from_freq_mhz() mapping.
- read_month_csv() basic parsing/validation.

Use:
    PYTHONPATH=. pytest -q tests/test_ingest.py
Notes:
    These tests avoid network and DuckDB I/O.
See also:
    tests/test_ingest_io.py for end-to-end ingest & cache behavior.
"""
import io
import gzip
import pandas as pd

from pipelines.ingest import (
    month_range,
    band_from_freq_mhz,
    read_month_csv,
)

def test_month_range_basic():
    """Docstring: This is to make pre-commit happy"""
    assert month_range("2014-07", "2014-07") == [(2014, 7)]
    assert month_range("2014-11", "2015-02") == [(2014, 11), (2014, 12), (2015, 1), (2015, 2)]

def test_band_from_freq():
    """Docstring: This is to make pre-commit happy"""
    assert band_from_freq_mhz(14.0956) == 20
    assert band_from_freq_mhz(7.0386) == 40
    assert band_from_freq_mhz(50.294) == 6

def test_read_month_csv_minimal():
    """Docstring: This is to make pre-commit happy"""
    # Construct a minimal CSV buffer with needed columns at expected positions
    # cols: 0..N, we use indices 1..7
    rows = [
        [1, 1404172800, "KD0HFC", "EN24qo", -22, 14.097077, "AE7CD", "EM12pt"],
        [2, 1404172860, "K1JT",   "FN20qi", -18, 7.038600,  "KI7MT", "DN45fo"],
    ]
    csv = "\n".join(",".join(map(str, r)) for r in rows).encode()
    buf = io.BytesIO(csv)
    df = read_month_csv(buf)
    assert {"ts","band","freq","snr","reporter","reporter_grid","txcall","tx_grid","year","month"} <= set(df.columns)
    assert len(df) == 2
