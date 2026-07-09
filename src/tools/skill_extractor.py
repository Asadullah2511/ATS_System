from typing import Dict, Any, List
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field


class SkillExtractorTool(BaseTool):
    name: str = "skill_extractor"
    description: str = "Extracts and categorizes skills from text with proficiency levels"
    llm: Any = Field(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.llm is None:
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _run(self, text: str) -> Dict[str, Any]:
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at extracting and categorizing technical and soft skills.
            Analyze the text and extract skills grouped by category.

            Return a JSON object with:
            {{
                "technical_skills": [
                    {{
                        "name": "skill name",
                        "category": "programming/framework/database/cloud/devops/etc",
                        "proficiency": "beginner/intermediate/advanced/expert or null",
                        "years_of_experience": "float or null"
                    }}
                ],
                "soft_skills": ["list of soft skills"],
                "tools_and_technologies": ["list of tools"],
                "domains": ["list of domain expertise areas"]
            }}
            """),
            ("user", "Text to analyze:\n\n{text}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"text": text})

        import json
        try:
            return json.loads(response.content)
        except json.JSONDecodeError:
            return {
                "error": "Failed to extract skills",
                "response": response.content
            }
