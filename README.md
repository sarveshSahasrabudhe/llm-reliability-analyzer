# LLM Reliability Analyzer 🔬

> **Turn prompt engineering from alchemy into engineering.**
> A comprehensive platform for semantic evaluation, robustness testing, and regression detection of Large Language Models.


## 📖 Documentation
- **[Walkthrough (Day-by-Day Log)](docs/WALKTHROUGH.md)**: Steps we took from Day 1 to Day 11.
- **[Project Overview](docs/PROJECT_OVERVIEW.md)**: Why we built this and our philosophy.
- **[Tech Stack](docs/TECH_STACK.md)**: Detailed breakdown of technologies used.

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker (optional)
- Groq API Key (for LLM inference)

### Installation
```bash
# 1. Clone the repo
git clone https://github.com/sarveshSahasrabudhe/llm-reliability-analyzer.git
cd llm-reliability-analyzer

# 2. Install dependencies (uv recommended)
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env and add your GROQ_API_KEY
```


### Running with Docker (Recommended)
```bash
# Start both API and Dashboard
docker-compose up --build

# Access:
# - Dashboard: http://localhost:8501
# - API Docs:  http://localhost:8000/docs
```

### Running Manually (Local)
```bash
# Start the Dashboard
streamlit run ui/dashboard.py

# Run the Test Suite (CLI)
python scripts/trigger_full_run.py
```

## ✨ Key Features
- **30+ Automated Tests**: Covering JSON extraction, Grounding, Refusal, and more.
- **LLM-as-a-Judge**: Semantic evaluation for complex outputs.
- **Prompt Sensitivity Engine**: Tests robustness against rephrasing and noise.
- **Regression Comparison**: Side-by-side run analysis to catch bugs.
- **CI/CD Pipeline**: GitHub Actions integration for automated verification.

## 📂 Project Structure
- `app/`: FastAPI backend service
- `ui/`: Streamlit dashboard
- `evaluator/`: Core logic (LLM clients, judges, perturbations)
- `datasets/`: Test cases in JSON/YAML
- `scripts/`: Utility scripts for maintenance

---
