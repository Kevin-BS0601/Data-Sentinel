from typing import Dict, List, Tuple


def compute_health_score(profile: dict) -> Tuple[int, str, dict]:
    overview = profile["overview"]
    columns = profile["columns"]

    total_rows = max(overview.get("total_rows", 1), 1)
    total_columns = max(overview.get("total_columns", 1), 1)
    total_cells = total_rows * total_columns

    total_missing = overview.get("total_missing", 0)
    duplicate_rows = overview.get("duplicate_rows", 0)

    outlier_count = 0
    heavily_missing_columns = 0
    invalid_email_count = 0

    for col_data in columns.values():
        outliers = col_data.get("outliers")
        if isinstance(outliers, dict):
            outlier_count += outliers.get("count", 0)

        if col_data.get("missing_pct", 0) >= 40:
            heavily_missing_columns += 1

        invalid_emails = col_data.get("invalid_emails")
        if isinstance(invalid_emails, dict):
            invalid_email_count += invalid_emails.get("count", 0)

    missing_pct_dataset = (total_missing / total_cells) * 100 if total_cells else 0
    duplicate_pct = (duplicate_rows / total_rows) * 100 if total_rows else 0
    outlier_pct = (outlier_count / total_rows) * 100 if total_rows else 0
    invalid_email_pct = (invalid_email_count / total_rows) * 100 if total_rows else 0

    missing_penalty = int(missing_pct_dataset * 1.2)
    duplicate_penalty = int(duplicate_pct * 2.0)
    outlier_penalty = int(outlier_pct * 1.5)
    invalid_email_penalty = int(invalid_email_pct * 1.2)
    heavy_missing_penalty = heavily_missing_columns * 8

    total_penalty = (
        missing_penalty
        + duplicate_penalty
        + outlier_penalty
        + invalid_email_penalty
        + heavy_missing_penalty
    )

    score = 100 - total_penalty
    score = max(0, min(100, score))

    if score >= 80:
        verdict = "Healthy"
    elif score >= 55:
        verdict = "Needs attention"
    else:
        verdict = "Critical"

    breakdown = {
        "missing_penalty": missing_penalty,
        "duplicate_penalty": duplicate_penalty,
        "outlier_penalty": outlier_penalty,
        "invalid_email_penalty": invalid_email_penalty,
        "heavy_missing_penalty": heavy_missing_penalty,
        "total_penalty": total_penalty,
    }

    return score, verdict, breakdown


def assign_severity(column_data: dict) -> str:
    missing_pct = column_data.get("missing_pct", 0)

    outlier_count = 0
    outliers = column_data.get("outliers")
    if isinstance(outliers, dict):
        outlier_count = outliers.get("count", 0)

    invalid_email_count = 0
    invalid_emails = column_data.get("invalid_emails")
    if isinstance(invalid_emails, dict):
        invalid_email_count = invalid_emails.get("count", 0)

    if missing_pct >= 40 or invalid_email_count > 10:
        return "critical"
    if missing_pct >= 10 or outlier_count > 0 or invalid_email_count > 0:
        return "warning"
    return "clean"


def classify_issues(profile: dict) -> List[Dict]:
    issues = []

    overview = profile["overview"]
    columns = profile["columns"]

    duplicate_rows = overview.get("duplicate_rows", 0)
    if duplicate_rows > 0:
        issues.append({
            "severity": "warning" if duplicate_rows < 10 else "critical",
            "title": "Duplicate rows detected",
            "detail": f"{duplicate_rows} duplicate row(s) found in the dataset.",
            "action": "Review duplicated records and remove exact duplicates if they are not intentional."
        })

    for col_name, col_data in columns.items():
        missing = col_data.get("missing", 0)
        missing_pct = col_data.get("missing_pct", 0)

        outlier_count = 0
        outlier_pct = 0
        outliers = col_data.get("outliers")
        if isinstance(outliers, dict):
            outlier_count = outliers.get("count", 0)
            outlier_pct = outliers.get("pct", 0)

        invalid_email_count = 0
        invalid_email_pct = 0
        invalid_emails = col_data.get("invalid_emails")
        if isinstance(invalid_emails, dict):
            invalid_email_count = invalid_emails.get("count", 0)
            invalid_email_pct = invalid_emails.get("pct", 0)

        if missing > 0:
            severity = "critical" if missing_pct >= 40 else "warning"
            action = (
                "Investigate the data source first. If values are genuinely missing, consider imputation or excluding this column from downstream analysis."
                if missing_pct >= 40
                else "Consider filling missing values using a suitable strategy such as median, mode, or source correction."
            )

            issues.append({
                "severity": severity,
                "title": f"{col_name}: missing values",
                "detail": f"{missing} missing value(s) detected ({missing_pct}%).",
                "action": action
            })

        if outlier_count > 0:
            issues.append({
                "severity": "warning",
                "title": f"{col_name}: outliers detected",
                "detail": f"{outlier_count} possible outlier(s) detected ({outlier_pct}%).",
                "action": "Inspect whether these values are valid extremes or data entry errors before removing or capping them."
            })

        if invalid_email_count > 0:
            issues.append({
                "severity": "critical" if invalid_email_pct >= 10 else "warning",
                "title": f"{col_name}: invalid email values",
                "detail": f"{invalid_email_count} invalid email value(s) detected ({invalid_email_pct}%).",
                "action": "Review malformed email values, correct formatting issues, and validate the source system generating these addresses."
            })

    severity_rank = {"critical": 0, "warning": 1, "clean": 2}
    issues.sort(key=lambda x: severity_rank.get(x["severity"], 99))

    return issues


def severity_badge(severity: str) -> str:
    if severity == "critical":
        return "🔴 Critical"
    if severity == "warning":
        return "🟡 Warning"
    return "🟢 Clean" 

from typing import Dict, List, Tuple


def compute_health_score(profile: dict) -> Tuple[int, str, dict]:
    overview = profile["overview"]
    columns = profile["columns"]

    total_rows = max(overview.get("total_rows", 1), 1)
    total_columns = max(overview.get("total_columns", 1), 1)
    total_cells = total_rows * total_columns

    total_missing = overview.get("total_missing", 0)
    duplicate_rows = overview.get("duplicate_rows", 0)

    outlier_count = 0
    heavily_missing_columns = 0
    invalid_email_count = 0

    for col_data in columns.values():
        outliers = col_data.get("outliers")
        if isinstance(outliers, dict):
            outlier_count += outliers.get("count", 0)

        if col_data.get("missing_pct", 0) >= 40:
            heavily_missing_columns += 1

        invalid_emails = col_data.get("invalid_emails")
        if isinstance(invalid_emails, dict):
            invalid_email_count += invalid_emails.get("count", 0)

    missing_pct_dataset = (total_missing / total_cells) * 100 if total_cells else 0
    duplicate_pct = (duplicate_rows / total_rows) * 100 if total_rows else 0
    outlier_pct = (outlier_count / total_rows) * 100 if total_rows else 0
    invalid_email_pct = (invalid_email_count / total_rows) * 100 if total_rows else 0

    missing_penalty = int(missing_pct_dataset * 1.2)
    duplicate_penalty = int(duplicate_pct * 2.0)
    outlier_penalty = int(outlier_pct * 1.5)
    invalid_email_penalty = int(invalid_email_pct * 1.2)
    heavy_missing_penalty = heavily_missing_columns * 8

    total_penalty = (
        missing_penalty
        + duplicate_penalty
        + outlier_penalty
        + invalid_email_penalty
        + heavy_missing_penalty
    )

    score = 100 - total_penalty
    score = max(0, min(100, score))

    if score >= 80:
        verdict = "Healthy"
    elif score >= 55:
        verdict = "Needs attention"
    else:
        verdict = "Critical"

    breakdown = {
        "missing_penalty": missing_penalty,
        "duplicate_penalty": duplicate_penalty,
        "outlier_penalty": outlier_penalty,
        "invalid_email_penalty": invalid_email_penalty,
        "heavy_missing_penalty": heavy_missing_penalty,
        "total_penalty": total_penalty,
    }

    return score, verdict, breakdown


def assign_severity(column_data: dict) -> str:
    missing_pct = column_data.get("missing_pct", 0)

    outlier_count = 0
    outliers = column_data.get("outliers")
    if isinstance(outliers, dict):
        outlier_count = outliers.get("count", 0)

    invalid_email_count = 0
    invalid_emails = column_data.get("invalid_emails")
    if isinstance(invalid_emails, dict):
        invalid_email_count = invalid_emails.get("count", 0)

    if missing_pct >= 40 or invalid_email_count > 10:
        return "critical"
    if missing_pct >= 10 or outlier_count > 0 or invalid_email_count > 0:
        return "warning"
    return "clean"


def classify_issues(profile: dict) -> List[Dict]:
    issues = []

    overview = profile["overview"]
    columns = profile["columns"]

    duplicate_rows = overview.get("duplicate_rows", 0)
    if duplicate_rows > 0:
        issues.append({
            "severity": "warning" if duplicate_rows < 10 else "critical",
            "title": "Duplicate rows detected",
            "detail": f"{duplicate_rows} duplicate row(s) found in the dataset.",
            "action": "Review duplicated records and remove exact duplicates if they are not intentional."
        })

    for col_name, col_data in columns.items():
        missing = col_data.get("missing", 0)
        missing_pct = col_data.get("missing_pct", 0)

        outlier_count = 0
        outlier_pct = 0
        outliers = col_data.get("outliers")
        if isinstance(outliers, dict):
            outlier_count = outliers.get("count", 0)
            outlier_pct = outliers.get("pct", 0)

        invalid_email_count = 0
        invalid_email_pct = 0
        invalid_emails = col_data.get("invalid_emails")
        if isinstance(invalid_emails, dict):
            invalid_email_count = invalid_emails.get("count", 0)
            invalid_email_pct = invalid_emails.get("pct", 0)

        if missing > 0:
            severity = "critical" if missing_pct >= 40 else "warning"
            action = (
                "Investigate the data source first. If values are genuinely missing, consider imputation or excluding this column from downstream analysis."
                if missing_pct >= 40
                else "Consider filling missing values using a suitable strategy such as median, mode, or source correction."
            )

            issues.append({
                "severity": severity,
                "title": f"{col_name}: missing values",
                "detail": f"{missing} missing value(s) detected ({missing_pct}%).",
                "action": action
            })

        if outlier_count > 0:
            issues.append({
                "severity": "warning",
                "title": f"{col_name}: outliers detected",
                "detail": f"{outlier_count} possible outlier(s) detected ({outlier_pct}%).",
                "action": "Inspect whether these values are valid extremes or data entry errors before removing or capping them."
            })

        if invalid_email_count > 0:
            issues.append({
                "severity": "critical" if invalid_email_pct >= 10 else "warning",
                "title": f"{col_name}: invalid email values",
                "detail": f"{invalid_email_count} invalid email value(s) detected ({invalid_email_pct}%).",
                "action": "Review malformed email values, correct formatting issues, and validate the source system generating these addresses."
            })

    severity_rank = {"critical": 0, "warning": 1, "clean": 2}
    issues.sort(key=lambda x: severity_rank.get(x["severity"], 99))

    return issues


def severity_badge(severity: str) -> str:
    if severity == "critical":
        return "🔴 Critical"
    if severity == "warning":
        return "🟡 Warning"
    return "🟢 Clean"