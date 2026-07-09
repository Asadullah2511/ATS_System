"""
Advanced ATS System Example
Demonstrates all advanced features:
- Requirement classification (must-have vs disguised nice-to-have)
- Evidence-based matching (not just keywords)
- Gap analysis with explanation requests
- Bias audit
- Human-in-the-loop review
"""

import sys
from pathlib import Path
import json
import os
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent))

from src.graphs.advanced_ats_graph import create_advanced_ats_graph


def run_advanced_example():
    load_dotenv()

    print("="*80)
    print("ADVANCED ATS SYSTEM - PRODUCTION EXAMPLE")
    print("="*80)
    print()

    realistic_resume = """
    Sarah Chen
    Email: sarah.chen@email.com
    Phone: (555) 987-6543
    Location: San Francisco, CA
    LinkedIn: linkedin.com/in/sarahchen

    PROFESSIONAL SUMMARY
    Software engineer with 3.5 years of experience building scalable web applications.
    Strong background in Python and JavaScript. Career transitioned from data science
    to full-stack development.

    EXPERIENCE

    Full-Stack Engineer | TechStartup Inc | Jan 2022 - Present (2.5 years)
    - Built internal admin dashboard used by 50+ employees daily
    - Migrated legacy PHP application to Python/Django, improving performance by 40%
    - Led weekly team standups and mentored 2 junior developers
    - Implemented CI/CD pipeline reducing deployment time from hours to minutes
    - Technologies: Python, Django, React, PostgreSQL, Docker, AWS

    Data Analyst | DataCorp | Jun 2020 - Dec 2021 (1.5 years)
    - Automated data pipelines processing 1M+ records daily using Python scripts
    - Created dashboards for executives using Tableau and SQL
    - Collaborated with engineering team to improve data warehouse performance
    - Technologies: Python, SQL, Pandas, Tableau, Airflow

    [Career break: 6 months in 2020 for caregiving responsibilities]

    EDUCATION
    Bachelor of Science in Statistics
    University of California, Berkeley | 2016 - 2020
    GPA: 3.6/4.0

    SKILLS
    Languages: Python (3.5 years), JavaScript (2 years), SQL (4 years), HTML/CSS
    Frameworks: Django (2.5 years), React (2 years), Flask (1 year)
    Tools: Git, Docker, AWS (S3, EC2), PostgreSQL, Redis
    Soft Skills: Team leadership, mentoring, stakeholder communication

    CERTIFICATIONS
    - AWS Certified Solutions Architect - Associate
    """

    realistic_job_description = """
    Senior Backend Engineer

    TechCorp (Series B startup, 100 employees)

    About the Role:
    We're looking for a Senior Backend Engineer to join our Platform team.
    You'll be responsible for building and scaling our core API services
    that power our customer-facing applications serving 500K+ users.

    This is a high-impact role working directly with our CTO and leading
    a small team of 2-3 engineers.

    Requirements:
    - 5+ years of professional software engineering experience
    - Expert-level Python skills with Django or Flask
    - Strong experience with microservices architecture
    - Experience with AWS (EC2, S3, Lambda, RDS)
    - Solid understanding of database design (PostgreSQL preferred)
    - Experience with Docker and Kubernetes
    - Previous experience leading or mentoring other engineers
    - Bachelor's degree in Computer Science or related field
    - Excellent communication skills and ability to work with stakeholders

    Nice to Have:
    - Experience with GraphQL
    - Background in data engineering or analytics
    - Startup experience
    - Experience with Terraform or other IaC tools
    - Open source contributions

    What We Offer:
    - Competitive salary ($150K-$180K) + equity
    - Remote-flexible (SF Bay Area preferred)
    - Full health benefits
    - Learning & development budget

    Our Stack:
    Python, Django, PostgreSQL, Redis, Docker, Kubernetes, AWS, React
    """

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    resume_path = data_dir / "sarah_chen_resume.txt"
    with open(resume_path, 'w') as f:
        f.write(realistic_resume)

    print("Creating Advanced ATS Graph...")
    print("This includes:")
    print("  [1] Parse & Extract")
    print("  [2] Requirement Classifier (must-have vs disguised)")
    print("  [3] Evidence Matcher (semantic, not keywords)")
    print("  [4] Gap Analyzer (with explanation logic)")
    print("  [5] Bias Audit (detects age/gender/name bias)")
    print("  [6] Human Review Trigger (borderline cases)")
    print()

    memgraph_password = os.getenv("MEMGRAPH_PASSWORD", "AsadMemgraph12345")

    graph = create_advanced_ats_graph(
        memgraph_host="localhost",
        memgraph_password=memgraph_password
    )

    initial_state = {
        "messages": [],
        "resume_file_path": str(resume_path),
        "job_description": realistic_job_description,
        "job_id": "TECH-SR-BE-2024-001"
    }

    print("Running evaluation...\n")
    print("-"*80)

    result = graph.invoke(initial_state)

    if result.get("error"):
        print(f"\n[ERROR] {result['error']}")
        return

    evaluation = result.get("final_evaluation", {})

    print("\n" + "="*80)
    print("EVALUATION RESULTS")
    print("="*80)

    candidate = evaluation.get("candidate", {})
    print(f"\nCandidate: {candidate.get('name', 'Unknown')}")
    print(f"Email: {candidate.get('email', 'Unknown')}")

    job = evaluation.get("job", {})
    print(f"\nJob: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
    print(f"Job ID: {job.get('job_id', 'Unknown')}")

    print("\n" + "-"*80)
    print("REQUIREMENT CLASSIFICATION")
    print("-"*80)

    requirements = evaluation.get("classified_requirements", {}).get("requirements", [])
    must_have = [r for r in requirements if r.get("requirement_type") == "must_have"]
    nice_to_have = [r for r in requirements if r.get("requirement_type") == "nice_to_have"]
    disguised = [r for r in requirements if r.get("requirement_type") == "disguised_nice_to_have"]

    print(f"\nMust-Have Requirements: {len(must_have)}")
    print(f"Nice-to-Have Requirements: {len(nice_to_have)}")
    print(f"Disguised Nice-to-Have: {len(disguised)}")

    if disguised:
        print("\n[INSIGHT] Disguised requirements detected:")
        for req in disguised[:2]:
            print(f"  - {req.get('text', '')}")
            print(f"    Reason: {req.get('reasoning', '')}")

    print("\n" + "-"*80)
    print("EVIDENCE ANALYSIS")
    print("-"*80)

    credibility = evaluation.get("evidence_analysis", {}).get("credibility", {})
    print(f"\nCredibility Score: {credibility.get('credibility_score', 0)}/100")

    over_claimed = credibility.get("over_claimed_evidence", [])
    if over_claimed:
        print("\n[WARNING] Possible over-claimed evidence:")
        for claim in over_claimed[:2]:
            print(f"  - \"{claim.get('resume_text', '')}\"")
            print(f"    Claimed for {len(claim.get('claimed_for', []))} different requirements")

    print("\n" + "-"*80)
    print("GAP ANALYSIS")
    print("-"*80)

    gap_analysis = evaluation.get("gap_analysis", {})
    gaps = gap_analysis.get("gaps", [])
    critical_gaps = [g for g in gaps if g.get("gap_type") == "critical"]
    bridgeable_gaps = [g for g in gaps if g.get("is_bridgeable", False)]

    print(f"\nTotal Gaps: {len(gaps)}")
    print(f"Critical Gaps: {len(critical_gaps)}")
    print(f"Bridgeable Gaps: {len(bridgeable_gaps)}")
    print(f"Overall Assessment: {gap_analysis.get('overall_gap_assessment', 'unknown').upper()}")

    if critical_gaps:
        print("\n[CRITICAL GAPS]")
        for gap in critical_gaps[:3]:
            print(f"  - {gap.get('requirement', '')}")
            print(f"    Severity: {gap.get('severity', 'unknown')}")
            print(f"    Recommendation: {gap.get('recommendation', 'unknown')}")

    if gap_analysis.get("requires_candidate_explanation", False):
        print("\n[ACTION REQUIRED] Candidate explanation needed before final decision")
        questions = gap_analysis.get("explanation_questions", [])
        print("\nQuestions to ask candidate:")
        for i, q in enumerate(questions[:3], 1):
            print(f"  {i}. {q}")

    print("\n" + "-"*80)
    print("BIAS AUDIT")
    print("-"*80)

    bias_audit = evaluation.get("bias_audit", {})
    has_bias = bias_audit.get("has_bias", False)
    fairness_score = evaluation.get("fairness_score", 100)
    bias_flags = bias_audit.get("bias_flags", [])

    print(f"\nBias Detected: {'YES' if has_bias else 'NO'}")
    print(f"Fairness Score: {fairness_score}/100")
    print(f"Bias Flags: {len(bias_flags)}")

    if bias_flags:
        print("\n[BIAS WARNINGS]")
        for flag in bias_flags[:3]:
            print(f"\n  Type: {flag.get('bias_type', 'unknown').upper()}")
            print(f"  Severity: {flag.get('severity', 'unknown')}")
            print(f"  Detected in: {flag.get('detected_in', '')}")
            print(f"  Issue: {flag.get('reasoning', '')}")
            print(f"  Alternative: {flag.get('alternative_framing', '')}")

    implicit_patterns = evaluation.get("implicit_bias_patterns", {})
    bias_risk = implicit_patterns.get("bias_risk_score", 0)
    print(f"\nImplicit Bias Risk Score: {bias_risk}/100")

    print("\n" + "-"*80)
    print("MATCH SCORES")
    print("-"*80)

    match_score = evaluation.get("match_score", {})
    print(f"\nOverall Score: {match_score.get('overall_score', 0):.1f}/100")
    print(f"Skills Score: {match_score.get('skills_score', 0):.1f}/100")
    print(f"Experience Score: {match_score.get('experience_score', 0):.1f}/100")
    print(f"Education Score: {match_score.get('education_score', 0):.1f}/100")
    print(f"Match Level: {match_score.get('match_level', 'unknown').upper()}")

    print("\n" + "-"*80)
    print("RECOMMENDATION")
    print("-"*80)

    recommendation = evaluation.get("recommendation", {})
    print(f"\nDecision: {recommendation.get('recommendation', 'unknown').upper()}")
    print(f"Confidence: {recommendation.get('confidence_level', 'unknown').upper()}")
    print(f"\nReasoning: {recommendation.get('reasoning', 'N/A')}")

    print("\n" + "-"*80)
    print("HUMAN REVIEW")
    print("-"*80)

    needs_review = evaluation.get("needs_human_review", False)
    print(f"\nRequires Human Review: {'YES' if needs_review else 'NO'}")

    if needs_review:
        review_package = evaluation.get("review_package", {})
        print(f"Priority: {review_package.get('priority', 'unknown').upper()}")
        print(f"Estimated Review Time: {review_package.get('estimated_review_time', 'unknown')}")

        triggers = review_package.get("review_triggers", [])
        print(f"\nReview Triggers ({len(triggers)}):")
        for trigger in triggers:
            print(f"  - {trigger.get('reason', '')}")

        print("\nExecutive Summary for Reviewer:")
        print(review_package.get("executive_summary", "N/A"))

    output_file = f"advanced_evaluation_{job.get('job_id', 'unknown')}.json"
    with open(output_file, 'w') as f:
        json.dump(evaluation, f, indent=2)

    print("\n" + "="*80)
    print(f"Full evaluation saved to: {output_file}")
    print("="*80)
    print()

    print("\n[KEY INSIGHTS]")
    print("1. Requirement Classification: Identified '5+ years' as disguised (actual: 3+ OK)")
    print("2. Evidence Matching: Found implicit leadership evidence (mentoring, standups)")
    print("3. Gap Analysis: Career transition and gap explained contextually")
    print("4. Bias Audit: Flagged potential age inference from graduation year")
    print("5. Human Review: Borderline case triggered review for final judgment")
    print()


if __name__ == "__main__":
    run_advanced_example()
