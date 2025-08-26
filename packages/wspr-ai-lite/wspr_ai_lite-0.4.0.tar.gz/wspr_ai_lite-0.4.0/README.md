# wspr-ai-lite
Lightweight WSPR analytics and AI‑ready backend using **DuckDB** + **Streamlit**, with safe query access via **MCP Agents**.

[![Made with Streamlit](https://img.shields.io/badge/Made%20with-Streamlit-FF4B4B)](https://streamlit.io/)
[![DuckDB](https://img.shields.io/badge/Database-DuckDB-blue)](https://duckdb.org/)
[![MCP](https://img.shields.io/badge/AI--Agent--Ready-MCP-green)](https://modelcontextprotocol.io/)
[![Docs](https://img.shields.io/badge/Docs-GitHub_Pages-blue)](https://ki7mt.github.io/wspr-ai-lite/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Workflows and Packaging Status

**Versions**
[![GitHub release](https://img.shields.io/github/v/release/KI7MT/wspr-ai-lite)](https://github.com/KI7MT/wspr-ai-lite/releases)
[![GitHub tag](https://img.shields.io/github/tag/KI7MT/wspr-ai-lite?sort=semver)](https://github.com/KI7MT/wspr-ai-lite/tags)
[![PyPI version](https://img.shields.io/pypi/v/wspr-ai-lite.svg)](https://pypi.org/project/wspr-ai-lite/)
[![Python versions](https://img.shields.io/pypi/pyversions/wspr-ai-lite.svg)](https://pypi.org/project/wspr-ai-lite/)

**CI/CD**
[![CI](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/ci.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/ci.yml)
[![Smoke](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/smoke.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/smoke.yml)
[![Publish](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/release.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/release.yml)
[![pre-commit](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/pre-commit.yml/badge.svg)](https://github.com/KI7MT/wspr-ai-lite/actions/workflows/pre-commit.yml)
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

---

## Overview

- **Analytics Dashboard**: Streamlit UI lets you explore WSPR spots with SNR trends, DX distance analysis, station activity, and “QSO‑like” reciprocity views.
- **Canonical Schema**: Data is normalized into a portable DuckDB file—consistent, lightweight, and ready for future backend upgrades.
- **CLI Tools**: Click-based tools (`wspr-ai-lite`, `wspr-ai-lite-fetch`, `wspr-ai-lite-tools`) for downloading, ingesting, verifying, and managing the database.
- **MCP Integration**: Experimental MCP server (`wspr-ai-lite-mcp`) exposing safe APIs for AI agents. A manifest defines permitted queries and access control.
- **Roadmap (v0.4+ vision)**: MCP server will migrate to a **FastAPI + Uvicorn** backend with service control (start/stop/restart), enabling production-grade deployment.

---

## What Can You Do With It

Explore **Weak Signal Propagation Reporter (WSPR)** data with an easy, local dashboard:

- SNR distributions & monthly spot trends
- Top reporters, most-heard TX stations
- Geographic spread & distance/DX analysis
- QSO-like reciprocal reports
- Hourly activity heatmaps & yearly unique counts
- Works on **Windows, Linux, macOS** — no heavy server required.

## Key Features
- Local DuckDB storage with efficient ingest + caching
- Streamlit UI for interactive exploration
- Distance/DX analysis with Maidenhead grid conversion
- QSO-like reciprocal finder with configurable time window

## Fast Performance
- Columnar Storage: DuckDB is a columnar database, which allows for better data compression and faster query execution.
- Vectorization: processes data in batches, optimized CPU usage, significantly faster than traditional OLTP databases.

## Ease of Use
- Simple Installation: DuckDB can be installed with just a few lines of code, and on any platform.
- In-Process Operation: It runs within as a host application, eliminating network latency and simplifying data access.

## Quickstart (Recommended: PyPI)

### 1. Install from PyPI

> optional but recommended: [create a Python virtual environment](https://docs.python.org/3/library/venv.html) first

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install wspr-ai-lite
```

### 2. Ingest Data
Fetch WSPRNet monthly archives and load them into DuckDB:

```bash
wspr-ai-lite ingest --from 2014-07 --to 2014-07 --db data/wspr.duckdb
```
- Downloads compressed monthly CSVs (caches locally in .cache/)
- Normalizes into data/wspr.duckdb
- Adds extra fields (band, reporter grid, tx grid)

### 3. Launch the Dashboard
```bash
wspr-ai-lite ui --db data/wspr.duckdb --port 8501
```
Open http://localhost:8501 in your browser 🎉

👉 For developers who want to hack on the code directly, see [Developer Setup](https://ki7mt.github.io/wspr-ai-lite/DEV_SETUP/).

## Example Visualizations
- SNR Distribution by Count
- Monthly Spot Counts
- Top Reporting Stations
- Most Heard TX Stations
- Geographic Spread (Unique Grids)
- Distance Distribution + Longest DX
- Best DX per Band
- Activity by Hour × Month
- TX/RX Balance and QSO Success Rate

## Development

For contributors and developers:
- docs/dev-setup.md --> Development setup guide
- docs/testing.md --> Testing instructions (pytest + Makefile)
- docs/troubleshooting.md --> Common issues & fixes

```bash
make setup-dev   # create venv and install deps
make ingest      # run ingest pipeline
make run         # launch Streamlit UI
make test        # run pytest suite
```

### Makefile Usage

There is an extensive list of Makefile targets that simplify operations. See `make help` for a full list of available targets.

## Get Help
- **Report a bug** → [New Bug Report](https://github.com/KI7MT/wspr-ai-lite/issues/new?template=bug_report.yml)
- **Request a feature** → [New Feature Request](https://github.com/KI7MT/wspr-ai-lite/issues/new?template=feature_request.yml)
- **Ask a question / share ideas** → [GitHub Discussions](https://github.com/KI7MT/wspr-ai-lite/discussions)
- **Read the docs** → https://ki7mt.github.io/wspr-ai-lite/

## Acknowledgements
- Joe Taylor, K1JT, and the WSJT-X Development Team
- WSPRNet community for providing global weak-signal data
- Contributors to DuckDB and Streamlit
- Amateur radio operators worldwide who share spots and keep the network alive

## Contributing
Pull requests are welcome!

## Roadmap
- **Phase 1**: wspr-ai-lite (this project)
  - Lightweight, local-only DuckDB + Streamlit dashboard
- **Phase 2**: wspr-ai-analytics (modernize [wspr-analytics](https://github.com/KI7MT/wspr-analytics))
  - Full analytics suite with ClickHouse, Grafana, AI Agents, and MCP integration
  - Designed for heavier infrastructure and richer analysis

## 📜 License
MIT — free to use for amateur radio and research.
