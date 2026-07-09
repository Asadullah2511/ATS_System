from typing import Dict, Any
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field


class ExperienceAnalyzerTool(BaseTool):
    name: str = "experience_analyzer"
    description: str = "Analyzes work experience and calculates relevant metrics"
    llm: Any = Field(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.llm is None:
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _run(self, experience_list: str, job_requirements: str) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at analyzing work experience relevance.
            Compare the candidate's experience with job requirements and provide analysis.

            Return a JSON object with:
            {{
                "total_years_experience": "float",
                "relevant_years_experience": "float",
                "career_progression": "string description",
                "industry_match": "string assessment",
                "role_relevance_score": "float 0-100",
                "key_achievements": ["list of notable achievements"],
                "experience_gaps": ["list of gaps or concerns"],
                "recommendations": ["list of assessment points"]
            }}
            """),
            ("user", "Candidate Experience:\n{experience}\n\nJob Requirements:\n{requirements}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "experience": experience_list,
            "requirements": job_requirements
        })

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to analyze experience",
                "response": response.content
            }
