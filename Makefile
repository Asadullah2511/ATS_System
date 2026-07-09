.PHONY: install test run api clean format lint help

help:
	@echo "Available commands:"
	@echo "  make install    - Install dependencies"
	@echo "  make test       - Run tests"
	@echo "  make run        - Run CLI application"
	@echo "  make api        - Start FastAPI server"
	@echo "  make example    - Run example script"
	@echo "  make format     - Format code with black"
	@echo "  make lint       - Run linters"
	@echo "  make clean      - Clean up generated files"

install:
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=src

run:
	python main.py

api:
	uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

example:
	python example.py

format:
	black src/ tests/ main.py example.py

lint:
	flake8 src/ tests/ --max-line-length=100
	mypy src/ --ignore-missing-imports

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf build/ dist/
