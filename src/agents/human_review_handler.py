from typing import Dict, Any, List, Optional
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import json
from datetime import datetime


class HumanReviewHandler:
    """
    Handles human-in-the-loop reviews for borderline cases.
    Provides context to human reviewers and captures their decisions.
    """

    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)

    def determine_if_needs_human_review(
        self,
        evaluation_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Determine if this evaluation needs human review."""

        triggers = []

        overall_score = evaluation_data.get("match_score", {}).get("overall_score", 0)
        if 45 <= overall_score <= 65:
            triggers.append({
                "type": "borderline_score",
                "reason": f"Score {overall_score} is in borderline range (45-65)",
                "priority": "medium"
            })

        has_bias = evaluation_data.get("bias_audit", {}).get("has_bias", False)
        if has_bias:
            high_severity_flags = [
                f for f in evaluation_data.get("bias_audit", {}).get("bias_flags", [])
                if f.get("severity") == "high"
            ]
            if high_severity_flags:
                triggers.append({
                    "type": "bias_detected",
                    "reason": f"High severity bias flags: {len(high_severity_flags)}",
                    "priority": "high"
                })

        gap_analysis = evaluation_data.get("gap_analysis", {})
        if gap_analysis.get("requires_candidate_explanation", False):
            triggers.append({
                "type": "critical_gap_needs_explanation",
                "reason": "Critical gaps that candidate should explain",
                "priority": "high"
            })

        recommendation = evaluation_data.get("recommendation", {})
        model_confidence = recommendation.get("confidence_level", "low")
        if model_confidence == "low":
            triggers.append({
                "type": "low_confidence",
                "reason": "Model has low confidence in recommendation",
                "priority": "medium"
            })

        credibility = evaluation_data.get("evidence_analysis", {}).get("credibility_score", 100)
        if credibility < 60:
            triggers.append({
                "type": "credibility_concern",
                "reason": f"Evidence credibility score: {credibility}",
                "priority": "medium"
            })

        return {
            "needs_review": len(triggers) > 0,
            "triggers": triggers,
            "priority": max([t["priority"] for t in triggers], default="low"),
            "estimated_review_time": self._estimate_review_time(triggers)
        }

    def prepare_review_package(
        self,
        evaluation_data: Dict[str, Any],
        review_triggers: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Prepare comprehensive package for human reviewer."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Summarize this candidate evaluation for a human reviewer.

Focus on:
1. Why this needs human review
2. Key decision points
3. Conflicting signals
4. Specific questions for the reviewer

Be concise - reviewer has limited time.
Highlight the MOST important 3-5 points.
"""),
            ("user", """Full Evaluation:
{evaluation}

Review Triggers:
{triggers}

Prepare review summary.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "evaluation": json.dumps(evaluation_data, indent=2),
            "triggers": json.dumps(review_triggers, indent=2)
        })

        candidate = evaluation_data.get("parsed_resume", {}).get("candidate", {})
        job = evaluation_data.get("parsed_job", {})

        return {
            "candidate_name": candidate.get("name", "Unknown"),
            "candidate_email": candidate.get("email", "Unknown"),
            "job_title": job.get("title", "Unknown"),
            "job_id": job.get("job_id", "Unknown"),
            "model_recommendation": evaluation_data.get("recommendation", {}).get("recommendation", "unknown"),
            "model_confidence": evaluation_data.get("recommendation", {}).get("confidence_level", "low"),
            "overall_score": evaluation_data.get("match_score", {}).get("overall_score", 0),
            "review_triggers": review_triggers,
            "executive_summary": response.content,
            "key_questions": self._generate_review_questions(evaluation_data, review_triggers),
            "relevant_excerpts": self._extract_relevant_excerpts(evaluation_data),
            "review_deadline": self._calculate_review_deadline(review_triggers),
            "bias_warnings": evaluation_data.get("bias_audit", {}).get("bias_flags", [])
        }

    def _generate_review_questions(
        self,
        evaluation_data: Dict[str, Any],
        triggers: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate specific questions for the human reviewer."""

        questions = []

        for trigger in triggers:
            if trigger["type"] == "borderline_score":
                questions.append("Does the candidate's experience quality make up for quantitative gaps?")

            elif trigger["type"] == "bias_detected":
                questions.append("Are there legitimate concerns here, or is this bias affecting our judgment?")

            elif trigger["type"] == "critical_gap_needs_explanation":
                questions.append("Should we ask the candidate to explain these gaps before deciding?")

            elif trigger["type"] == "low_confidence":
                questions.append("What additional information would help make a confident decision?")

            elif trigger["type"] == "credibility_concern":
                questions.append("Do the candidate's claims seem credible? Should we verify references?")

        questions.extend([
            "Would you interview this candidate?",
            "What's your gut feeling about culture fit?",
            "What's the biggest risk if we move forward?"
        ])

        return questions

    def _extract_relevant_excerpts(self, evaluation_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract most relevant parts of resume and analysis."""

        return {
            "strengths": evaluation_data.get("recommendation", {}).get("strengths", [])[:3],
            "weaknesses": evaluation_data.get("recommendation", {}).get("weaknesses", [])[:3],
            "critical_gaps": [
                g.get("explanation")
                for g in evaluation_data.get("gap_analysis", {}).get("gaps", [])
                if g.get("gap_type") == "critical"
            ][:3],
            "bias_concerns": [
                f"{b.get('bias_type')}: {b.get('reasoning')}"
                for b in evaluation_data.get("bias_audit", {}).get("bias_flags", [])
                if b.get("severity") in ["high", "medium"]
            ][:3]
        }

    def _estimate_review_time(self, triggers: List[Dict[str, Any]]) -> str:
        """Estimate how long human review will take."""

        base_time = 5

        for trigger in triggers:
            if trigger.get("priority") == "high":
                base_time += 5
            elif trigger.get("priority") == "medium":
                base_time += 3

        if base_time <= 5:
            return "5 minutes"
        elif base_time <= 10:
            return "10 minutes"
        elif base_time <= 15:
            return "15 minutes"
        else:
            return "20+ minutes"

    def _calculate_review_deadline(self, triggers: List[Dict[str, Any]]) -> str:
        """Calculate when review should be completed."""

        has_high_priority = any(t.get("priority") == "high" for t in triggers)

        if has_high_priority:
            return "within 24 hours"
        else:
            return "within 3 business days"

    def capture_human_decision(
        self,
        evaluation_id: str,
        reviewer_name: str,
        decision: str,
        reasoning: Optional[str] = None,
        additional_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Capture the human reviewer's decision."""

        return {
            "evaluation_id": evaluation_id,
            "reviewer_name": reviewer_name,
            "decision": decision,
            "reasoning": reasoning,
            "additional_notes": additional_notes,
            "reviewed_at": datetime.now().isoformat(),
            "review_metadata": {
                "review_source": "human",
                "review_type": "borderline_case"
            }
        }

    def analyze_human_override(
        self,
        model_recommendation: str,
        human_decision: str,
        reasoning: Optional[str] = None
    ) -> Dict[str, Any]:
        """Analyze why human overrode the model recommendation."""

        if model_recommendation == human_decision:
            return {
                "is_override": False,
                "agreement_type": "full_agreement"
            }

        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze why the human reviewer disagreed with the model.

Categorize the disagreement:
- better_context: Human had context model lacked
- bias_correction: Human caught model bias
- risk_tolerance: Different risk assessment
- gut_feeling: Intangible factors (culture fit, potential)
- domain_expertise: Human's industry knowledge
- error_correction: Model made factual error

Return JSON:
{{
    "disagreement_type": "category",
    "likely_reason": "explanation",
    "should_retrain": true/false (if model needs updating),
    "learning_opportunity": "what model should learn"
}}
"""),
            ("user", """Model Recommended: {model_rec}
Human Decided: {human_dec}
Human Reasoning: {reasoning}

Analyze disagreement.""")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "model_rec": model_recommendation,
            "human_dec": human_decision,
            "reasoning": reasoning or "No reasoning provided"
        })

        try:
            analysis = json.loads(response.content)
            analysis["is_override"] = True
            return analysis
        except json.JSONDecodeError:
            return {
                "is_override": True,
                "disagreement_type": "unknown",
                "likely_reason": "Unable to analyze",
                "should_retrain": False
            }
