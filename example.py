import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.graphs.ats_graph import create_ats_graph
import json


def run_example():
    print("Running ATS System Example...")
    print("Note: Make sure to set your OpenAI API key in .env file\n")

    sample_resume = """
    John Doe
    Email: john.doe@email.com
    Phone: (555) 123-4567
    LinkedIn: linkedin.com/in/johndoe

    PROFESSIONAL SUMMARY
    Senior Software Engineer with 8+ years of experience in full-stack development,
    specializing in Python, React, and cloud technologies. Proven track record of
    leading teams and delivering scalable solutions.

    EXPERIENCE
    Senior Software Engineer | Tech Corp | 2020 - Present
    - Led development of microservices architecture serving 1M+ users
    - Managed team of 5 engineers
    - Implemented CI/CD pipelines reducing deployment time by 60%
    - Technologies: Python, Django, React, AWS, Docker, Kubernetes

    Software Engineer | StartupXYZ | 2017 - 2020
    - Built RESTful APIs handling 10K requests/second
    - Developed frontend using React and Redux
    - Implemented automated testing achieving 90% coverage
    - Technologies: Python, Flask, React, PostgreSQL, Redis

    EDUCATION
    Bachelor of Science in Computer Science
    University of Technology | 2013 - 2017
    GPA: 3.8/4.0

    SKILLS
    - Languages: Python, JavaScript, TypeScript, SQL
    - Frameworks: Django, Flask, React, Node.js
    - Cloud: AWS (EC2, S3, Lambda, RDS), Docker, Kubernetes
    - Databases: PostgreSQL, MongoDB, Redis
    - Tools: Git, Jenkins, GitHub Actions, Terraform

    CERTIFICATIONS
    - AWS Certified Solutions Architect
    - Certified Kubernetes Administrator (CKA)
    """

    sample_job = """
    Senior Backend Engineer

    About the Role:
    We're looking for a Senior Backend Engineer to join our growing team.
    You'll be responsible for designing and building scalable backend systems
    that power our platform used by millions of users.

    Requirements:
    - 5+ years of experience in backend development
    - Strong proficiency in Python and Django/Flask
    - Experience with microservices architecture
    - Expertise in AWS cloud services
    - Experience with Docker and Kubernetes
    - Strong understanding of database design (PostgreSQL, Redis)
    - Experience leading or mentoring other engineers
    - Bachelor's degree in Computer Science or related field

    Preferred:
    - Experience with event-driven architectures
    - Knowledge of GraphQL
    - Experience with Terraform or other IaC tools
    - AWS certifications

    Responsibilities:
    - Design and implement scalable backend services
    - Lead technical discussions and architecture decisions
    - Mentor junior engineers
    - Optimize system performance and reliability
    - Collaborate with frontend and DevOps teams
    """

    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    resume_path = data_dir / "sample_resume.txt"
    with open(resume_path, 'w') as f:
        f.write(sample_resume)

    print("Creating ATS Graph...")
    graph = create_ats_graph()

    initial_state = {
        "messages": [],
        "resume_file_path": str(resume_path),
        "job_description": sample_job,
        "job_id": "JOB-2024-001"
    }

    print("Running evaluation...\n")
    result = graph.invoke(initial_state)

    if result.get("error"):
        print(f"Error: {result['error']}")
        return

    evaluation = result.get("final_evaluation", {})

    print("="*80)
    print("EVALUATION RESULTS")
    print("="*80)

    scores = evaluation.get("scores", {})
    print(f"\nOverall Match Score: {scores.get('overall_score', 0):.1f}/100")
    print(f"Match Level: {scores.get('match_level', 'unknown').upper()}")

    recommendation = evaluation.get("recommendation", {})
    print(f"\nRecommendation: {recommendation.get('recommendation', 'unknown').upper()}")
    print(f"Confidence: {recommendation.get('confidence_level', 'unknown')}")

    output_file = "example_evaluation.json"
    with open(output_file, 'w') as f:
        json.dump(evaluation, f, indent=2)

    print(f"\nFull evaluation saved to: {output_file}")
    print("="*80)


if __name__ == "__main__":
    run_example()
