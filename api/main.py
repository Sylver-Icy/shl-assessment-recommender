from fastapi import FastAPI, HTTPException
from api.schemas import RecommendRequest, RecommendResponse, Assessment
from embedding.index import search

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

    results = search(req.query, top_k=req.top_k)

    formatted = [
        Assessment(
            name=r["name"],
            url=r["url"],
            score=float(score)
        )
        for score, r in results
    ]

    return RecommendResponse(results=formatted)