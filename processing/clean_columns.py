import re
import pandas as pd

def extract_fields(description: str):
    if not isinstance(description, str):
        return {
            "job_levels": None,
            "languages": None,
            "duration_minutes": None,
            "test_type": []
        }

    # Job Levels
    job_levels_match = re.search(
    r"Job levels\s+(.*?)(?=Languages|Assessment length|Test Type:)",
    description,
    re.IGNORECASE | re.DOTALL
)
    job_levels = (
        [j.strip() for j in job_levels_match.group(1).split(",")]
        if job_levels_match else None
    )

    # Languages
    languages_match = re.search(
    r"Languages\s+(.*?)(?=Assessment length|Test Type:)",
    description,
    re.IGNORECASE | re.DOTALL
)
    languages = (
        [l.strip() for l in languages_match.group(1).split(",")]
        if languages_match else None
    )

    # Duration
    duration_match = re.search(
        r"(?:Completion Time in minutes\s*=\s*|Assessment length\s*)(Untimed|Variable|max\s*\d+|\d+)",
        description,
        re.IGNORECASE
    )

    duration_raw = duration_match.group(1) if duration_match else None
    if duration_raw and duration_raw.isdigit():
        duration_minutes = int(duration_raw)
    else:
        duration_minutes = duration_raw  # Untimed / Variable / max 60

    # Test Type
    test_type_match = re.search(
        r"Test Type:\s*([A-Z\s]+)",
        description,
        re.IGNORECASE
    )
    test_type = (
    re.findall(r"[A-Z]", test_type_match.group(1))
    if test_type_match else []
)

    return {
        "job_levels": job_levels,
        "languages": languages,
        "duration_minutes": duration_minutes,
        "test_type": test_type
    }

df = pd.read_csv("data/processed/assessments_clean.csv")

parsed = df["description"].apply(extract_fields)

parsed_df = pd.json_normalize(parsed)

df_final = pd.concat([df, parsed_df], axis=1)

df_final.to_csv("data/processed/assessments_structured.csv", index=False)
print("✅ Parsed CSV saved to data/processed/assessments_structured.csv")