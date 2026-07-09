from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate


class RecommendationAgent:
    def __init__(self, model: str = "gpt-4o"):
        self.llm = ChatOpenAI(model=model, temperature=0.3)

    def generate_recommendation(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        match_score: Dict[str, Any],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert hiring manager providing final recommendations.
            Based on all the analysis, provide:
            1. Clear hire/no-hire/maybe recommendation with reasoning
            2. Key strengths that make this candidate suitable
            3. Key concerns or weaknesses
            4. Interview focus areas
            5. Next steps in the hiring process

            Return JSON format:
            {{
                "recommendation": "strong_yes/yes/maybe/no/strong_no",
                "confidence_level": "high/medium/low",
                "reasoning": "detailed paragraph explaining the recommendation",
                "strengths": ["list of key strengths"],
                "weaknesses": ["list of key weaknesses"],
                "interview_focus_areas": ["list of areas to probe in interview"],
                "next_steps": ["list of recommended next steps"],
                "risk_factors": ["list of potential risks"],
                "deal_breaker_assessment": "string - whether any deal-breakers exist",
                "alternative_roles": ["list of potentially better-fit roles if not perfect for this one"]
            }}
            """),
            ("user", """
            Candidate Resume:
            {resume_data}

            Job Requirements:
            {job_data}

            Match Score:
            {match_score}

            Gap Analysis:
            {gap_analysis}
            """)
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "resume_data": str(resume_data),
            "job_data": str(job_data),
            "match_score": str(match_score),
            "gap_analysis": str(gap_analysis)
        })

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to generate recommendation",
                "response": response.content
            }

    def generate_interview_questions(
        self,
        resume_data: Dict[str, Any],
        job_data: Dict[str, Any],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate tailored interview questions based on the candidate's profile and job requirements.
            Create questions that:
            - Probe areas of concern or gaps
            - Verify claimed skills and experience
            - Assess cultural fit
            - Evaluate problem-solving abilities

            Return JSON format:
            {{
                "technical_questions": [
                    {{"question": "string", "purpose": "what you're assessing", "follow_ups": ["list"]}}
                ],
                "behavioral_questions": [
                    {{"question": "string", "purpose": "string", "red_flags_to_watch": ["list"]}}
                ],
                "situational_questions": ["list"],
                "questions_about_gaps": [
                    {{"gap": "string", "question": "string"}}
                ]
            }}
            """),
            ("user", "Resume:\n{resume}\n\nJob:\n{job}\n\nGaps:\n{gaps}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({
            "resume": str(resume_data),
            "job": str(job_data),
            "gaps": str(gap_analysis)
        })

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to generate interview questions",
                "response": response.content
            }
