from fastapi import FastAPI, HTTPException
from api.schemas import RecommendRequest, RecommendResponse, RecommendedAssessment
from service.recommendation_service import recommend_assessments

app = FastAPI(
    title="SHL Assessment Recommendation API",
    version="1.0.0"
)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/recommend", response_model=RecommendResponse)
def recommend(req: RecommendRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    results = recommend_assessments(req.query, top_k=req.top_k)

    formatted = [
        RecommendedAssessment(
            url=r["url"],
            adaptive_support=r["adaptive_support"],
            description=r["description"],
            duration=int(r["duration_minutes"]) if r.get("duration_minutes") == r.get("duration_minutes") else 0,
            remote_support=r["remote_support"],
            test_type=(
                r["test_type"]
                if isinstance(r.get("test_type"), list)
                else [t.strip().strip("'\"") for t in str(r.get("test_type")).strip("[]").split(",") if t.strip()]
            ),
        )
        for r in results
    ]

    return RecommendResponse(recommended_assessments=formatted)