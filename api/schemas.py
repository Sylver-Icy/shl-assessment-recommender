from pydantic import BaseModel
from typing import List


class RecommendRequest(BaseModel):
    query: str
    top_k: int = 10


class RecommendedAssessment(BaseModel):
    url: str
    adaptive_support: str  # "Yes" / "No"
    description: str
    duration: int
    remote_support: str  # "Yes" / "No"
    test_type: List[str]


class RecommendResponse(BaseModel):
    recommended_assessments: List[RecommendedAssessment]