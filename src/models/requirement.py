from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class RequirementType(str, Enum):
    MUST_HAVE = "must_have"
    NICE_TO_HAVE = "nice_to_have"
    DISGUISED_NICE_TO_HAVE = "disguised_nice_to_have"


class Requirement(BaseModel):
    text: str
    category: str
    requirement_type: RequirementType
    reasoning: str
    keywords: List[str] = Field(default_factory=list)
    actual_necessity: str
    flexibility_score: float = Field(..., ge=0, le=100)


class Evidence(BaseModel):
    requirement: str
    resume_text: str
    match_type: str
    confidence: float = Field(..., ge=0, le=100)
    reasoning: str
    is_keyword_match: bool
    is_semantic_match: bool


class GapAnalysis(BaseModel):
    requirement: str
    gap_type: str
    severity: str
    explanation: str
    is_bridgeable: bool
    time_to_bridge: Optional[str] = None
    recommendation: str
