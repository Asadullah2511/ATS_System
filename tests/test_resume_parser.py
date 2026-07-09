import pytest
from pathlib import Path
from src.tools.resume_parser import ResumeParserTool


@pytest.fixture
def resume_parser():
    return ResumeParserTool()


@pytest.fixture
def sample_resume_text(tmp_path):
    content = """
    John Doe
    john.doe@email.com
    (555) 123-4567

    EXPERIENCE
    Senior Software Engineer at Tech Corp (2020-Present)
    - Led development of microservices
    - Managed team of 5 engineers

    EDUCATION
    BS Computer Science, University of Technology (2017)

    SKILLS
    Python, Django, React, AWS, Docker
    """

    file_path = tmp_path / "test_resume.txt"
    file_path.write_text(content)
    return str(file_path)


def test_resume_parser_extracts_text(resume_parser, sample_resume_text):
    text = resume_parser._extract_text(sample_resume_text)
    assert "John Doe" in text
    assert "john.doe@email.com" in text
    assert "Tech Corp" in text


def test_resume_parser_handles_invalid_file(resume_parser):
    with pytest.raises(FileNotFoundError):
        resume_parser._extract_text("nonexistent_file.txt")


def test_resume_parser_unsupported_format(resume_parser, tmp_path):
    file_path = tmp_path / "test.invalid"
    file_path.write_text("content")

    with pytest.raises(ValueError, match="Unsupported file format"):
        resume_parser._extract_text(str(file_path))
