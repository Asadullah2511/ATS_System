from typing import Dict, Any
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field


class JobParserTool(BaseTool):
    name: str = "job_parser"
    description: str = "Parses job descriptions and extracts structured requirements"
    llm: Any = Field(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.llm is None:
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _run(self, job_text: str, job_id: str = None) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert job description parser. Extract structured information from the job posting.
            Return a JSON object with the following structure:
            {{
                "title": "string",
                "company": "string",
                "location": "string or null",
                "job_type": "string or null",
                "description": "string",
                "requirements": {{
                    "category": "string",
                    "required_skills": ["list of required skills"],
                    "preferred_skills": ["list of preferred skills"],
                    "min_years_experience": "int or null",
                    "education_level": "string or null"
                }},
                "responsibilities": ["list of responsibilities"],
                "salary_range": "string or null",
                "benefits": ["list of benefits"]
            }}
            """),
            ("user", "Job description:\n\n{job_text}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"job_text": job_text})

        import json
        try:
            parsed_data = json.loads(response.content)
            parsed_data["job_id"] = job_id or "unknown"
            parsed_data["raw_text"] = job_text
            return parsed_data
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse job description",
                "raw_text": job_text,
                "response": response.content
            }
