from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ats-system",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Applicant Tracking System powered by LangGraph and LangChain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ats-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.9",
    install_requires=[
        "langgraph>=0.2.0",
        "langchain>=0.3.0",
        "langchain-openai>=0.2.0",
        "langchain-anthropic>=0.2.0",
        "langchain-community>=0.3.0",
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pypdf>=5.0.0",
        "python-docx>=1.0.0",
        "pandas>=2.0.0",
        "fastapi>=0.100.0",
        "uvicorn>=0.30.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.13.0",
        "redis>=5.0.0",
        "celery>=5.4.0",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-asyncio>=0.23.0",
            "black>=24.0.0",
            "flake8>=7.0.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "ats-system=main:main",
        ],
    },
)
