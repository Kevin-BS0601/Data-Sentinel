import json
from datetime import datetime

import pandas as pd
import streamlit as st

from detector import profile_dataframe
from llm_client import get_ai_analysis
from scorer import compute_health_score, assign_severity, classify_issues, severity_badge


def build_audit_report(uploaded_file_name, profile, health_score, health_label, issues, ai_result=None):
    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source_file": uploaded_file_name,
        "dataset_health": {
            "score": health_score,
            "label": health_label,
        },
        "overview": profile["overview"],
        "columns": profile["columns"],
        "fix_priority": issues,
        "ai_analysis": ai_result if ai_result else None,
    }


# ── page setup ────────────────────────────────────────────────────────────────

st.set_page_config(page_title="DataSentinel", page_icon="🔍", layout="wide")

# Minimal CSS — only targets elements Streamlit cannot style natively.
# Scoped to three things: hero card container, score number, status badge.
st.markdown("""
<style>
:root {
    --bg-0: #070b14;
    --panel-0: #0f1626;
    --panel-1: #131d31;
    --line-0: rgba(255,255,255,0.08);
    --text-0: #e5ecfa;
    --text-1: #b8c4dc;
    --text-2: #8f9ab3;
    --brand-0: #7c8dff;
    --brand-1: #5a6dff;
}

[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(900px 420px at 82% -2%, rgba(124,141,255,0.10) 0%, rgba(7,11,20,0) 60%),
        radial-gradient(680px 300px at -8% 0%, rgba(64,120,255,0.07) 0%, rgba(7,11,20,0) 58%),
        var(--bg-0);
}

.main .block-container {
    padding-top: 1.65rem;
    padding-bottom: 1.2rem;
    max-width: 1160px;
    font-family: -apple-system, BlinkMacSystemFont, "Helvetica Neue", Helvetica, Arial, sans-serif;
    color: var(--text-0);
}

h1, h2, h3 {
    letter-spacing: -0.02em;
    color: #f3f7ff;
}

h1 {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.05;
    margin-bottom: 0.18rem;
}
.ds-title-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.2rem;
}
.ds-title-icon {
    width: 30px;
    height: 30px;
    object-fit: contain;
    flex: 0 0 30px;
}
.ds-title-text {
    font-size: 2.2rem;
    font-weight: 800;
    line-height: 1.2;
    letter-spacing: -0.02em;
    color: #f3f7ff;
    margin: 0;
    padding: 0;
}

.ds-title-text-inline {
    margin: 0;
    padding: 0;
}

h2 {
    font-size: 1.08rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    margin-top: 0.2rem;
    margin-bottom: 0.28rem;
    color: #d3def5;
}

.stCaption {
    font-size: 0.78rem;
    color: var(--text-2);
    letter-spacing: 0.01em;
}

[data-testid="stMetric"] {
    background: linear-gradient(180deg, rgba(19,29,49,0.92) 0%, rgba(15,22,38,0.92) 100%);
    border: 1px solid var(--line-0);
    border-radius: 12px;
    padding: 10px 12px;
}

[data-testid="stMetricLabel"] {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--text-2);
}

[data-testid="stMetricValue"] {
    font-size: 1.18rem;
    font-weight: 700;
}

.ds-hero {
    border: 1px solid rgba(124,141,255,0.30);
    border-radius: 14px;
    padding: 20px 24px 18px 24px;
    margin: 10px 0 12px 0;
    display: flex;
    justify-content: space-between;
    align-items: stretch;
    gap: 22px;
    background: linear-gradient(
        140deg,
        rgba(124,141,255,0.20) 0%,
        rgba(29,43,75,0.86) 46%,
        rgba(18,28,46,0.94) 100%
    );
    box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.08),
        0 18px 34px rgba(0,0,0,0.30);
    position: relative;
    overflow: hidden;
}
.ds-hero:before {
    content: "";
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 4px;
    background: linear-gradient(180deg, #9ba8ff 0%, #5c70ff 100%);
}
.ds-hero-main {
    padding-left: 8px;
}
.ds-score {
    font-size: 78px;
    font-weight: 800;
    line-height: 1;
    letter-spacing: -1.5px;
}
.ds-grade {
    font-size: 20px;
    font-weight: 600;
    opacity: 0.74;
    margin-left: 7px;
}
.ds-badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    margin-bottom: 7px;
}
.ds-badge-green  { background:#052e16; color:#4ade80; border:1px solid #166534; }
.ds-badge-amber  { background:#2d1a00; color:#fbbf24; border:1px solid #92400e; }
.ds-badge-red    { background:#2d0a0a; color:#f87171; border:1px solid #991b1b; }
.ds-meta {
    font-size: 11px;
    color: var(--text-2);
    letter-spacing: 0.02em;
    margin-top: 5px;
}
.ds-hero-stats {
    min-width: 240px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}
.ds-hero-stat {
    border: 1px solid rgba(255,255,255,0.10);
    border-radius: 10px;
    padding: 8px 10px;
    background: rgba(10,16,30,0.36);
}
.ds-hero-stat-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-2);
}
.ds-hero-stat-value {
    margin-top: 2px;
    font-size: 16px;
    font-weight: 700;
    color: #f4f8ff;
}

.ds-preview-label {
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-2);
    margin: 0 0 3px 2px;
}
.ds-divider { border: none; border-top: 1px solid rgba(255,255,255,0.05); margin: 1px 0 9px 0; }

/* Compact issue rows */
.ds-issue-row {
    display: grid;
    grid-template-columns: 20px 1fr;
    column-gap: 8px;
    row-gap: 1px;
    padding: 6px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    font-size: 12px;
}
.ds-issue-row:last-child { border-bottom: none; }
.ds-issue-num  { opacity: 0.28; font-size: 10px; padding-top: 1px; }
.ds-issue-main { display: flex; align-items: baseline; gap: 7px; flex-wrap: wrap; }
.ds-issue-title{ font-weight: 650; }
.ds-issue-detail{ color: var(--text-1); opacity: 0.62; font-size: 11px; }
.ds-issue-action{
    grid-column: 2 / -1;
    font-size: 10px;
    color: var(--text-2);
    opacity: 0.9;
    font-style: italic;
}
.ds-fix-heading {
    margin-top: 0;
    margin-bottom: 5px;
    font-size: 1rem;
    font-weight: 750;
    letter-spacing: -0.015em;
    color: #f3f7ff;
}
.ds-fix-note {
    font-size: 11px;
    color: var(--text-2);
    margin-bottom: 7px;
}
</style>
""", unsafe_allow_html=True)

title_icon_col, title_text_col = st.columns([0.8, 24], gap="small")
with title_icon_col:
    st.image("datasentinel_icon.png", width=44)
with title_text_col:
    st.markdown("<div class='ds-title-text ds-title-text-inline'>DataSentinel</div>", unsafe_allow_html=True)
st.caption("Instant data quality audit for any CSV.")


# ── upload ────────────────────────────────────────────────────────────────────

uploaded = st.file_uploader("Choose a CSV file", type="csv")

if uploaded is None:
    st.info("Upload a CSV file above to get started.")
    st.stop()


# ── load data ─────────────────────────────────────────────────────────────────

try:
    df = pd.read_csv(uploaded)
except Exception as e:
    st.error(f"Could not read file: {e}")
    st.stop()

st.caption(f"Loaded {len(df):,} rows • {len(df.columns)} columns")


# ── preview — collapsed by default ───────────────────────────────────────────

st.markdown("<div class='ds-preview-label'>Data preview</div>", unsafe_allow_html=True)
with st.expander("Preview data (first 10 rows)", expanded=False):
    st.dataframe(df.head(10), use_container_width=True, height=180)


# ── profiling ─────────────────────────────────────────────────────────────────

profile = profile_dataframe(df)
health_score, health_label, breakdown = compute_health_score(profile)
issues = classify_issues(profile)

overview = profile["overview"]
columns = profile["columns"]

if "ai_result" not in st.session_state:
    st.session_state.ai_result = None


# ── HEALTH SCORE — hero card ──────────────────────────────────────────────────

# Grade letter
def _grade(s):
    if s >= 90: return "A"
    if s >= 75: return "B"
    if s >= 60: return "C"
    if s >= 40: return "D"
    return "F"

# Badge class — amber for warning, not green
if health_score >= 80:
    badge_cls = "ds-badge-green"
elif health_score >= 50:
    badge_cls = "ds-badge-amber"   # was st.warning → green-adjacent; now amber
else:
    badge_cls = "ds-badge-red"

grade = _grade(health_score)

st.markdown(f"""
<div class="ds-hero">
  <div class="ds-hero-main">
    <span class="ds-score">{health_score}</span><span class="ds-grade">/ 100 &nbsp; {grade}</span>
    <div style="margin-top:10px;">
      <span class="ds-badge {badge_cls}">{health_label}</span>
    </div>
    <div class="ds-meta">Based on missing data, duplicates, outliers, and consistency signals.</div>
  </div>
  <div class="ds-hero-stats">
    <div class="ds-hero-stat">
      <div class="ds-hero-stat-label">Rows</div>
      <div class="ds-hero-stat-value">{overview['total_rows']:,}</div>
    </div>
    <div class="ds-hero-stat">
      <div class="ds-hero-stat-label">Columns</div>
      <div class="ds-hero-stat-value">{overview['total_columns']}</div>
    </div>
    <div class="ds-hero-stat">
      <div class="ds-hero-stat-label">Missing cells</div>
      <div class="ds-hero-stat-value">{overview['total_missing']:,}</div>
    </div>
    <div class="ds-hero-stat">
      <div class="ds-hero-stat-label">Priority issues</div>
      <div class="ds-hero-stat-value">{len(issues)}</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── score breakdown ───────────────────────────────────────────────────────────

penalties = [
    (label, val) for label, val in [
        ("Missing",           breakdown["missing_penalty"]),
        ("Duplicates",        breakdown["duplicate_penalty"]),
        ("Outliers",          breakdown["outlier_penalty"]),
        ("Bad emails",        breakdown["invalid_email_penalty"]),
        ("Heavy missing cols",breakdown["heavy_missing_penalty"]),
    ] if val != 0
]

if penalties:
    st.markdown("**Why your score is " + str(health_score) + "**")
    cols = st.columns(len(penalties))
    for col, (label, value) in zip(cols, penalties):
        col.metric(label, f"−{value}")          # use − (minus sign) not hyphen

    main_issue = max(penalties, key=lambda x: x[1])
    st.caption(
        f"{main_issue[0]} is your biggest drag — "
        f"responsible for {main_issue[1]} of the score penalty."
    )


# ── dataset overview ──────────────────────────────────────────────────────────

st.markdown("<hr class='ds-divider'>", unsafe_allow_html=True)
st.subheader("Dataset overview")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Rows",           f"{overview['total_rows']:,}")
c2.metric("Columns",        overview["total_columns"])
c3.metric("Missing cells",  f"{overview['total_missing']:,}")
c4.metric("Duplicate rows", f"{overview['duplicate_rows']:,}")


# ── column breakdown ──────────────────────────────────────────────────────────

st.markdown("<hr class='ds-divider'>", unsafe_allow_html=True)
st.subheader("Column breakdown")

show_invalid_email_column = any(
    isinstance(info.get("invalid_emails"), dict) and info["invalid_emails"].get("count", 0) > 0
    for info in columns.values()
)

rows = []
for col_name, info in columns.items():
    severity = assign_severity(info)

    outlier_text = (
        f"{info['outliers']['count']} ({info['outliers']['pct']}%)"
        if isinstance(info.get("outliers"), dict) and info["outliers"]["count"] > 0
        else "—"
    )

    invalid_email_text = (
        f"{info['invalid_emails']['count']} ({info['invalid_emails']['pct']}%)"
        if isinstance(info.get("invalid_emails"), dict) and info["invalid_emails"]["count"] > 0
        else "—"
    )

    missing_pct = info["missing_pct"]
    missing_label = (
        "✔︎ 0%"      if missing_pct == 0  else
        f"🟡 {missing_pct}%"  if missing_pct < 10 else
        f"🔴 {missing_pct}%"
    )

    row = {
        "Column":        col_name,
        "Data type":     info["dtype"],
        "Missing":       missing_label,
        "Unique values": info["unique"],
        "Outliers":      outlier_text,
        "Severity":      severity_badge(severity),
    }
    if show_invalid_email_column:
        row["Invalid emails"] = invalid_email_text

    rows.append(row)

st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


# ── issues ranked by priority — compact rows ──────────────────────────────────

st.markdown("<hr class='ds-divider'>", unsafe_allow_html=True)

if issues:
    st.subheader("Issues ranked by priority")
    st.caption("Resolve highest-severity items first.")

    # Build one HTML block for all rows — avoids per-item Streamlit overhead
    rows_html = ""
    for i, item in enumerate(issues, 1):
        badge  = severity_badge(item["severity"])   # returns e.g. "🟡 Warning"
        rows_html += f"""
        <div class="ds-issue-row">
          <span class="ds-issue-num">{i}</span>
          <div class="ds-issue-main">
            <span class="ds-issue-title">{badge} &nbsp; {item['title']}</span>
            <span class="ds-issue-detail">{item['detail']}</span>
          </div>
          <div class="ds-issue-action">💡 {item['action']}</div>
        </div>
        """

    st.markdown(rows_html, unsafe_allow_html=True)

else:
    st.success("No issues found — dataset looks clean.")


# ── AI insights ───────────────────────────────────────────────────────────────

st.markdown("<hr class='ds-divider'>", unsafe_allow_html=True)
st.subheader("AI recommendations")
st.caption("Column stats are sent to the AI — your raw data never leaves your machine.")

if st.button("Analyse with AI", type="primary"):
    try:
        with st.spinner("Analysing…"):
            result = get_ai_analysis(profile)
        st.session_state.ai_result = result
    except Exception as e:
        st.error(f"Error: {e}")

if st.session_state.ai_result:
    result = st.session_state.ai_result

    # ── Fix Code first — lead with the answer ────────────────────────────────
    if result.get("column_recommendations"):
        st.markdown("<div class='ds-fix-heading'>Fix code (copy and run first)</div>", unsafe_allow_html=True)
        st.markdown("<div class='ds-fix-note'>Start here before reading the summary.</div>", unsafe_allow_html=True)
        for item in result["column_recommendations"]:
            col_name = item.get("column", "")
            issue    = item.get("issue", "")
            fix      = item.get("recommendation", "")
            st.markdown(
                f"<span style='font-size:13px; opacity:0.7'>"
                f"{col_name} — {issue}</span>",
                unsafe_allow_html=True,
            )
            st.code(fix, language="python")

    # ── Top risk ─────────────────────────────────────────────────────────────
    if result.get("top_risk"):
        st.markdown("**Top risk**")
        st.error(result["top_risk"])

    # ── Summary ──────────────────────────────────────────────────────────────
    if result.get("summary"):
        st.markdown("**AI summary**")
        st.caption(result["summary"])

    # ── Next steps ───────────────────────────────────────────────────────────
    if result.get("next_steps"):
        st.markdown("**Next steps**")
        for step in result["next_steps"]:
            st.markdown(f"- {step}")


# ── export ────────────────────────────────────────────────────────────────────

st.markdown("<hr class='ds-divider'>", unsafe_allow_html=True)
st.subheader("Export")

audit_report = build_audit_report(
    uploaded_file_name=uploaded.name,
    profile=profile,
    health_score=health_score,
    health_label=health_label,
    issues=issues,
    ai_result=st.session_state.ai_result,
)

st.download_button(
    label     = "Download audit report (.json)",
    data      = json.dumps(audit_report, indent=2),
    file_name = f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
    mime      = "application/json",
)


# ── validate improvements ─────────────────────────────────────────────────────

st.markdown("<hr class='ds-divider'>", unsafe_allow_html=True)
st.subheader("Validate improvements")
st.caption("Apply your fixes, export the cleaned CSV, then upload it here to see the score delta.")

cleaned_file = st.file_uploader(
    "Upload your cleaned CSV to compare",
    type="csv",
    key="cleaned",
)

if cleaned_file:
    try:
        df_clean = pd.read_csv(cleaned_file)

        profile_clean              = profile_dataframe(df_clean)
        score_clean, label_clean, _ = compute_health_score(profile_clean)
        delta                      = score_clean - health_score

        col1, col2, col3 = st.columns(3)
        col1.metric("Original score", health_score)
        col2.metric("Cleaned score",  score_clean)

        if delta > 0:
            col3.metric("Improvement", f"+{delta}")
            st.success(f"Score improved by {delta} points after your fixes.")
        elif delta == 0:
            col3.metric("Change", "0")
            st.info("No change in score — the files may be identical or fixes had no measurable effect.")
        else:
            col3.metric("Regression", str(delta))
            st.error(
                f"Score dropped by {abs(delta)} points. "
                "Check whether the cleaned file introduced new issues."
            )

    except Exception as e:
        st.error(f"Could not read cleaned file: {e}")
