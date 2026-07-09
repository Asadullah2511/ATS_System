from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from enum import Enum


class MatchLevel(str, Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class SkillMatch(BaseModel):
    skill: str
    required: bool
    candidate_has: bool
    years_experience: Optional[float] = None
    match_score: float


class MatchScore(BaseModel):
    overall_score: float = Field(..., ge=0, le=100)
    skills_score: float = Field(..., ge=0, le=100)
    experience_score: float = Field(..., ge=0, le=100)
    education_score: float = Field(..., ge=0, le=100)
    match_level: MatchLevel
    skill_matches: List[SkillMatch] = Field(default_factory=list)
    missing_required_skills: List[str] = Field(default_factory=list)
    additional_skills: List[str] = Field(default_factory=list)


class EvaluationResult(BaseModel):
    candidate_name: str
    candidate_email: str
    job_id: str
    job_title: str
    match_score: MatchScore
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    recommendation: str
    detailed_analysis: str
    next_steps: List[str] = Field(default_factory=list)
    metadata: Dict[str, str] = Field(default_factory=dict)
