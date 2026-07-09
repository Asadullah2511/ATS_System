from typing import List, Optional
from pydantic import BaseModel, Field


class JobRequirement(BaseModel):
    category: str
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    min_years_experience: Optional[int] = None
    education_level: Optional[str] = None


class JobPosting(BaseModel):
    job_id: str
    title: str
    company: str
    location: Optional[str] = None
    job_type: Optional[str] = None
    description: str
    requirements: JobRequirement
    responsibilities: List[str] = Field(default_factory=list)
    salary_range: Optional[str] = None
    benefits: List[str] = Field(default_factory=list)
    raw_text: str
