from typing import List, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class BiasType(str, Enum):
    AGE = "age"
    GENDER = "gender"
    NAME = "name"
    EDUCATION_PRESTIGE = "education_prestige"
    EMPLOYMENT_GAP = "employment_gap"
    CAREER_PATH = "career_path"
    LOCATION = "location"
    OTHER = "other"


class BiasFlag(BaseModel):
    bias_type: BiasType
    detected_in: str
    problematic_text: str
    reasoning: str
    severity: str
    alternative_framing: str
    confidence: float = Field(..., ge=0, le=100)


class BiasAuditResult(BaseModel):
    has_bias: bool
    flags: List[BiasFlag] = Field(default_factory=list)
    overall_fairness_score: float = Field(..., ge=0, le=100)
    recommendations: List[str] = Field(default_factory=list)
    protected_attributes_detected: List[str] = Field(default_factory=list)


class FeedbackRecord(BaseModel):
    evaluation_id: str
    candidate_name: str
    job_id: str
    model_recommendation: str
    model_confidence: float
    human_decision: str
    human_reasoning: Optional[str] = None
    disagreement: bool
    disagreement_type: Optional[str] = None
    timestamp: str
    metadata: Dict = Field(default_factory=dict)
