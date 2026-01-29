# LLM Reliability Analyzer Tech Stack

## Core Technologies
| Component | Technology | Reasoning |
|-----------|------------|-----------|
| **Language** | Python 3.12 | Modern type hinting, performance improvements, and rich AI ecosystem. |
| **API Framework** | FastAPI | High performance, automatic Swagger documentation, and async support. |
| **Frontend** | Streamlit | Rapid prototyping for data apps; perfect for visualizing test results. |
| **Package Management** | uv | Extremely fast pip alternative for dependency resolution. |

## AI & Evaluation
| Component | Technology | Reasoning |
|-----------|------------|-----------|
| **LLM Provider** | Groq (Llama 3.3) | Blazing fast inference (essential for running 30+ tests quickly). |
| **Pydantic** | Pydantic V2 | Robust data validation for LLM outputs and JSON schemas. |
| **Embeddings** | Sentence Transformers | Local, efficient semantic similarity calculation (`all-MiniLM-L6-v2`). |
| **LLM Judge** | Custom Implementation | Using LLM-as-a-Judge pattern for semantic scoring (Grounding/Hallucination). |

## Data & Persistence
| Component | Technology | Reasoning |
|-----------|------------|-----------|
| **Database** | SQLite | Lightweight, file-based, zero configuration needed for local development. |
| **ORM** | SQLAlchemy | Robust object-relational mapping for Python. |

## Testing & CI/CD
| Component | Technology | Reasoning |
|-----------|------------|-----------|
| **Test Framework** | Custom Runner | Specialized async runner with rate limiting and retry logic. |
| **CI/CD** | GitHub Actions | Automated workflow for smoke testing on every push. |
| **Containerization** | Docker | Consistent deployment environment across machines. |

## Project Structure
```
llm-reliability-analyzer/
├── app/                  # FastAPI Application
├── datasets/             # Test Cases (JSON/YAML)
├── db/                   # Database Models & Session
├── docs/                 # Documentation
├── evaluator/            # Core Evaluation Logic
├── metrics/              # Metric Calculations (Latency, Similarity)
├── scripts/              # Utility Scripts
├── ui/                   # Streamlit Dashboard
└── tests/                # Unit Tests
```
