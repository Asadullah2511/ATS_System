from typing import TypedDict, Annotated, Dict, Any
from langgraph.graph import StateGraph, END
from langchain_core.messages import BaseMessage
import operator

from src.agents.resume_agent import ResumeAnalysisAgent
from src.agents.job_agent import JobAnalysisAgent
from src.agents.matching_agent import MatchingAgent
from src.agents.recommendation_agent import RecommendationAgent
from src.tools.resume_parser import ResumeParserTool
from src.tools.job_parser import JobParserTool


class ATSState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    resume_file_path: str
    job_description: str
    job_id: str

    parsed_resume: Dict[str, Any]
    parsed_job: Dict[str, Any]

    resume_analysis: Dict[str, Any]
    job_analysis: Dict[str, Any]

    match_score: Dict[str, Any]
    gap_analysis: Dict[str, Any]

    recommendation: Dict[str, Any]
    interview_questions: Dict[str, Any]

    final_evaluation: Dict[str, Any]
    error: str


class ATSGraph:
    def __init__(self):
        self.resume_parser = ResumeParserTool()
        self.job_parser = JobParserTool()

        self.resume_agent = ResumeAnalysisAgent()
        self.job_agent = JobAnalysisAgent()
        self.matching_agent = MatchingAgent()
        self.recommendation_agent = RecommendationAgent()

    def parse_resume_node(self, state: ATSState) -> ATSState:
        try:
            parsed = self.resume_parser._run(state["resume_file_path"])
            state["parsed_resume"] = parsed
            return state
        except Exception as e:
            state["error"] = f"Resume parsing error: {str(e)}"
            return state

    def parse_job_node(self, state: ATSState) -> ATSState:
        try:
            parsed = self.job_parser._run(
                state["job_description"],
                state.get("job_id", "unknown")
            )
            state["parsed_job"] = parsed
            return state
        except Exception as e:
            state["error"] = f"Job parsing error: {str(e)}"
            return state

    def analyze_resume_node(self, state: ATSState) -> ATSState:
        try:
            analysis = self.resume_agent.analyze_resume(state["parsed_resume"])
            qualifications = self.resume_agent.extract_key_qualifications(
                state["parsed_resume"]
            )
            state["resume_analysis"] = {
                "analysis": analysis,
                "qualifications": qualifications
            }
            return state
        except Exception as e:
            state["error"] = f"Resume analysis error: {str(e)}"
            return state

    def analyze_job_node(self, state: ATSState) -> ATSState:
        try:
            analysis = self.job_agent.analyze_job_requirements(state["parsed_job"])
            deal_breakers = self.job_agent.identify_deal_breakers(state["parsed_job"])
            state["job_analysis"] = {
                "analysis": analysis,
                "deal_breakers": deal_breakers
            }
            return state
        except Exception as e:
            state["error"] = f"Job analysis error: {str(e)}"
            return state

    def calculate_match_node(self, state: ATSState) -> ATSState:
        try:
            match_score = self.matching_agent.calculate_match_score(
                state["parsed_resume"],
                state["parsed_job"],
                state["resume_analysis"],
                state["job_analysis"]
            )
            gap_analysis = self.matching_agent.identify_gaps(
                state["parsed_resume"],
                state["parsed_job"]
            )
            state["match_score"] = match_score
            state["gap_analysis"] = gap_analysis
            return state
        except Exception as e:
            state["error"] = f"Matching error: {str(e)}"
            return state

    def generate_recommendation_node(self, state: ATSState) -> ATSState:
        try:
            recommendation = self.recommendation_agent.generate_recommendation(
                state["parsed_resume"],
                state["parsed_job"],
                state["match_score"],
                state["gap_analysis"]
            )
            interview_questions = self.recommendation_agent.generate_interview_questions(
                state["parsed_resume"],
                state["parsed_job"],
                state["gap_analysis"]
            )
            state["recommendation"] = recommendation
            state["interview_questions"] = interview_questions
            return state
        except Exception as e:
            state["error"] = f"Recommendation error: {str(e)}"
            return state

    def compile_final_evaluation_node(self, state: ATSState) -> ATSState:
        state["final_evaluation"] = {
            "candidate": state["parsed_resume"].get("candidate", {}),
            "job": {
                "job_id": state["parsed_job"].get("job_id"),
                "title": state["parsed_job"].get("title"),
                "company": state["parsed_job"].get("company")
            },
            "scores": state["match_score"],
            "gaps": state["gap_analysis"],
            "recommendation": state["recommendation"],
            "interview_questions": state["interview_questions"],
            "resume_analysis": state["resume_analysis"],
            "job_analysis": state["job_analysis"]
        }
        return state

    def should_continue(self, state: ATSState) -> str:
        if state.get("error"):
            return "error"
        return "continue"


def create_ats_graph() -> StateGraph:
    ats = ATSGraph()

    workflow = StateGraph(ATSState)

    workflow.add_node("parse_resume", ats.parse_resume_node)
    workflow.add_node("parse_job", ats.parse_job_node)
    workflow.add_node("analyze_resume", ats.analyze_resume_node)
    workflow.add_node("analyze_job", ats.analyze_job_node)
    workflow.add_node("calculate_match", ats.calculate_match_node)
    workflow.add_node("generate_recommendation", ats.generate_recommendation_node)
    workflow.add_node("compile_evaluation", ats.compile_final_evaluation_node)

    workflow.set_entry_point("parse_resume")

    workflow.add_edge("parse_resume", "parse_job")
    workflow.add_edge("parse_job", "analyze_resume")
    workflow.add_edge("analyze_resume", "analyze_job")
    workflow.add_edge("analyze_job", "calculate_match")
    workflow.add_edge("calculate_match", "generate_recommendation")
    workflow.add_edge("generate_recommendation", "compile_evaluation")
    workflow.add_edge("compile_evaluation", END)

    return workflow.compile()
