# 🔍 DataSentinel

**Automated data quality auditing for CSV datasets — score health, rank issues, generate fix code.**

**[→ Live Demo](https://data-sentinel-vdbjrmxm7jwuauxsdjqgb4.streamlit.app/)** &nbsp;|&nbsp; Python · Streamlit · Pandas · Gemini API

---

## What it does

Most data quality checks are either too heavy (Great Expectations, dbt test suites) or too shallow (`df.info()`). DataSentinel sits in between: upload a CSV, get a scored audit report with ranked issues, column-level diagnostics, and working Pandas fix code — in under 10 seconds.

It is designed for the moment before analysis or model training begins, when you need to know *how bad is this data and what do I fix first* — not a full pipeline contract.

---

## Features

| Feature | Detail |
|---|---|
| Health score (0–100) | Rule-based score with per-penalty breakdown |
| Issue ranking | Issues sorted by severity — critical before warning |
| Column diagnostics | Missing %, outliers, invalid emails, data types |
| AI fix code | Gemini generates executable Pandas snippets per column |
| Before/after comparison | Upload a cleaned CSV to see the score delta |
| JSON export | Full audit report with timestamp, downloadable |

---

## How the health score works

The score starts at 100 and subtracts weighted penalties:

| Signal | Penalty weight | Rationale |
|---|---|---|
| Missing values | 1.2× the missing % | Propagate silently into aggregations |
| Duplicate rows | 2.0× the duplicate % | Inflate every count and distort aggregates |
| Outliers | 1.5× the outlier % | Bias means; severity depends on analysis type |
| Invalid emails | 1.2× the invalid % | Silent join failures in CRM/marketing pipelines |
| Heavily missing columns (≥40%) | −8 pts each | Structural problem, not a fill problem |

Score ranges: **80–100** Healthy · **55–79** Needs attention · **0–54** Critical

This is a practical auditing signal, not a statistical standard. The weights encode a specific opinion about downstream risk — they are documented so you can adjust them for your context.

---

## Architecture

```
detector.py        — profiles raw DataFrame: missing %, outliers, email validity
      ↓
scorer.py          — computes health score, classifies severity, ranks issues
      ↓
llm_client.py      — sends profile summary (not raw data) to Gemini, parses structured JSON
      ↓
app.py             — Streamlit UI: orchestrates all modules, manages session state
```

All detection and scoring runs locally. Only column-level statistics (no raw values) are sent to the AI.

---

## Screenshots

### Dashboard — health score card and score breakdown
![Dashboard](screenshots/dashboard.png)

### Column breakdown — per-column diagnostics with severity badges
![Column Breakdown](screenshots/column_breakdown.png)

### AI recommendations — fix code and top risk, generated from the profile
![AI Recommendations](screenshots/ai_recommendations.png)

---

## Tech stack

- **Python 3.11**
- **Streamlit** — UI framework
- **Pandas + NumPy** — data profiling and outlier detection
- **Google Gemini 2.5 Flash** — AI fix code generation
- **python-dotenv** — local API key management

---

## Run locally

```bash
git clone https://github.com/Kevin-BS0601/Data-Sentinel.git
cd Data-Sentinel
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Run the app:

```bash
streamlit run app.py
```

The app runs without an API key — the AI section will be disabled, but all detection and scoring works offline.

---

## Project structure

```
app.py             — Streamlit application and UI layout
detector.py        — DataFrame profiling (missing values, outliers, email validation)
scorer.py          — Health score calculation and issue classification
llm_client.py      — Gemini API integration and prompt handling
requirements.txt   — Pinned dependencies
screenshots/       — UI screenshots for README
```

---

## Why I built this

Data cleaning is the most time-consuming part of most ML and analytics projects. The usual workflow is `df.info()`, `df.describe()`, some manual column checks — repeated across every new dataset. I built DataSentinel to compress that into a single scored report with a prioritised fix list, so the first 10 minutes of any data project are faster and more systematic.

The before/after comparison feature came from a specific frustration: after cleaning a dataset it's not always obvious whether your fixes actually improved things or introduced new problems. The score delta makes that concrete.

---

*Built by Kevin · M.Sc. Artificial Intelligence · BTU Cottbus-Senftenberg*
