from typing import TypedDict, Annotated, Dict, Any, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import operator
from datetime import datetime

from src.agents.requirement_classifier import RequirementClassifierAgent
from src.agents.evidence_matcher import EvidenceMatcherAgent
from src.agents.gap_analyzer import GapAnalyzerAgent
from src.agents.bias_auditor import BiasAuditorAgent
from src.agents.human_review_handler import HumanReviewHandler
from src.agents.resume_agent import ResumeAnalysisAgent
from src.agents.matching_agent import MatchingAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.tools.resume_parser import ResumeParserTool
from src.tools.job_parser import JobParserTool
from src.utils.memgraph_connector import MemgraphConnector


class AdvancedATSState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    resume_file_path: str
    job_description: str
    job_id: str
    evaluation_id: str

    parsed_resume: Dict[str, Any]
    parsed_job: Dict[str, Any]

    classified_requirements: Dict[str, Any]

    evidence_results: list[Dict[str, Any]]
    evidence_credibility: Dict[str, Any]

    gap_analysis: Dict[str, Any]
    requires_explanation: bool
    explanation_generated: str

    bias_audit: Dict[str, Any]
    implicit_bias_patterns: Dict[str, Any]
    fairness_score: float

    match_score: Dict[str, Any]
    recommendation: Dict[str, Any]

    needs_human_review: bool
    review_package: Dict[str, Any]
    human_decision: Dict[str, Any]

    final_evaluation: Dict[str, Any]
    error: str


class AdvancedATSGraph:
    def __init__(self, memgraph_host: str = "localhost", memgraph_password: str = ""):
        self.resume_parser = ResumeParserTool()
        self.job_parser = JobParserTool()

        self.requirement_classifier = RequirementClassifierAgent()
        self.evidence_matcher = EvidenceMatcherAgent()
        self.gap_analyzer = GapAnalyzerAgent()
        self.bias_auditor = BiasAuditorAgent()
        self.human_review_handler = HumanReviewHandler()

        self.resume_agent = ResumeAnalysisAgent()
        self.matching_agent = MatchingAgent()
        self.recommendation_agent = RecommendationAgent()

        try:
            self.db = MemgraphConnector(
                host=memgraph_host,
                port=7687,
                username="",
                password=memgraph_password
            )
            self.db.create_indexes()
        except Exception as e:
            print(f"Warning: Memgraph connection failed: {e}")
            self.db = None

    def parse_resume_node(self, state: AdvancedATSState) -> AdvancedATSState:
        try:
            parsed = self.resume_parser._run(state["resume_file_path"])
            state["parsed_resume"] = parsed

            if self.db:
                self.db.store_candidate(parsed.get("candidate", {}))

            return state
        except Exception as e:
            state["error"] = f"Resume parsing error: {str(e)}"
            return state

    def parse_job_node(self, state: AdvancedATSState) -> AdvancedATSState:
        try:
            parsed = self.job_parser._run(
                state["job_description"],
                state.get("job_id", "unknown")
            )
            state["parsed_job"] = parsed

            if self.db:
                self.db.store_job(parsed)

            return state
        except Exception as e:
            state["error"] = f"Job parsing error: {str(e)}"
            return state

    def classify_requirements_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Classify requirements into must-have, nice-to-have, and disguised-nice-to-have."""
        try:
            classified = self.requirement_classifier.classify_requirements(
                state["parsed_job"]
            )

            contradictions = self.requirement_classifier.detect_requirement_contradictions(
                classified.get("requirements", [])
            )

            classified["contradictions"] = contradictions

            state["classified_requirements"] = classified

            if self.db:
                job_id = state["parsed_job"].get("job_id")
                for req in classified.get("requirements", []):
                    self.db.store_requirement(job_id, req)

            return state
        except Exception as e:
            state["error"] = f"Requirement classification error: {str(e)}"
            return state

    def evidence_matching_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Find evidence in resume for each requirement."""
        try:
            requirements = state["classified_requirements"].get("requirements", [])
            resume_data = state["parsed_resume"]

            evidence_results = self.evidence_matcher.batch_find_evidence(
                requirements,
                resume_data
            )

            credibility = self.evidence_matcher.cross_reference_evidence(
                evidence_results
            )

            state["evidence_results"] = evidence_results
            state["evidence_credibility"] = credibility

            return state
        except Exception as e:
            state["error"] = f"Evidence matching error: {str(e)}"
            return state

    def gap_analysis_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Analyze gaps and determine if explanation is needed."""
        try:
            gap_analysis = self.gap_analyzer.analyze_gaps(
                state["evidence_results"],
                state["parsed_resume"]
            )

            state["gap_analysis"] = gap_analysis
            state["requires_explanation"] = gap_analysis.get("requires_candidate_explanation", False)

            return state
        except Exception as e:
            state["error"] = f"Gap analysis error: {str(e)}"
            return state

    def generate_explanation_request_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Generate explanation request for candidate."""
        try:
            candidate_name = state["parsed_resume"].get("candidate", {}).get("name", "Candidate")

            explanation_request = self.gap_analyzer.generate_explanation_request(
                state["gap_analysis"],
                candidate_name
            )

            state["explanation_generated"] = explanation_request

            return state
        except Exception as e:
            state["error"] = f"Explanation generation error: {str(e)}"
            return state

    def bias_audit_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Audit for bias in reasoning."""
        try:
            all_analysis = {
                "requirements": state.get("classified_requirements"),
                "evidence": state.get("evidence_results"),
                "gaps": state.get("gap_analysis")
            }

            bias_audit = self.bias_auditor.audit_for_bias(
                state["parsed_resume"],
                state.get("match_score", {}),
                all_analysis
            )

            candidate_name = state["parsed_resume"].get("candidate", {}).get("name", "")
            implicit_patterns = self.bias_auditor.detect_implicit_bias_patterns(
                candidate_name,
                state["parsed_resume"]
            )

            state["bias_audit"] = bias_audit
            state["implicit_bias_patterns"] = implicit_patterns
            state["fairness_score"] = bias_audit.get("overall_fairness_score", 100)

            if self.db and state.get("evaluation_id"):
                for flag in bias_audit.get("bias_flags", []):
                    self.db.store_bias_flag(state["evaluation_id"], flag)

            return state
        except Exception as e:
            state["error"] = f"Bias audit error: {str(e)}"
            return state

    def calculate_match_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Calculate match score considering evidence quality."""
        try:
            evidence_summary = {
                "requirements_with_evidence": state["evidence_results"],
                "credibility_score": state["evidence_credibility"].get("credibility_score", 75)
            }

            match_score = self.matching_agent.calculate_match_score(
                state["parsed_resume"],
                state["parsed_job"],
                {"evidence_analysis": evidence_summary},
                {"requirements": state["classified_requirements"]}
            )

            state["match_score"] = match_score

            return state
        except Exception as e:
            state["error"] = f"Matching error: {str(e)}"
            return state

    def generate_recommendation_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Generate final recommendation."""
        try:
            recommendation = self.recommendation_agent.generate_recommendation(
                state["parsed_resume"],
                state["parsed_job"],
                state["match_score"],
                state["gap_analysis"]
            )

            state["recommendation"] = recommendation

            return state
        except Exception as e:
            state["error"] = f"Recommendation error: {str(e)}"
            return state

    def determine_human_review_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Determine if human review is needed."""
        try:
            evaluation_data = {
                "parsed_resume": state["parsed_resume"],
                "parsed_job": state["parsed_job"],
                "match_score": state["match_score"],
                "gap_analysis": state["gap_analysis"],
                "bias_audit": state["bias_audit"],
                "recommendation": state["recommendation"],
                "evidence_analysis": state["evidence_credibility"]
            }

            review_decision = self.human_review_handler.determine_if_needs_human_review(
                evaluation_data
            )

            state["needs_human_review"] = review_decision.get("needs_review", False)

            if state["needs_human_review"]:
                review_package = self.human_review_handler.prepare_review_package(
                    evaluation_data,
                    review_decision.get("triggers", [])
                )
                state["review_package"] = review_package

            return state
        except Exception as e:
            state["error"] = f"Human review determination error: {str(e)}"
            return state

    def await_human_review_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Pause for human review (simulated for now)."""

        state["human_decision"] = {
            "status": "pending",
            "review_package_id": state.get("evaluation_id"),
            "note": "Human review required - evaluation paused"
        }

        return state

    def compile_final_evaluation_node(self, state: AdvancedATSState) -> AdvancedATSState:
        """Compile everything into final evaluation."""
        try:
            import uuid
            evaluation_id = str(uuid.uuid4())
            state["evaluation_id"] = evaluation_id

            final_eval = {
                "evaluation_id": evaluation_id,
                "candidate": state["parsed_resume"].get("candidate", {}),
                "job": {
                    "job_id": state["parsed_job"].get("job_id"),
                    "title": state["parsed_job"].get("title"),
                    "company": state["parsed_job"].get("company")
                },
                "classified_requirements": state["classified_requirements"],
                "evidence_analysis": {
                    "evidence_results": state["evidence_results"],
                    "credibility": state["evidence_credibility"]
                },
                "gap_analysis": state["gap_analysis"],
                "bias_audit": state["bias_audit"],
                "implicit_bias_patterns": state["implicit_bias_patterns"],
                "fairness_score": state["fairness_score"],
                "match_score": state["match_score"],
                "recommendation": state["recommendation"],
                "needs_human_review": state.get("needs_human_review", False),
                "review_package": state.get("review_package", {}),
                "human_decision": state.get("human_decision", {}),
                "timestamp": datetime.now().isoformat()
            }

            state["final_evaluation"] = final_eval

            if self.db:
                eval_data = {
                    "candidate_email": state["parsed_resume"].get("candidate", {}).get("email"),
                    "job_id": state["parsed_job"].get("job_id"),
                    "overall_score": state["match_score"].get("overall_score", 0),
                    "skills_score": state["match_score"].get("skills_score", 0),
                    "experience_score": state["match_score"].get("experience_score", 0),
                    "education_score": state["match_score"].get("education_score", 0),
                    "match_level": state["match_score"].get("match_level", "poor"),
                    "recommendation": state["recommendation"].get("recommendation", "no"),
                    "confidence_level": state["recommendation"].get("confidence_level", "low"),
                    "has_bias": state["bias_audit"].get("has_bias", False),
                    "fairness_score": state["fairness_score"],
                    "requires_human_review": state.get("needs_human_review", False)
                }
                self.db.store_evaluation(eval_data)

            return state
        except Exception as e:
            state["error"] = f"Final evaluation compilation error: {str(e)}"
            return state

    def route_after_gap_analysis(self, state: AdvancedATSState) -> Literal["generate_explanation", "bias_audit"]:
        """Route to explanation generation if needed, otherwise continue to bias audit."""
        if state.get("requires_explanation", False):
            return "generate_explanation"
        return "bias_audit"

    def route_after_human_review_check(self, state: AdvancedATSState) -> Literal["human_review", "compile"]:
        """Route to human review if needed, otherwise compile."""
        if state.get("needs_human_review", False):
            return "human_review"
        return "compile"


def create_advanced_ats_graph(memgraph_host: str = "localhost", memgraph_password: str = "") -> StateGraph:
    """Create the advanced ATS graph with all nodes."""
    ats = AdvancedATSGraph(memgraph_host=memgraph_host, memgraph_password=memgraph_password)

    workflow = StateGraph(AdvancedATSState)

    workflow.add_node("parse_resume", ats.parse_resume_node)
    workflow.add_node("parse_job", ats.parse_job_node)
    workflow.add_node("classify_requirements", ats.classify_requirements_node)
    workflow.add_node("evidence_matching", ats.evidence_matching_node)
    workflow.add_node("gap_analysis", ats.gap_analysis_node)
    workflow.add_node("generate_explanation", ats.generate_explanation_request_node)
    workflow.add_node("bias_audit", ats.bias_audit_node)
    workflow.add_node("calculate_match", ats.calculate_match_node)
    workflow.add_node("generate_recommendation", ats.generate_recommendation_node)
    workflow.add_node("determine_human_review", ats.determine_human_review_node)
    workflow.add_node("human_review", ats.await_human_review_node)
    workflow.add_node("compile", ats.compile_final_evaluation_node)

    workflow.set_entry_point("parse_resume")

    workflow.add_edge("parse_resume", "parse_job")
    workflow.add_edge("parse_job", "classify_requirements")
    workflow.add_edge("classify_requirements", "evidence_matching")
    workflow.add_edge("evidence_matching", "gap_analysis")

    workflow.add_conditional_edges(
        "gap_analysis",
        ats.route_after_gap_analysis,
        {
            "generate_explanation": "generate_explanation",
            "bias_audit": "bias_audit"
        }
    )

    workflow.add_edge("generate_explanation", "bias_audit")
    workflow.add_edge("bias_audit", "calculate_match")
    workflow.add_edge("calculate_match", "generate_recommendation")
    workflow.add_edge("generate_recommendation", "determine_human_review")

    workflow.add_conditional_edges(
        "determine_human_review",
        ats.route_after_human_review_check,
        {
            "human_review": "human_review",
            "compile": "compile"
        }
    )

    workflow.add_edge("human_review", "compile")
    workflow.add_edge("compile", END)

    return workflow.compile()
