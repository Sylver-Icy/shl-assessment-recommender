from fastapi import FastAPI, HTTPException
from api.schemas import RecommendRequest, RecommendResponse, RecommendedAssessment
from service.recommendation_service import recommend_assessments

app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Default top_k to 10 if not provided in request
    top_k = req.top_k if req.top_k is not None else 10
    results = recommend_assessments(req.query, top_k=top_k)

    formatted = []

    for r in results:
        # ---- duration normalization ----
        raw_duration = r.get("duration_minutes")

        if isinstance(raw_duration, int):
            duration = raw_duration
        elif isinstance(raw_duration, str) and raw_duration.isdigit():
            duration = int(raw_duration)
        else:
            duration = 0
        # -------------------------------------------

        # ---- test type normalization ----
        if isinstance(r.get("expanded_test_type"), list):
            test_type = r["expanded_test_type"]
        else:
            test_type = [
                t.strip().strip("'\"")
                for t in str(r.get("expanded_test_type", ""))
                .strip("[]")
                .split(",")
                if t.strip()
            ]
        # --------------------------------

        formatted.append(
            RecommendedAssessment(
                url=r["url"],
                name=r["name"],
                adaptive_support=r["adaptive_support"],
                description=r["description"],
                duration=duration,
                remote_support=r["remote_support"],
                test_type=test_type,
            )
        )

    return RecommendResponse(recommended_assessments=formatted)