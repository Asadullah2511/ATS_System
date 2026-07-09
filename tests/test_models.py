import pytest
from datetime import date
from src.models.resume import Resume, Candidate, Experience, Education, Skill
from src.models.job import JobPosting, JobRequirement
from src.models.evaluation import EvaluationResult, MatchScore, MatchLevel


def test_candidate_model():
    candidate = Candidate(
        name="John Doe",
        email="john@example.com",
        phone="555-1234",
        location="San Francisco, CA"
    )
    assert candidate.name == "John Doe"
    assert candidate.email == "john@example.com"


def test_skill_model():
    skill = Skill(
        name="Python",
        proficiency="Expert",
        years_of_experience=5.0
    )
    assert skill.name == "Python"
    assert skill.years_of_experience == 5.0


def test_experience_model():
    experience = Experience(
        company="Tech Corp",
        title="Senior Engineer",
        start_date=date(2020, 1, 1),
        end_date=date(2024, 1, 1),
        description="Led development team",
        responsibilities=["Coding", "Mentoring"],
        achievements=["Increased efficiency by 50%"]
    )
    assert experience.company == "Tech Corp"
    assert len(experience.responsibilities) == 2


def test_resume_model():
    candidate = Candidate(name="John Doe", email="john@example.com")
    resume = Resume(
        candidate=candidate,
        summary="Experienced engineer",
        experience=[],
        education=[],
        skills=[],
        raw_text="Sample resume text"
    )
    assert resume.candidate.name == "John Doe"
    assert resume.raw_text == "Sample resume text"


def test_job_requirement_model():
    req = JobRequirement(
        category="Backend Engineering",
        required_skills=["Python", "Django"],
        preferred_skills=["Docker", "Kubernetes"],
        min_years_experience=5,
        education_level="Bachelor's degree"
    )
    assert len(req.required_skills) == 2
    assert req.min_years_experience == 5


def test_job_posting_model():
    req = JobRequirement(
        category="Engineering",
        required_skills=["Python"]
    )
    job = JobPosting(
        job_id="JOB-001",
        title="Senior Engineer",
        company="Tech Corp",
        description="Great opportunity",
        requirements=req,
        raw_text="Job posting text"
    )
    assert job.job_id == "JOB-001"
    assert job.title == "Senior Engineer"


def test_match_score_model():
    match_score = MatchScore(
        overall_score=85.5,
        skills_score=90.0,
        experience_score=80.0,
        education_score=85.0,
        match_level=MatchLevel.GOOD,
        skill_matches=[],
        missing_required_skills=["Docker"],
        additional_skills=["React"]
    )
    assert match_score.overall_score == 85.5
    assert match_score.match_level == MatchLevel.GOOD


def test_match_score_validation():
    with pytest.raises(ValueError):
        MatchScore(
            overall_score=150,
            skills_score=90,
            experience_score=80,
            education_score=85,
            match_level=MatchLevel.GOOD
        )
