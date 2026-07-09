"""
Verification script to check if the ATS system is properly set up.
Run this after installation to ensure everything is configured correctly.
"""

import sys
from pathlib import Path

def check_python_version():
    print("Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"[OK] Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"[FAIL] Python {version.major}.{version.minor} - FAILED (requires 3.9+)")
        return False


def check_packages():
    print("\nChecking required packages...")
    required_packages = [
        "langgraph",
        "langchain",
        "langchain_openai",
        "langchain_anthropic",
        "fastapi",
        "uvicorn",
        "pydantic",
        "pypdf",
        "docx",
        "pytest"
    ]

    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package} - installed")
        except ImportError:
            print(f"[FAIL] {package} - MISSING")
            missing.append(package)

    return len(missing) == 0


def check_env_file():
    print("\nChecking environment configuration...")
    env_file = Path(".env")

    if not env_file.exists():
        print("[FAIL] .env file not found")
        print("   Create it from .env.example: cp .env.example .env")
        return False

    print("[OK] .env file exists")

    with open(env_file, 'r') as f:
        content = f.read()

    if "OPENAI_API_KEY=your_" in content or "OPENAI_API_KEY=" not in content:
        print("[WARN]  WARNING: OPENAI_API_KEY not configured in .env")
        print("   The system requires a valid OpenAI API key to function")
        return False

    print("[OK] OPENAI_API_KEY appears to be configured")
    return True


def check_directory_structure():
    print("\nChecking directory structure...")
    required_dirs = [
        "src",
        "src/agents",
        "src/graphs",
        "src/tools",
        "src/models",
        "src/api",
        "src/utils",
        "tests",
        "data",
        "data/resumes",
        "data/job_descriptions"
    ]

    all_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"[OK] {dir_path}/")
        else:
            print(f"[FAIL] {dir_path}/ - MISSING")
            all_ok = False

    return all_ok


def check_key_files():
    print("\nChecking key files...")
    required_files = [
        "main.py",
        "example.py",
        "requirements.txt",
        "src/graphs/ats_graph.py",
        "src/agents/resume_agent.py",
        "src/agents/job_agent.py",
        "src/agents/matching_agent.py",
        "src/agents/recommendation_agent.py",
        "src/api/main.py"
    ]

    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"[OK] {file_path}")
        else:
            print(f"[FAIL] {file_path} - MISSING")
            all_ok = False

    return all_ok


def test_imports():
    print("\nTesting critical imports...")

    try:
        from src.graphs.ats_graph import create_ats_graph
        print("[OK] Can import create_ats_graph")
    except Exception as e:
        print(f"[FAIL] Failed to import create_ats_graph: {e}")
        return False

    try:
        from src.agents.resume_agent import ResumeAnalysisAgent
        print("[OK] Can import ResumeAnalysisAgent")
    except Exception as e:
        print(f"[FAIL] Failed to import ResumeAnalysisAgent: {e}")
        return False

    try:
        from src.api.main import app
        print("[OK] Can import FastAPI app")
    except Exception as e:
        print(f"[FAIL] Failed to import FastAPI app: {e}")
        return False

    return True


def main():
    print("="*80)
    print("ATS SYSTEM - SETUP VERIFICATION")
    print("="*80)
    print()

    checks = {
        "Python Version": check_python_version(),
        "Required Packages": check_packages(),
        "Environment Configuration": check_env_file(),
        "Directory Structure": check_directory_structure(),
        "Key Files": check_key_files(),
        "Import Test": test_imports()
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
        print("\nSUCCESS! SUCCESS! Your ATS system is properly set up and ready to use.")
        print("\nNext steps:")
        print("  1. Run the example: python example.py")
        print("  2. Try the CLI: python main.py")
        print("  3. Start the API: python src/api/main.py")
        print("\nFor detailed usage, see QUICKSTART.md")
    else:
        print("\n[WARN]  SETUP INCOMPLETE - Please fix the failed checks above.")
        print("\nCommon fixes:")
        print("  - Install packages: pip install -r requirements.txt")
        print("  - Create .env: cp .env.example .env")
        print("  - Add API key to .env file")
        print("\nFor help, see README.md or QUICKSTART.md")

    print()
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
