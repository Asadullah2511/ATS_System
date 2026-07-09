from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from src.models.resume import Resume


class ResumeAnalysisAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.llm = ChatOpenAI(model=model, temperature=0)
        self.parser = JsonOutputParser(pydantic_object=Resume)

    def analyze_resume(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume analyst. Analyze the provided resume data and provide:
            1. Key strengths and qualifications
            2. Areas for improvement
            3. Career level assessment
            4. Notable achievements
            5. Potential red flags or concerns

            Return a detailed analysis as JSON with these fields:
            {{
                "career_level": "entry/mid/senior/executive",
                "strengths": ["list of strengths"],
                "improvements": ["list of improvement areas"],
                "achievements": ["list of key achievements"],
                "concerns": ["list of concerns or red flags"],
                "summary": "overall assessment paragraph"
            }}
            """),
            ("user", "Resume data:\n\n{resume_data}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"resume_data": str(resume_data)})

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to analyze resume",
                "response": response.content
            }

    def extract_key_qualifications(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Extract and summarize key qualifications from the resume.
            Focus on:
            - Years of experience per skill/technology
            - Leadership experience
            - Team size managed
            - Notable companies or projects
            - Unique qualifications

            Return JSON format:
            {{
                "total_experience_years": "float",
                "leadership_experience": "boolean",
                "team_sizes_managed": ["list"],
                "notable_companies": ["list"],
                "unique_qualifications": ["list"],
                "specializations": ["list"]
            }}
            """),
            ("user", "Resume data:\n\n{resume_data}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"resume_data": str(resume_data)})

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to extract qualifications",
                "response": response.content
            }
