def adjust_score(base_score, record, intent):
    score = base_score

    # 1. Required test types (HARD constraint)
    required = set(intent["required_test_types"])
    record_types = set(record["test_type"] or [])

    if required and not required.intersection(record_types):
        score -= 0.5

    # 2. Preferred test types (SOFT boost)
    preferred = set(intent["preferred_test_types"])
    if preferred.intersection(record_types):
        score += 0.25

    # 2b. Strong intent alignment boost (reward, not just penalize)
    if required.intersection(record_types):
        score += 0.4

    # 3. Remote requirement
    if intent["remote_required"] == "Yes" and record["remote_support"] != "Yes":
        score -= 0.4

    # 4. Adaptive requirement
    if intent["adaptive_required"] == "Yes" and record["adaptive_support"] != "Yes":
        score -= 0.3

    # 5. Time constraint
    max_time = intent["time_constraint_minutes"]
    duration = record["duration_minutes"]

    if max_time and isinstance(duration, int) and duration > max_time:
        score -= 0.2

    if max_time and isinstance(duration, int) and duration <= max_time:
        score += 0.15

    # 6. Experience level match
    exp = intent["experience_level"]
    job_levels = record.get("job_levels")

    if not isinstance(job_levels, (list, set)):
        job_levels = []

    if exp and exp not in job_levels:
        score -= 0.3

    if exp and exp in job_levels:
        score += 0.2
    return score

def enforce_required_types(results, required_types, k=10):
    """
    Ensure at least one assessment per required test type (e.g., K, P, A)
    when the query spans multiple domains.
    """
    final = []
    covered_types = set()

    # 1. First pass: pick the best item for each required test type
    for req_type in required_types:
        for score, r in results:
            if req_type in (r.get("test_type") or []):
                final.append((score, r))
                covered_types.add(req_type)
                break

    # 2. Second pass: fill remaining slots by score
    for score, r in results:
        if len(final) >= k:
            break
        if r not in [x[1] for x in final]:
            final.append((score, r))

    return final

from processing.intent_extraction import extract_intent
from embedding.index import search

def recommend_assessments(query: str, top_k: int = 10):
    # 1. Extract intent using LLM
    intent = extract_intent(query)

    # 2. Retrieve high-recall semantic candidates
    scored_results = search(query, top_k=25)
    # expected format: [(semantic_score, record), ...]

    # 3. Adjust scores using intent
    reranked = []
    for base_score, record in scored_results:
        final_score = adjust_score(base_score, record, intent)
        reranked.append((final_score, record))

    # 4. Sort by final score (descending)
    reranked.sort(key=lambda x: x[0], reverse=True)

    # 5. Enforce required test type coverage
    required_types = set(intent["required_test_types"])
    if required_types:
        reranked = enforce_required_types(reranked, required_types, k=top_k)

    # 6. Return top-k records only
    return [record for _, record in reranked[:top_k]]