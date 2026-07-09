from typing import Dict, Any
from langchain_core.tools import BaseTool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import Field
import pypdf
import docx
import os


class ResumeParserTool(BaseTool):
    name: str = "resume_parser"
    description: str = "Parses resume files (PDF, DOCX, TXT) and extracts structured information"
    llm: Any = Field(default=None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.llm is None:
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    def _run(self, file_path: str) -> Dict[str, Any]:
        text = self._extract_text(file_path)

        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert resume parser. Extract structured information from the resume text.
            Return a JSON object with the following structure:
            {{
                "candidate": {{
                    "name": "string",
                    "email": "string",
                    "phone": "string or null",
                    "location": "string or null",
                    "linkedin": "string or null",
                    "github": "string or null"
                }},
                "summary": "string or null",
                "experience": [
                    {{
                        "company": "string",
                        "title": "string",
                        "start_date": "YYYY-MM or null",
                        "end_date": "YYYY-MM or null",
                        "description": "string",
                        "responsibilities": ["list of strings"],
                        "achievements": ["list of strings"]
                    }}
                ],
                "education": [
                    {{
                        "institution": "string",
                        "degree": "string",
                        "field_of_study": "string or null",
                        "start_date": "YYYY-MM or null",
                        "end_date": "YYYY-MM or null",
                        "gpa": "float or null"
                    }}
                ],
                "skills": [
                    {{
                        "name": "string",
                        "proficiency": "string or null",
                        "years_of_experience": "float or null"
                    }}
                ],
                "certifications": ["list of strings"],
                "languages": ["list of strings"]
            }}
            """),
            ("user", "Resume text:\n\n{text}")
        ])

        chain = prompt | self.llm
        response = chain.invoke({"text": text})

        import json
        try:
            parsed_data = json.loads(response.content)
            parsed_data["raw_text"] = text
            return parsed_data
        except json.JSONDecodeError:
            return {
                "error": "Failed to parse resume",
                "raw_text": text,
                "response": response.content
            }

    def _extract_text(self, file_path: str) -> str:
        ext = os.path.splitext(file_path)[1].lower()

        if ext == '.pdf':
            return self._extract_pdf(file_path)
        elif ext == '.docx':
            return self._extract_docx(file_path)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def _extract_pdf(self, file_path: str) -> str:
        reader = pypdf.PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def _extract_docx(self, file_path: str) -> str:
        doc = docx.Document(file_path)
        return "\n".join([paragraph.text for paragraph in doc.paragraphs])
