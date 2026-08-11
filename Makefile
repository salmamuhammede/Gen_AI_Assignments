.PHONY: install format lint fix check run clean

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


# Run individual LLM components
assignment_1:
	python -m src.assignment1_async_dataclass_pydantic.part_1
	python -m src.
	python -m src.llm.explainer
	python -m src.llm.generator
	python -m src.llm.relevance_checker

# Run individual services components
services:
	python -m src.services.assistant
	python -m src.services.router

# Run individual data processing components	
data_processing:
	python -m src.data_processing.processor

# Run individual code tool components	
tools:
	python -m src.tools.code_runner

# Run individual feedback components	
feedback:
	python -m src.feedback.learner

# Run individual conversation memory components	
memory:
	python -m src.memory.conversation_memory

# Run individual CRAG components	
crag:
	python -m src.rag.ingestion.loader
	python -m src.rag.ingestion.chunker
	python -m src.rag.ingestion.embeddings
	python -m src.rag.ingestion.ingest
	python -m src.rag.ingestion.download_dataset
	python -m src.rag.ingestion.vector_db
	python -m src.rag.retrieval.retriever

backend:
	uvicorn src.api.main:app --reload
	uvicorn src.api.main:app 

ui:
	python -m streamlit run src/ui/app.py

# Remove Python cache files
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete