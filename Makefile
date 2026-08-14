.PHONY: install format lint fix check assignment_1 clean

# Install dependencies
install:
	pip install -r requirements.txt


# Format code using Ruff
format:
	ruff format .


# Lint code
lint:
	ruff check .


# Auto-fix lint issues
fix:
	ruff check . --fix


# Run formatting + lint fixes
check: fix format


# Run individual assignment_1 components
assignment_1:
	python -m src.assignment1_async_dataclass_pydantic.part_1
	python -m src.assignment1_async_dataclass_pydantic.part_2
    python -m src.assignment1_async_dataclass_pydantic.part_3
	python -m src.assignment1_async_dataclass_pydantic.part_4
	python -m src.assignment1_async_dataclass_pydantic.part_5
	python -m src.assignment1_async_dataclass_pydantic.part_5_2
# Remove Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete