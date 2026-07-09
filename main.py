import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.graphs.ats_graph import create_ats_graph
from src.utils.logger import setup_logger
from src.utils.config import load_config
import json


def main():
    config = load_config()
    logger = setup_logger("ats_main", "logs/ats.log")

    logger.info("Starting ATS System")

    resume_path = input("Enter resume file path: ")
    job_description = input("Enter job description (or path to file): ")
    job_id = input("Enter job ID: ")

    if Path(job_description).exists():
        with open(job_description, 'r') as f:
            job_description = f.read()

    graph = create_ats_graph()

    initial_state = {
        "messages": [],
        "resume_file_path": resume_path,
        "job_description": job_description,
        "job_id": job_id
    }

    logger.info("Running ATS evaluation...")
    result = graph.invoke(initial_state)

    if result.get("error"):
        logger.error(f"Error: {result['error']}")
        print(f"\nError occurred: {result['error']}")
        return

    evaluation = result.get("final_evaluation", {})

    print("\n" + "="*80)
    print("ATS EVALUATION REPORT")
    print("="*80)

    candidate = evaluation.get("candidate", {})
    print(f"\nCandidate: {candidate.get('name', 'Unknown')}")
    print(f"Email: {candidate.get('email', 'Unknown')}")

    job = evaluation.get("job", {})
    print(f"\nJob: {job.get('title', 'Unknown')} at {job.get('company', 'Unknown')}")
    print(f"Job ID: {job.get('job_id', 'Unknown')}")

    scores = evaluation.get("scores", {})
    print(f"\n--- MATCH SCORES ---")
    print(f"Overall Score: {scores.get('overall_score', 0):.1f}/100")
    print(f"Skills Score: {scores.get('skills_score', 0):.1f}/100")
    print(f"Experience Score: {scores.get('experience_score', 0):.1f}/100")
    print(f"Education Score: {scores.get('education_score', 0):.1f}/100")
    print(f"Match Level: {scores.get('match_level', 'unknown').upper()}")

    recommendation = evaluation.get("recommendation", {})
    print(f"\n--- RECOMMENDATION ---")
    print(f"Decision: {recommendation.get('recommendation', 'unknown').upper()}")
    print(f"Confidence: {recommendation.get('confidence_level', 'unknown').upper()}")
    print(f"\nReasoning: {recommendation.get('reasoning', 'N/A')}")

    strengths = recommendation.get("strengths", [])
    if strengths:
        print(f"\nStrengths:")
        for strength in strengths:
            print(f"  • {strength}")

    weaknesses = recommendation.get("weaknesses", [])
    if weaknesses:
        print(f"\nWeaknesses:")
        for weakness in weaknesses:
            print(f"  • {weakness}")

    next_steps = recommendation.get("next_steps", [])
    if next_steps:
        print(f"\nNext Steps:")
        for step in next_steps:
            print(f"  • {step}")

    output_file = f"evaluation_{job_id}_{candidate.get('name', 'unknown').replace(' ', '_')}.json"
    with open(output_file, 'w') as f:
        json.dump(evaluation, f, indent=2)

    print(f"\n--- Full evaluation saved to: {output_file} ---")
    print("="*80)

    logger.info("ATS evaluation completed successfully")


if __name__ == "__main__":
    main()
