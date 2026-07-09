from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json


class GapAnalyzerAgent:
    """
    Analyzes gaps between requirements and evidence.
    For critical gaps, generates explanations instead of auto-rejecting.
    """

    def __init__(self, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def analyze_gaps(
        self,
        requirements_with_evidence: List[Dict[str, Any]],
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Identify and categorize gaps."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze gaps between job requirements and candidate evidence.

Classify each gap:
1. CRITICAL: Must-have requirement with no evidence → candidate likely fails
2. SIGNIFICANT: Must-have with weak/partial evidence → needs investigation
3. MODERATE: Nice-to-have missing → candidate could still succeed
4. BRIDGEABLE: Missing but learnable quickly given candidate's background
5. EXPLAINABLE: Missing but candidate may have valid reason (career break, pivot, etc.)

For CRITICAL and SIGNIFICANT gaps, assess if there's a potential explanation:
- Career break (parental leave, caregiving, health)
- Career pivot (transitioning from related field)
- Recent grad (building experience)
- Skill transfer (has equivalent skill with different name)

Return JSON:
{{
    "gaps": [
        {{
            "requirement": "requirement text",
            "gap_type": "critical/significant/moderate/bridgeable/explainable",
            "severity": "high/medium/low",
            "explanation": "what's missing and why it matters",
            "is_bridgeable": true/false,
            "time_to_bridge": "2 weeks/1 month/3 months/6+ months",
            "potential_explanations": ["possible reasons for this gap"],
            "recommendation": "auto_reject/request_explanation/acceptable_gap/minor_concern"
        }}
    ],
    "critical_gaps_count": 0,
    "requires_candidate_explanation": true/false,
    "explanation_questions": ["specific questions to ask candidate"],
    "overall_gap_assessment": "deal_breaker/needs_explanation/acceptable/minor"
}}
"""),
            ("user", """Requirements with Evidence:
{requirements_evidence}

Resume Summary:
{resume_summary}

Analyze all gaps and determine if any require candidate explanation before rejection.""")
        ])

        resume_summary = {
            "candidate": resume_data.get("candidate", {}),
            "experience": resume_data.get("experience", []),
            "education": resume_data.get("education", []),
            "skills": resume_data.get("skills", [])
        }

        chain = prompt | self.llm
        response = chain.invoke({
            "requirements_evidence": json.dumps(requirements_with_evidence, indent=2),
            "resume_summary": json.dumps(resume_summary, indent=2)
        })

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "gaps": [],
                "critical_gaps_count": 0,
                "requires_candidate_explanation": False,
                "error": response.content
            }

    def generate_explanation_request(
        self,
        gap_analysis: Dict[str, Any],
        candidate_name: str
    ) -> str:
        """Generate a personalized message asking candidate to explain gaps."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate a respectful, personalized email to the candidate asking them to explain gaps.

Be:
- Specific about what you want explained
- Non-judgmental and open
- Clear that this is NOT a rejection, just clarification
- Professional but warm

DO NOT:
- Sound accusatory
- Mention "red flags" or "concerns"
- Imply they're unqualified
- Use form letter language
"""),
            ("user", """Candidate: {candidate_name}

Gaps that need explanation:
{gaps}

Questions to ask:
{questions}

Generate email subject and body.""")
        ])

        gaps_needing_explanation = [
            g for g in gap_analysis.get("gaps", [])
            if g.get("recommendation") == "request_explanation"
        ]

        chain = prompt | self.llm
        response = chain.invoke({
            "candidate_name": candidate_name,
            "gaps": json.dumps(gaps_needing_explanation, indent=2),
            "questions": json.dumps(gap_analysis.get("explanation_questions", []))
        })

        return response.content

    def evaluate_gap_explanation(
        self,
        gap: Dict[str, Any],
        candidate_explanation: str
    ) -> Dict[str, Any]:
        """Evaluate if the candidate's explanation is satisfactory."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Evaluate if the candidate's explanation adequately addresses the gap.

Consider:
- Is the explanation honest and specific?
- Does it make sense given their career trajectory?
- Does it show awareness of the gap and plan to address it?
- Are they credible or making excuses?

Return JSON:
{{
    "explanation_satisfactory": true/false,
    "credibility": "high/medium/low",
    "reasoning": "why you accept/reject this explanation",
    "reduces_concern": true/false,
    "new_recommendation": "proceed/reject/request_more_info"
}}
"""),
            ("user", """Gap: {gap}

Candidate's Explanation: {explanation}

Evaluate.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "gap": json.dumps(gap, indent=2),
            "explanation": candidate_explanation
        })

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "explanation_satisfactory": False,
                "credibility": "low",
                "reasoning": "Unable to parse explanation",
                "reduces_concern": False,
                "new_recommendation": "reject"
            }
