from typing import Dict, Any, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
import re


class BiasAuditorAgent:
    """
    Audits the model's own reasoning for bias.
    Flags if scoring leaned on proxies correlated with protected attributes.
    """

    def __init__(self, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def audit_for_bias(
        self,
        resume_data: Dict[str, Any],
        scoring_reasoning: Dict[str, Any],
        all_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Audit the evaluation for bias indicators."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a bias detection expert. Audit this candidate evaluation for bias.

Look for reasoning that inappropriately considered:

AGE PROXIES:
- Graduation year → assuming age
- "Long career" → age discrimination
- "Recent grad" → age discrimination
- Employment gaps → may indicate caregiving (gender) or health issues
- "Overqualified" → often age-related

GENDER PROXIES:
- Career gaps → often women returning from maternity leave
- Part-time work → often women with caregiving responsibilities
- "Aggressive" vs "assertive" → gendered language
- Industries stereotypically gendered (nursing, engineering)

NAME BIAS:
- Ethnic-sounding names → unconscious bias
- Assumptions about cultural fit based on name
- Assumptions about language skills based on name

EDUCATION PRESTIGE:
- Ivy League bias → socioeconomic proxy
- "Target school" preference → discriminatory
- Discounting non-traditional education → classism

LOCATION BIAS:
- Urban vs rural → socioeconomic/cultural assumptions
- International experience → positive bias
- "Cultural fit" based on location

CAREER PATH BIAS:
- Non-linear paths penalized → discriminates against career pivoters
- Job hopping → may be industry norm or economic necessity
- Startup experience valued over other sectors → arbitrary

Return JSON:
{{
    "has_bias": true/false,
    "bias_flags": [
        {{
            "bias_type": "age/gender/name/education_prestige/location/career_path/other",
            "detected_in": "which part of reasoning",
            "problematic_text": "exact text that shows bias",
            "reasoning": "why this is biased",
            "severity": "high/medium/low",
            "alternative_framing": "how to evaluate this fairly",
            "confidence": 0-100
        }}
    ],
    "overall_fairness_score": 0-100,
    "recommendations": ["how to make evaluation fairer"],
    "protected_attributes_detected": ["age", "gender", etc.],
    "requires_human_review": true/false
}}
"""),
            ("user", """Resume Data:
{resume_data}

Scoring & Reasoning:
{scoring_reasoning}

All Analysis:
{all_analysis}

Audit for bias.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "resume_data": json.dumps(resume_data, indent=2),
            "scoring_reasoning": json.dumps(scoring_reasoning, indent=2),
            "all_analysis": json.dumps(all_analysis, indent=2)
        })

        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "has_bias": False,
                "bias_flags": [],
                "overall_fairness_score": 100,
                "error": response.content
            }

    def detect_implicit_bias_patterns(
        self,
        candidate_name: str,
        resume_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Detect patterns that might trigger implicit bias."""

        patterns = {
            "age_indicators": [],
            "gender_indicators": [],
            "name_ethnicity": None,
            "employment_gaps": [],
            "education_prestige": [],
            "location_factors": []
        }

        education = resume_data.get("education", [])
        experience = resume_data.get("experience", [])

        if education:
            grad_years = [
                e.get("end_date") for e in education
                if e.get("end_date")
            ]
            if grad_years:
                patterns["age_indicators"].append({
                    "type": "graduation_year",
                    "values": grad_years,
                    "risk": "Could infer approximate age"
                })

            prestigious_keywords = ["Harvard", "MIT", "Stanford", "Yale", "Princeton", "Ivy"]
            for edu in education:
                institution = edu.get("institution", "")
                if any(keyword.lower() in institution.lower() for keyword in prestigious_keywords):
                    patterns["education_prestige"].append({
                        "institution": institution,
                        "risk": "Prestige bias - may favor privileged backgrounds"
                    })

        if experience:
            exp_list = sorted(experience, key=lambda x: x.get("start_date", ""), reverse=True)

            for i in range(len(exp_list) - 1):
                current_end = exp_list[i].get("end_date")
                next_start = exp_list[i + 1].get("start_date")

                if current_end and next_start:
                    pass

        name_indicators = self._analyze_name_bias(candidate_name)
        patterns["name_ethnicity"] = name_indicators

        return {
            "patterns_detected": patterns,
            "bias_risk_score": self._calculate_bias_risk(patterns),
            "mitigation_needed": True if self._calculate_bias_risk(patterns) > 30 else False
        }

    def _analyze_name_bias(self, name: str) -> Dict[str, Any]:
        """Analyze if name might trigger unconscious bias."""

        common_western_names = [
            "john", "michael", "david", "james", "robert", "william",
            "mary", "patricia", "jennifer", "linda", "elizabeth", "susan"
        ]

        name_lower = name.lower()

        is_common_western = any(
            common in name_lower
            for common in common_western_names
        )

        return {
            "name": name,
            "appears_western_common": is_common_western,
            "risk_level": "low" if is_common_western else "medium",
            "note": "Non-Western names may face unconscious bias in screening"
        }

    def _calculate_bias_risk(self, patterns: Dict) -> float:
        """Calculate overall bias risk score from detected patterns."""

        risk_score = 0

        if patterns.get("age_indicators"):
            risk_score += 20

        if patterns.get("education_prestige"):
            risk_score += 15

        if patterns.get("employment_gaps"):
            risk_score += 25

        name_info = patterns.get("name_ethnicity", {})
        if not name_info.get("appears_western_common", True):
            risk_score += 20

        return min(risk_score, 100)

    def generate_fairness_report(
        self,
        bias_audit: Dict[str, Any],
        implicit_patterns: Dict[str, Any]
    ) -> str:
        """Generate human-readable fairness report."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate a clear fairness report for the hiring team.

Explain:
- What bias risks were detected
- Why they matter
- How they might have affected the evaluation
- Recommendations for fair consideration

Be specific and actionable. Use plain language."""),
            ("user", """Bias Audit:
{bias_audit}

Implicit Pattern Detection:
{implicit_patterns}

Generate fairness report.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "bias_audit": json.dumps(bias_audit, indent=2),
            "implicit_patterns": json.dumps(implicit_patterns, indent=2)
        })

        return response.content
