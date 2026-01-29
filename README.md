# LLM Failure & Reliability Analyzer

A production-minded system that evaluates LLM reliability across hallucination risk, grounding, instruction compliance, format correctness, prompt sensitivity, and latency — with regression tracking and CI integration.

## Features
- **Test Case Management**: Schema-based test definitions.
- **Execution Engine**: Sequential/concurrent test running with retry logic.
- **Rule-Based Evaluation**: JSON validation, instruction compliance, latency tracking.
- **LLM-as-Judge**: Qualitative evaluation using model-based grading.
- **Prompt Sensitivity**: perturbation analysis for stability checking.
- **Dashboard**: Streamlit-based visualization of results and regressions.
- **CI/CD Integration**: Automated reliability checks.

## Setup
1. Clone the repository.
2. Install `uv` if not already installed.
3. specificy the python version: `uv python install 3.12`
4. Create a virtual environment: `uv venv`
5. Activate the environment: `source .venv/bin/activate`
6. Install dependencies: `uv pip install -r requirements.txt`
7. Ensure Ollama is running and pull the model: `ollama pull llama3`
8. Copy `.env.example` to `.env`.

## Running
- **First Run (Smoke Test)**: `python -m evaluator.run_suite`
- **API**: `uvicorn app.main:app --reload`
- **Dashboard**: `streamlit run ui/dashboard.py`
