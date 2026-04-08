import pandas as pd
import numpy as np


def profile_dataframe(df: pd.DataFrame) -> dict:
    """
    Analyzes a DataFrame and returns a profile of data quality issues.

    Returns a dict with:
      - overview:  high-level dataset stats
      - columns:   per-column analysis (missing, dtype, unique, outliers)
    """

    profile = {
        "overview": _get_overview(df),
        "columns": {}
    }

    for col in df.columns:
        profile["columns"][col] = _profile_column(df[col])

    return profile


# ── helpers ───────────────────────────────────────────────────────────────────

def _get_overview(df: pd.DataFrame) -> dict:
    return {
        "total_rows": len(df),
        "total_columns": len(df.columns),
        "total_missing": int(df.isnull().sum().sum()),
        "duplicate_rows": int(df.duplicated().sum()),
    }


def _profile_column(series: pd.Series) -> dict:
    total = len(series)
    null_count = int(series.isnull().sum())

    result = {
        "dtype": str(series.dtype),
        "total": total,
        "missing": null_count,
        "missing_pct": round(null_count / total * 100, 1) if total else 0,
        "unique": int(series.nunique(dropna=True)),
        "outliers": None,   # only filled for numeric columns
    }

    # Outlier detection for numeric columns
    if pd.api.types.is_numeric_dtype(series):
        result["outliers"] = _count_outliers(series)

    return result


def _count_outliers(series: pd.Series) -> dict:
    """
    Detect outliers in a numeric series.

    Strategy:
    - For very small samples (3-4 values), use Modified Z-score
    - For larger samples, use IQR
    """
    clean = series.dropna()

    if len(clean) < 3:
        return {"count": 0, "pct": 0.0}

    # Small sample fallback: Modified Z-score
    if len(clean) < 5:
        median = clean.median()
        mad = np.median(np.abs(clean - median))

        if mad == 0:
            return {"count": 0, "pct": 0.0}

        modified_z_scores = 0.6745 * (clean - median) / mad
        count = int((np.abs(modified_z_scores) > 3.5).sum())

        return {
            "count": count,
            "pct": round(count / len(series) * 100, 1),
        }

    # Larger sample: IQR method
    q1 = clean.quantile(0.25)
    q3 = clean.quantile(0.75)
    iqr = q3 - q1

    if iqr == 0:
        return {"count": 0, "pct": 0.0}

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    count = int(((clean < lower) | (clean > upper)).sum())

    return {
        "count": count,
        "pct": round(count / len(series) * 100, 1),
    }
