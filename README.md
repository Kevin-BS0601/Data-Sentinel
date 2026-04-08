# Data-Sentinel
Data-Sentinel is a Streamlit-based data quality auditing app for CSV datasets. It helps users inspect dataset health, detect quality issues, and generate actionable cleaning suggestions.

## Features

- Upload and analyze CSV datasets
- Compute an overall data health score
- Detect:
  - missing values
  - duplicate rows
  - outliers
  - datatype inconsistencies
- Rank issues by priority
- Generate AI-assisted fix suggestions
- Export audit results as JSON
- Validate improvements using before/after comparison

## Tech Stack

- Python
- Streamlit
- Pandas

## Project Files

- `app.py` – main Streamlit app
- `scorer.py` – health score logic
- `detector.py` – profiling and issue detection
- `llm_client.py` – AI analysis integration
- `requirements.txt` – dependencies

## How to Run Locally

1. Clone the repository
2. Install dependencies:

```bash
pip install -r requirements.txt
