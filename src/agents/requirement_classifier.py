from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json


class RequirementClassifierAgent:
    """
    Classifies job requirements into must-have, nice-to-have, and disguised-nice-to-have.
    Detects when requirements are inflated (e.g., "5+ years required" when 3 is actually fine).
    """

    def __init__(self, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def classify_requirements(self, job_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert recruiter who can detect when job requirements are inflated or flexible.

Your task is to classify each requirement into:
1. MUST_HAVE: Truly critical, candidate will fail without it
2. NICE_TO_HAVE: Explicitly optional or preferred
3. DISGUISED_NICE_TO_HAVE: Stated as required but context suggests flexibility

For disguised requirements, look for:
- Years of experience that seem arbitrary (e.g., "5+ years" for mid-level role)
- Tech stack requirements where similar skills would transfer easily
- Requirements contradicted by other parts of the JD
- Industry-standard inflation (saying "required" but really "strongly preferred")

Return JSON with this structure:
{{
    "requirements": [
        {{
            "text": "exact requirement text",
            "category": "technical_skill/soft_skill/experience/education/certification",
            "requirement_type": "must_have/nice_to_have/disguised_nice_to_have",
            "reasoning": "why you classified it this way",
            "keywords": ["key", "terms"],
            "actual_necessity": "what's really needed",
            "flexibility_score": 0-100 (0=rigid, 100=very flexible)
        }}
    ],
    "hidden_flexibility": "overall assessment of how flexible this role really is"
}}
"""),
            ("user", "Job Title: {title}\n\nJob Description:\n{description}\n\nRequirements Section:\n{requirements}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "title": job_data.get("title", ""),
            "description": job_data.get("description", ""),
            "requirements": str(job_data.get("requirements", {}))
        })

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "requirements": [],
                "hidden_flexibility": "Unable to parse",
                "error": response.content
            }

    def detect_requirement_contradictions(self, requirements: List[Dict]) -> List[Dict]:
        """Detect requirements that contradict each other or the job level."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze these requirements for contradictions or unrealistic combinations.

Look for:
- Junior role with senior requirements
- Requirements that conflict with each other
- Unrealistic skill combinations
- Time paradoxes (more years required than technology has existed)

Return JSON:
{{
    "contradictions": [
        {{
            "requirement_1": "text",
            "requirement_2": "text",
            "contradiction_type": "level_mismatch/skill_conflict/time_paradox/other",
            "explanation": "why this is contradictory"
        }}
    ],
    "overall_realism_score": 0-100
}}
"""),
            ("user", "Requirements:\n{requirements}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"requirements": json.dumps(requirements, indent=2)})

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {"contradictions": [], "overall_realism_score": 50}
