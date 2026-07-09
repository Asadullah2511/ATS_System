from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class MatchingAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def calculate_match_score(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        resume_analysis: Dict[str, Any],
        job_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at matching candidates to job requirements.
            Calculate a comprehensive match score based on:
            - Skills alignment (required vs possessed)
            - Experience relevance and level
            - Education match
            - Career trajectory fit
            - Cultural fit indicators

            Return JSON format:
            {{
                "overall_score": "float 0-100",
                "skills_score": "float 0-100",
                "experience_score": "float 0-100",
                "education_score": "float 0-100",
                "cultural_fit_score": "float 0-100",
                "match_level": "excellent/good/fair/poor",
                "skill_matches": [
                    {{"skill": "name", "required": true/false, "candidate_has": true/false, "match_score": "float 0-100"}}
                ],
                "missing_required_skills": ["list"],
                "additional_skills": ["list of skills candidate has but not required"],
                "score_breakdown": "detailed explanation"
            }}
            """),
            ("user", """
            Candidate Resume:
            {resume_data}

            Resume Analysis:
            {resume_analysis}

            Job Requirements:
            {job_data}

            Job Analysis:
            {job_analysis}
            """)
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "resume_data": str(resume_data),
            "resume_analysis": str(resume_analysis),
            "job_data": str(job_data),
            "job_analysis": str(job_analysis)
        })

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to calculate match score",
                "response": response.content
            }

    def identify_gaps(
        self,
        resume_data: Dict[str, Any],
        job_requirements: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Identify gaps between candidate qualifications and job requirements.
            Categorize gaps by:
            - Critical gaps (must-have requirements not met)
            - Moderate gaps (preferred requirements not met)
            - Minor gaps (nice-to-have not met)
            - Bridgeable gaps (could be learned/acquired quickly)

            Return JSON format:
            {{
                "critical_gaps": [
                    {{"requirement": "string", "impact": "string", "recommendation": "string"}}
                ],
                "moderate_gaps": ["list"],
                "minor_gaps": ["list"],
                "bridgeable_gaps": ["list with learning path suggestions"],
                "gap_analysis_summary": "string"
            }}
            """),
            ("user", "Resume:\n{resume}\n\nJob Requirements:\n{job}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "resume": str(resume_data),
            "job": str(job_requirements)
        })

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to identify gaps",
                "response": response.content
            }
