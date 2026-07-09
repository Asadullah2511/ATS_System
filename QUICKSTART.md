# ATS System - Quick Start Guide

Get your ATS system up and running in 5 minutes!

## Prerequisites

- Python 3.9 or higher
- OpenAI API key (required)
- Git (optional, for cloning)

## Installation

### 1. Clone or Download the Project

```bash
git clone <your-repo-url>
cd ATS_System
```

Or download and extract the ZIP file.

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all required packages including:
- LangGraph for workflow orchestration
- LangChain for LLM interactions
- FastAPI for the REST API
- And all other dependencies

### 4. Configure Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
```

**Important:** You MUST have an OpenAI API key for the system to work!

Get one at: https://platform.openai.com/api-keys

## Quick Test

### Option 1: Run the Example Script

```bash
python example.py
```

This will:
- Create a sample resume and job description
- Run the full ATS evaluation
- Save results to `example_evaluation.json`

**Expected output:**
```
Running ATS System Example...
Creating ATS Graph...
Running evaluation...

================================================================================
EVALUATION RESULTS
================================================================================

Overall Match Score: 87.5/100
Match Level: GOOD

Recommendation: YES
Confidence: high

Full evaluation saved to: example_evaluation.json
================================================================================
```

### Option 2: Interactive CLI

```bash
python main.py
```

Follow the prompts:
1. Enter path to a resume file (PDF, DOCX, or TXT)
2. Enter job description or path to job description file
3. Enter a job ID

The system will generate a comprehensive evaluation report.

### Option 3: REST API

Start the API server:

```bash
python src/api/main.py
```

Or:

```bash
uvicorn src.api.main:app --reload --port 8000
```

**Test the API:**

Open http://localhost:8000 in your browser to see API info.

**Health check:**
```bash
curl http://localhost:8000/health
```

**Evaluate a candidate:**
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -F "resume=@path/to/resume.pdf" \
  -F "job_description=Your job description here..." \
  -F "job_id=JOB-001"
```

## Usage Examples

### Example 1: Evaluate a Single Candidate

```python
from src.graphs.ats_graph import create_ats_graph

graph = create_ats_graph()

state = {
    "messages": [],
    "resume_file_path": "path/to/resume.pdf",
    "job_description": "Your job description text...",
    "job_id": "JOB-2024-001"
}

result = graph.invoke(state)
evaluation = result["final_evaluation"]

print(f"Match Score: {evaluation['scores']['overall_score']}")
print(f"Recommendation: {evaluation['recommendation']['recommendation']}")
```

### Example 2: Batch Evaluation via API

```python
import requests

files = [
    ("resumes", open("candidate1.pdf", "rb")),
    ("resumes", open("candidate2.pdf", "rb")),
    ("resumes", open("candidate3.pdf", "rb"))
]

data = {
    "job_description": "Senior Python Developer...",
    "job_id": "JOB-001"
}

response = requests.post(
    "http://localhost:8000/batch-evaluate",
    files=files,
    data=data
)

results = response.json()
print(f"Evaluated {results['successful']} candidates")
print("Top candidate:", results['ranked_candidates'][0]['filename'])
```

### Example 3: Custom Evaluation Pipeline

```python
from src.agents.resume_agent import ResumeAnalysisAgent
from src.agents.matching_agent import MatchingAgent
from src.tools.resume_parser import ResumeParserTool

parser = ResumeParserTool()
resume_agent = ResumeAnalysisAgent()
matching_agent = MatchingAgent()

parsed_resume = parser._run("resume.pdf")
analysis = resume_agent.analyze_resume(parsed_resume)

print("Candidate Strengths:")
for strength in analysis.get("strengths", []):
    print(f"  - {strength}")
```

## Troubleshooting

### Issue: ImportError or Module Not Found

**Solution:** Make sure you're in the virtual environment and all packages are installed:

```bash
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### Issue: OpenAI API Error

**Solution:** Check that:
1. Your `.env` file exists and contains `OPENAI_API_KEY`
2. The API key is valid and has credits
3. You have internet connection

### Issue: File Parsing Errors

**Solution:** 
- For PDFs: Ensure the PDF is text-based, not scanned images
- For DOCX: Use modern .docx format, not old .doc format
- For TXT: Use UTF-8 encoding

### Issue: Slow Performance

**Solution:**
- First run downloads model info and may be slower
- Resume parsing for large files takes 10-30 seconds
- Consider using `gpt-4o-mini` instead of `gpt-4` for faster responses

## Project Structure Overview

```
ATS_System/
├── src/
│   ├── agents/          # AI agents (Resume, Job, Matching, Recommendation)
│   ├── graphs/          # LangGraph workflow definitions
│   ├── tools/           # Parsing tools (Resume, Job, Skills)
│   ├── models/          # Data models (Pydantic schemas)
│   ├── api/             # FastAPI REST API
│   └── utils/           # Utilities (logging, config)
├── tests/               # Test suite
├── data/                # Data directory
├── main.py              # CLI entry point
├── example.py           # Example script
└── requirements.txt     # Python dependencies
```

## Key Components

### 1. Resume Parser
Extracts structured data from resume files (PDF, DOCX, TXT).

### 2. Job Parser
Analyzes job descriptions and extracts requirements.

### 3. Resume Agent
Analyzes candidate qualifications and experience.

### 4. Job Agent
Identifies must-have vs nice-to-have requirements.

### 5. Matching Agent
Calculates match scores across multiple dimensions.

### 6. Recommendation Agent
Generates hire/no-hire recommendations with reasoning.

### 7. LangGraph Workflow
Orchestrates the entire evaluation pipeline.

## Evaluation Output

The system produces:

```json
{
  "candidate": {
    "name": "John Doe",
    "email": "john@example.com"
  },
  "job": {
    "title": "Senior Engineer",
    "company": "Tech Corp"
  },
  "scores": {
    "overall_score": 87.5,
    "skills_score": 90.0,
    "experience_score": 85.0,
    "education_score": 88.0,
    "match_level": "good"
  },
  "recommendation": {
    "recommendation": "yes",
    "confidence_level": "high",
    "reasoning": "...",
    "strengths": [...],
    "weaknesses": [...],
    "next_steps": [...]
  },
  "interview_questions": {
    "technical_questions": [...],
    "behavioral_questions": [...],
    "situational_questions": [...]
  }
}
```

## Next Steps

1. **Try the example:** Run `python example.py`
2. **Test with real resumes:** Use `python main.py` with actual resume files
3. **Explore the API:** Start the API and try the endpoints
4. **Customize:** Modify agents and prompts for your specific needs
5. **Deploy:** Use Docker or deploy to cloud (AWS, Azure, GCP)

## API Documentation

Once the API is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## Performance Tips

1. **Use gpt-4o-mini for faster responses** (modify in agent initialization)
2. **Enable response streaming** for real-time feedback
3. **Batch process multiple resumes** using the batch endpoint
4. **Cache parsed resumes** to avoid re-parsing

## Cost Considerations

- **gpt-4o-mini:** ~$0.02-0.05 per evaluation
- **gpt-4:** ~$0.10-0.30 per evaluation
- Costs depend on resume/job description length

## Security Notes

- Never commit your `.env` file
- Keep API keys secure
- Validate file uploads in production
- Sanitize user inputs
- Use HTTPS in production

## Getting Help

- Check README.md for detailed documentation
- Review example.py for usage patterns
- Check tests/ directory for more examples
- Open an issue on GitHub for bugs

## License

MIT License - Free to use and modify!

---

**You're all set!** Start evaluating candidates with AI-powered insights. 🚀
