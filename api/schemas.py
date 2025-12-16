from pydantic import BaseModel
from typing import List


class RecommendRequest(BaseModel):
    query: str
    top_k: int = 10


class Assessment(BaseModel):
    name: str
    url: str
    score: float


class RecommendResponse(BaseModel):
    results: List[Assessment]