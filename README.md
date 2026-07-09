# ATS System - Applicant Tracking System with LangGraph

A sophisticated Applicant Tracking System built with LangGraph, LangChain, and OpenAI that automates the resume screening and candidate evaluation process.

## Features

- **Resume Parsing**: Supports PDF, DOCX, and TXT formats
- **Job Description Analysis**: Extracts requirements and priorities from job postings
- **Intelligent Matching**: Multi-dimensional scoring (skills, experience, education)
- **Gap Analysis**: Identifies missing qualifications and provides recommendations
- **Automated Recommendations**: Hire/No-hire decisions with detailed reasoning
- **Interview Questions**: Generates tailored interview questions based on candidate profile
- **Batch Processing**: Evaluate multiple candidates simultaneously
- **RESTful API**: FastAPI-based API for easy integration
- **LangGraph Workflow**: Structured multi-agent evaluation pipeline

## Architecture

The system uses LangGraph to orchestrate multiple specialized agents:

```
┌─────────────────┐
│  Resume Parser  │
└────────┬────────┘
         │
         v
┌─────────────────┐     ┌──────────────────┐
│  Job Parser     │────▶│  Resume Agent    │
└─────────────────┘     └────────┬─────────┘
         │                       │
         v                       v
┌─────────────────┐     ┌──────────────────┐
│  Job Agent      │────▶│  Matching Agent  │
└─────────────────┘     └────────┬─────────┘
                                 │
                                 v
                        ┌──────────────────┐
                        │ Recommendation   │
                        │     Agent        │
                        └────────┬─────────┘
                                 │
                                 v
                        ┌──────────────────┐
                        │ Final Evaluation │
                        └──────────────────┘
```

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ATS_System
```

2. **Create virtual environment**
```bash
python -m venv venv
```

3. **Activate virtual environment**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

5. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env and add your API keys
```

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

DATABASE_URL=sqlite:///./ats_system.db

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

LOG_LEVEL=INFO
```

## Usage

### Command Line Interface

```bash
python main.py
```

Follow the prompts to:
1. Enter resume file path
2. Enter job description (or path to job description file)
3. Enter job ID

The system will generate a comprehensive evaluation report.

### Example Script

Run the included example with sample data:

```bash
python example.py
```

### REST API

Start the FastAPI server:

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Or:

```bash
python src/api/main.py
```

#### API Endpoints

**Health Check**
```bash
GET /health
```

**Single Evaluation**
```bash
POST /evaluate
Content-Type: multipart/form-data

Parameters:
- resume: file (PDF, DOCX, TXT)
- job_description: string
- job_id: string
```

**Batch Evaluation**
```bash
POST /batch-evaluate
Content-Type: multipart/form-data

Parameters:
- resumes: list of files
- job_description: string
- job_id: string
```

### API Usage Examples

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/evaluate" \
  -F "resume=@path/to/resume.pdf" \
  -F "job_description=Your job description here" \
  -F "job_id=JOB-2024-001"
```

**Using Python:**
```python
import requests

url = "http://localhost:8000/evaluate"
files = {"resume": open("resume.pdf", "rb")}
data = {
    "job_description": "Job description text...",
    "job_id": "JOB-2024-001"
}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## Project Structure

```
ATS_System/
├── src/
│   ├── agents/              # Specialized AI agents
│   │   ├── resume_agent.py
│   │   ├── job_agent.py
│   │   ├── matching_agent.py
│   │   └── recommendation_agent.py
│   ├── graphs/              # LangGraph workflows
│   │   └── ats_graph.py
│   ├── tools/               # Parsing and extraction tools
│   │   ├── resume_parser.py
│   │   ├── job_parser.py
│   │   ├── skill_extractor.py
│   │   └── experience_analyzer.py
│   ├── models/              # Data models
│   │   ├── resume.py
│   │   ├── job.py
│   │   └── evaluation.py
│   ├── api/                 # FastAPI application
│   │   └── main.py
│   └── utils/               # Utilities
│       ├── logger.py
│       └── config.py
├── tests/                   # Test suite
├── data/                    # Data directory
│   ├── resumes/
│   └── job_descriptions/
├── config/                  # Configuration files
├── main.py                  # CLI entry point
├── example.py               # Example usage
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## Evaluation Process

The ATS system follows a structured evaluation pipeline:

1. **Parsing Phase**
   - Extract text from resume (PDF/DOCX/TXT)
   - Parse job description and requirements

2. **Analysis Phase**
   - Resume Agent: Analyzes candidate qualifications
   - Job Agent: Analyzes job requirements and priorities

3. **Matching Phase**
   - Calculate multi-dimensional match scores
   - Identify skill gaps and overlaps

4. **Recommendation Phase**
   - Generate hire/no-hire recommendation
   - Provide detailed reasoning
   - Create tailored interview questions

5. **Compilation Phase**
   - Assemble final evaluation report
   - Include all scores, analyses, and recommendations

## Scoring System

The system provides scores in multiple dimensions:

- **Overall Score** (0-100): Aggregate match score
- **Skills Score** (0-100): Technical and soft skills alignment
- **Experience Score** (0-100): Relevance and level of experience
- **Education Score** (0-100): Educational background match
- **Match Level**: Excellent, Good, Fair, or Poor

## Customization

### Adding New Agents

Create a new agent in `src/agents/`:

```python
from langchain_openai import ChatOpenAI

class MyCustomAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def analyze(self, data):
        # Your agent logic here
        pass
```

### Modifying the Graph

Edit `src/graphs/ats_graph.py` to add nodes or change the workflow:

```python
workflow.add_node("my_custom_node", my_custom_function)
workflow.add_edge("previous_node", "my_custom_node")
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```

Run tests with coverage:

```bash
pytest --cov=src tests/
```

## Performance

- Single evaluation: ~30-60 seconds
- Batch evaluation: Parallel processing for multiple candidates
- API response time: Depends on resume size and complexity

## Limitations

- Requires OpenAI API key (costs apply)
- Resume parsing accuracy depends on format quality
- Best results with well-structured resumes and job descriptions
- English language only (can be extended)

## Roadmap

- [ ] Add support for more LLM providers (Anthropic Claude, Google Gemini)
- [ ] Implement database persistence
- [ ] Add candidate ranking dashboard
- [ ] Support for multiple languages
- [ ] Integration with popular ATS platforms
- [ ] Advanced analytics and reporting
- [ ] Email notification system
- [ ] Batch processing optimization with Celery

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - feel free to use this project for any purpose.

## Support

For issues, questions, or contributions, please open an issue on GitHub.

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph)
- [LangChain](https://github.com/langchain-ai/langchain)
- [OpenAI](https://openai.com)
- [FastAPI](https://fastapi.tiangolo.com)

---

**Note**: This system is designed to assist in the hiring process, not replace human judgment. Always review automated recommendations and ensure compliance with employment laws and regulations.
