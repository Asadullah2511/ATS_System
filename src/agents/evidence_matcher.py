from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json


class EvidenceMatcherAgent:
    """
    Searches resume for evidence of meeting requirements using semantic understanding,
    not just keyword matching. Finds implicit demonstrations of skills.
    """

    def __init__(self, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def find_evidence(self, requirement: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Find evidence in resume that addresses a specific requirement."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at finding evidence in resumes, including IMPLICIT evidence.

DO NOT just look for keywords. Look for demonstrations, actions, and results that prove the skill.

Examples:
- Requirement: "leadership" → Evidence: "mentored 3 junior developers" or "led weekly standup"
- Requirement: "5 years Python" → Evidence: "Senior Python Developer 2018-2023"
- Requirement: "stakeholder management" → Evidence: "presented quarterly updates to C-suite"
- Requirement: "scalability experience" → Evidence: "optimized system to handle 10x traffic"

Return JSON:
{{
    "has_evidence": true/false,
    "evidence_items": [
        {{
            "resume_text": "exact quote from resume",
            "match_type": "explicit/implicit/transferable/demonstrated",
            "confidence": 0-100,
            "reasoning": "why this counts as evidence",
            "is_keyword_match": true/false,
            "is_semantic_match": true/false,
            "location": "experience/education/skills/projects"
        }}
    ],
    "overall_match_strength": 0-100,
    "missing_if_any": "what aspect is still unproven"
}}
"""),
            ("user", """Requirement: {requirement_text}
Requirement Type: {requirement_type}
Category: {category}

Resume Data:
{resume_data}

Find ALL evidence, including implicit demonstrations.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "requirement_text": requirement.get("text", ""),
            "requirement_type": requirement.get("requirement_type", ""),
            "category": requirement.get("category", ""),
            "resume_data": json.dumps(resume_data, indent=2)
        })

        try:
            result = json.loads(response.content)
            return result
        except json.JSONDecodeError:
            return {
                "has_evidence": False,
                "evidence_items": [],
                "overall_match_strength": 0,
                "error": response.content
            }

    def batch_find_evidence(
        self,
        requirements: List[Dict[str, Any]],
        resume_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Find evidence for multiple requirements at once."""

        results = []
        for requirement in requirements:
            evidence = self.find_evidence(requirement, resume_data)
            results.append({
                "requirement": requirement,
                "evidence": evidence
            })
        return results

    def cross_reference_evidence(
        self,
        evidence_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze if evidence is being over-claimed (same experience used for too many requirements)."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze if the candidate is using the same experience to claim multiple skills.

This is normal to some extent, but flag if:
- One project/role is claimed as evidence for 10+ different requirements
- Vague statements ("managed projects") used as proof of many specific skills
- No specific examples, just buzzwords

Return JSON:
{{
    "over_claimed_evidence": [
        {{
            "resume_text": "text being overused",
            "claimed_for": ["req1", "req2", ...],
            "concern_level": "low/medium/high",
            "reasoning": "why this is concerning"
        }}
    ],
    "credibility_score": 0-100,
    "red_flags": ["list of concerns"]
}}
"""),
            ("user", "Evidence Results:\n{evidence_results}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "evidence_results": json.dumps(evidence_results, indent=2)
        })

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "over_claimed_evidence": [],
                "credibility_score": 75,
                "red_flags": []
            }
