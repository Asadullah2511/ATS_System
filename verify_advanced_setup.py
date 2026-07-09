"""
Verify that the Advanced ATS System is properly set up.
Checks all advanced features and database connectivity.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))


def check_advanced_packages():
    print("\nChecking advanced packages...")
    required_packages = {
        "gqlalchemy": "Memgraph connectivity",
        "neo4j": "Graph database driver",
        "beautifulsoup4": "Web scraping",
        "sklearn": "Machine learning",
        "textblob": "NLP processing"
    }

    missing = []
    for package, purpose in required_packages.items():
        try:
            __import__(package)
            print(f"[OK] {package:20s} - {purpose}")
        except ImportError:
            print(f"[FAIL] {package:20s} - MISSING")
            missing.append(package)

    return len(missing) == 0


def check_advanced_agents():
    print("\nChecking advanced agents...")
    agents = [
        ("requirement_classifier", "RequirementClassifierAgent"),
        ("evidence_matcher", "EvidenceMatcherAgent"),
        ("gap_analyzer", "GapAnalyzerAgent"),
        ("bias_auditor", "BiasAuditorAgent"),
        ("human_review_handler", "HumanReviewHandler"),
    ]

    all_ok = True
    for module, class_name in agents:
        try:
            mod = __import__(f"src.agents.{module}", fromlist=[class_name])
            cls = getattr(mod, class_name)
            print(f"[OK] {class_name}")
        except Exception as e:
            print(f"[FAIL] {class_name} - {str(e)}")
            all_ok = False

    return all_ok


def check_advanced_graph():
    print("\nChecking advanced graph...")
    try:
        from src.graphs.advanced_ats_graph import create_advanced_ats_graph, AdvancedATSState
        print("[OK] Advanced ATS Graph imported")

        print("[INFO] Graph structure:")
        print("  - 11 workflow nodes")
        print("  - 2 conditional edges (gap analysis, human review)")
        print("  - Memgraph integration")
        print("  - Extended state with bias audit and human review")

        return True
    except Exception as e:
        print(f"[FAIL] Advanced graph import failed: {e}")
        return False


def check_memgraph_config():
    print("\nChecking Memgraph configuration...")
    import os
    from dotenv import load_dotenv

    load_dotenv()

    memgraph_host = os.getenv("MEMGRAPH_HOST", "localhost")
    memgraph_port = os.getenv("MEMGRAPH_PORT", "7687")
    memgraph_password = os.getenv("MEMGRAPH_PASSWORD")

    print(f"[INFO] Host: {memgraph_host}")
    print(f"[INFO] Port: {memgraph_port}")
    print(f"[INFO] Password: {'[SET]' if memgraph_password else '[NOT SET]'}")

    if not memgraph_password:
        print("[WARN] MEMGRAPH_PASSWORD not set in .env")
        print("       Expected: AsadMemgraph12345")
        return False

    return True


def check_memgraph_connection():
    print("\nChecking Memgraph connection...")
    import os
    from dotenv import load_dotenv

    load_dotenv()

    try:
        from src.utils.memgraph_connector import MemgraphConnector

        password = os.getenv("MEMGRAPH_PASSWORD", "AsadMemgraph12345")

        print(f"[INFO] Attempting connection to localhost:7687...")
        db = MemgraphConnector(
            host="localhost",
            port=7687,
            username="",
            password=password
        )

        print("[OK] Connected to Memgraph!")

        print("[INFO] Creating indexes...")
        db.create_indexes()
        print("[OK] Indexes created")

        db.close()
        return True

    except Exception as e:
        print(f"[FAIL] Memgraph connection failed: {e}")
        print("\n[HELP] Make sure Memgraph is running:")
        print("       docker run -p 7687:7687 -p 7444:7444 \\")
        print("         -e MEMGRAPH_PASSWORD=AsadMemgraph12345 \\")
        print("         memgraph/memgraph-platform")
        return False


def check_advanced_models():
    print("\nChecking advanced models...")
    models = [
        ("requirement", "Requirement, RequirementType, Evidence, GapAnalysis"),
        ("bias", "BiasType, BiasFlag, BiasAuditResult, FeedbackRecord"),
    ]

    all_ok = True
    for module, classes in models:
        try:
            mod = __import__(f"src.models.{module}", fromlist=["*"])
            print(f"[OK] {module}.py - {classes}")
        except Exception as e:
            print(f"[FAIL] {module}.py - {str(e)}")
            all_ok = False

    return all_ok


def check_advanced_files():
    print("\nChecking advanced files...")
    files = [
        "advanced_example.py",
        "ADVANCED_FEATURES.md",
        "ADVANCED_SUMMARY.md",
        "visualize_advanced_graph.py",
    ]

    all_ok = True
    for file_path in files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} - MISSING")
            all_ok = False

    return all_ok


def print_feature_summary():
    print("\n" + "="*80)
    print("ADVANCED FEATURES SUMMARY")
    print("="*80)

    features = [
        ("Requirement Classifier", "Detects disguised/inflated requirements"),
        ("Evidence Matcher", "Semantic matching (not just keywords)"),
        ("Gap Analyzer", "Contextual gap analysis with explanations"),
        ("Bias Auditor", "Self-audits for discrimination proxies"),
        ("Human-in-Loop", "Smart routing for borderline cases"),
        ("Feedback Loop", "Tracks disagreements, analyzes drift"),
    ]

    print("\nAdvanced Features:")
    for i, (feature, description) in enumerate(features, 1):
        print(f"  {i}. {feature:25s} - {description}")

    print("\nDatabase:")
    print("  - Memgraph graph database")
    print("  - 7 node types (Candidate, Job, Requirement, etc.)")
    print("  - 7 relationship types")
    print("  - Analytics queries (drift, bias patterns)")

    print("\nWorkflow:")
    print("  - 11 nodes (vs 7 in basic version)")
    print("  - 2 conditional routing points")
    print("  - Extended state with bias audit")

    print("\nKey Differentiator:")
    print("  >> Model audits its OWN reasoning for bias <<")
    print("  This is extremely rare in production ATS systems!")

    print("\n" + "="*80)


def main():
    print("="*80)
    print("ADVANCED ATS SYSTEM - SETUP VERIFICATION")
    print("="*80)

    checks = {
        "Advanced Packages": check_advanced_packages(),
        "Advanced Agents": check_advanced_agents(),
        "Advanced Graph": check_advanced_graph(),
        "Advanced Models": check_advanced_models(),
        "Memgraph Config": check_memgraph_config(),
        "Memgraph Connection": check_memgraph_connection(),
        "Advanced Files": check_advanced_files(),
    }

    print("\n" + "="*80)
    print("VERIFICATION SUMMARY")
    print("="*80)

    all_passed = True
    for check_name, result in checks.items():
        status = "[OK] PASS" if result else "[FAIL] FAIL"
        print(f"{check_name:.<40} {status}")
        if not result:
            all_passed = False

    print("="*80)

    if all_passed:
        print("\n[SUCCESS] Advanced ATS system is fully set up!")
        print_feature_summary()

        print("\nNext steps:")
        print("  1. Visualize workflow: python visualize_advanced_graph.py")
        print("  2. Run advanced example: python advanced_example.py")
        print("  3. Read documentation: ADVANCED_FEATURES.md")
        print()

    else:
        print("\n[INCOMPLETE] Some checks failed.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Start Memgraph: docker run -p 7687:7687 memgraph/memgraph-platform")
        print("  - Set password in .env: MEMGRAPH_PASSWORD=AsadMemgraph12345")
        print()

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
