# LLM Failure & Reliability Analyzer — Master Checklist

## 0. Repository & Project Setup (FOUNDATION)
- [ ] Create GitHub repo with clear name
- [ ] Add .gitignore (Python, venv, logs, DB files)
- [ ] Add LICENSE (MIT is fine)
- [ ] Add .env.example
- [ ] Repo structure
- [ ] Pin dependencies
- [ ] Add logging config
- [ ] Add UUID-based run IDs

## 1. Test Case Specification (CRITICAL)
- [ ] TestCase schema (YAML or JSON)
- [ ] Loader (Load folder, validate schema, fail fast)

## 2. Execution Engine (CORE LOGIC)
- [ ] Runner (Accept model/suite, execute, store results)
- [ ] Retry logic & error handling

## 3. Rule-Based Evaluators (MUST HAVE)
- [ ] Format Validator (JSON, Schema)
- [ ] Instruction Compliance (Limits, phrases, refusal)
- [ ] Latency Evaluator (Stats, flag slow tests)

## 4. LLM-as-Judge Evaluators (HIGH SIGNAL)
- [ ] Judge Prompt (Rubric, JSON output)
- [ ] Judge Metrics (Grounding, Hallucination, Completeness)
- [ ] Enforcement

## 5. Prompt Sensitivity Analyzer (DIFFERENTIATOR)
- [ ] Perturbation Engine (Rephrase, Reorder, Noise)
- [ ] Stability Metrics
- [ ] Sensitivity Scoring

## 6. Storage & Persistence
- [ ] Database (SQLite)
- [ ] Stored fields (Run data, stats)

## 7. FastAPI Service Layer
- [ ] Endpoints (Runs CRUD, Listeners)
- [ ] API Quality (Schemas, Validation)

## 8. Streamlit Dashboard (RECRUITER-VISIBLE)
- [ ] Summary View
- [ ] Detail View
- [ ] Regression View

## 9. CI / GitHub Actions (INTERVIEW GOLD)
- [ ] CI Pipeline (Smoke test, thresholds, reporting)

## 10. Test Data Requirements
- [ ] 50–100 tests minimum (Categories)

## 11. Documentation (NON-NEGOTIABLE)
- [ ] Required docs (Architecture, Evaluators, Scoring)
- [ ] README (Problem, Features, Demo)

## 12. Demo Readiness
- [ ] Comparisons, Failures, Regressions
