from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class JobAnalysisAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def analyze_job_requirements(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert job requirements analyst. Analyze the job posting and identify:
            1. Must-have vs nice-to-have requirements
            2. Priority ranking of skills
            3. Hidden requirements not explicitly stated
            4. Seniority level expectations
            5. Cultural fit indicators

            Return JSON format:
            {{
                "must_have_skills": ["list"],
                "nice_to_have_skills": ["list"],
                "priority_skills": [
                    {{"skill": "name", "priority": "high/medium/low", "reason": "explanation"}}
                ],
                "hidden_requirements": ["list"],
                "seniority_level": "entry/mid/senior/staff/principal",
                "cultural_indicators": ["list"],
                "role_complexity": "string assessment"
            }}
            """),
            ("user", "Job posting data:\n\n{job_data}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"job_data": str(job_data)})

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to analyze job requirements",
                "response": response.content
            }

    def identify_deal_breakers(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Identify absolute deal-breakers in this job posting.
            These are requirements that if not met, should disqualify a candidate.

            Return JSON format:
            {{
                "deal_breakers": [
                    {{"requirement": "string", "category": "skill/experience/education/certification", "reason": "why it's critical"}}
                ],
                "flexibility_areas": ["list of areas where there might be flexibility"],
                "assessment_notes": "string"
            }}
            """),
            ("user", "Job posting data:\n\n{job_data}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"job_data": str(job_data)})

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to identify deal-breakers",
                "response": response.content
            }
