from embedding.openai_client import _client
import json

INTENT_PROMPT = """
You are an intent extraction system for SHL assessments.

SHL test type codes:
A = Ability & Aptitude
B = Biodata & Situational Judgement
C = Competencies
D = Development & 360
E = Assessment Exercises
K = Knowledge & Skills
P = Personality & Behavior
S = Simulations

Valid experience levels:
- Entry-Level
- Graduate
- Mid-Professional
- Professional Individual Contributor
- Manager
- Executive
- Director
- General Population
- Front Line Manager
- Supervisor

Return ONLY valid JSON in this format:
{
  "required_test_types": [],
  "preferred_test_types": [],
  "remote_required": "Yes" | "No" | "Unknown",
  "adaptive_required": "Yes" | "No" | "Unknown",
  "experience_level": "DoesNotMatter",
  "time_constraint_minutes": 0
}

Rules:
- If no time limit is specified or implied, set time_constraint_minutes to 0.
- If a time limit is mentioned or implied (e.g. "90 mins", "under an hour", "short"), convert it to minutes and return an integer.
- If experience level is not specified, set experience_level to "DoesNotMatter".
- Do NOT return null for experience_level or time_constraint_minutes.
"""

def extract_intent(query: str) -> dict:
    response = _client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": INTENT_PROMPT},
            {"role": "user", "content": query}
        ],
        response_format={"type": "json_object"},
    )

    content = response.choices[0].message.content

    try:
        return json.loads(content)
    except Exception:
        return {
            "required_test_types": [],
            "preferred_test_types": [],
            "remote_required": "Unknown",
            "adaptive_required": "Unknown",
            "experience_level": "DoesNotMatter",
            "time_constraint_minutes": 0
        }
