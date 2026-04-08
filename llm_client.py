import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)


def build_prompt(profile: dict) -> str:
    overview = profile["overview"]
    columns = profile["columns"]

    issue_lines = []

    for col_name, data in columns.items():
        if data.get("missing", 0) > 0:
            issue_lines.append(
                f"- {col_name}: {data['missing']} missing values ({data['missing_pct']}%)"
            )

        outliers = data.get("outliers")
        if isinstance(outliers, dict) and outliers.get("count", 0) > 0:
            issue_lines.append(
                f"- {col_name}: {outliers['count']} outliers ({outliers['pct']}%)"
            )

        invalid_emails = data.get("invalid_emails")
        if isinstance(invalid_emails, dict) and invalid_emails.get("count", 0) > 0:
            issue_lines.append(
                f"- {col_name}: {invalid_emails['count']} invalid email values ({invalid_emails['pct']}%)"
            )

    if overview.get("duplicate_rows", 0) > 0:
        issue_lines.append(
            f"- dataset: {overview['duplicate_rows']} duplicate rows"
        )

    if not issue_lines:
        issue_lines.append("- no major issues detected")

    issues_text = "\n".join(issue_lines)

    return f"""
You are a senior data engineer.

Analyze this dataset profile and return STRICT JSON.

Rules:
- No paragraphs
- No explanations
- Output must be SHORT and ACTIONABLE
- Every recommendation MUST include real pandas code

Return format:

{{
  "summary": "1-2 lines max",
  "top_risk": "single most critical issue",

  "column_recommendations": [
    {{
      "column": "column_name",
      "issue": "short issue",
      "recommendation": "ONE LINE pandas fix code"
    }}
  ],

  "next_steps": [
    "short step",
    "short step"
  ]
}}

Dataset profile:
{profile}
"""
    

def get_ai_analysis(profile: dict) -> dict:
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in .env file")

    prompt = build_prompt(profile)

    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content(prompt)

    raw_text = response.text.strip() if response.text else ""

    try:
        parsed = json.loads(raw_text)
    except json.JSONDecodeError:
        start = raw_text.find("{")
        end = raw_text.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(raw_text[start:end + 1])
            except json.JSONDecodeError:
                raise ValueError("Gemini returned malformed JSON")
        else:
            raise ValueError("Gemini did not return valid JSON")

    return {
        "summary": parsed.get("summary", "No summary returned."),
        "top_risk": parsed.get("top_risk", ""),
        "column_recommendations": parsed.get("column_recommendations", []),
        "next_steps": parsed.get("next_steps", []),
    }
