# FinBench — Financial Risk Analytics & AI Benchmark Evaluation System

[![CI Pipeline](https://github.com/Arpitm544/finbench/actions/workflows/ci.yml/badge.svg)](https://github.com/Arpitm544/finbench/actions)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**FinBench** is an enterprise-grade financial risk analytics platform and AI benchmark evaluation system. It processes millions of mobile financial transactions (PaySim schema), detects fraud patterns, performs statistical hypothesis testing, and evaluates how accurately artificial intelligence models solve complex financial analytics problems.

---

## 1. System Architecture

```
                       FINBENCH
                          |
                 Financial Dataset (~6.36M Records)
                          |
                   Data Ingestion (Polars / Chunks)
                          |
                  Data Validation & Quality Engine
                          |
               PostgreSQL / SQLite Database
                          |
                  Analytics Engine
                    /          \
              SQL Analytics   Python Statistical Engine
                    \          /
                   Risk Analysis
                          |
                 Fraud Detection ML (LR, RF, LightGBM)
                          |
                 Benchmark Generator (100 Questions)
                          |
                Ground Truth Engine (SQL + Python Verified)
                          |
                 Benchmark Database
                          |
                  AI Model Runner (OpenAI Compatible)
                          |
                  Scoring Engine (Multi-Method)
                          |
                 Evaluation Results & Leaderboards
                          |
                    FastAPI Backend
                          |
               Streamlit Analytics Dashboard
```

---

## 2. Key Capabilities

- **Large-Scale Transaction Analytics**: Chunked and vector-accelerated processing of millions of transactions using Polars, Pandas, and SQL.
- **Statistical & Financial Reasoning**: Confidence intervals, two-sample t-tests, Mann-Whitney U tests, Chi-Square independence tests, Cohen's d effect sizes, and cost-benefit trade-offs.
- **Fraud Detection ML**: Leakage-free feature engineering, time-aware validation splits, and comparative modeling with Logistic Regression, Random Forest, and LightGBM.
- **100 Verified AI Benchmark Questions**: Spanning 7 analytical categories with independently verified ground truth (SQL and Python dual-verification).
- **Advanced Benchmark Governance**:
  - *Retired Question Registry & Data Owner Questionnaire*
  - *Freshness-Aware Categorization* (Static, Slowly Changing, Frequently Changing, Live-dependent)
  - *Contradictory Business Advice Evaluation* (Evaluating whether AI models adapt thresholds to changing unit economics rather than defaulting to generic advice).
- **Interactive Full-Stack Platform**: High-performance FastAPI REST API and 5-page Streamlit dashboard.

---

## 3. Quickstart

### Prerequisites
- Python 3.11+ (Python 3.12 recommended)
- `uv` (recommended) or `pip`
- Docker & Docker Compose (optional for PostgreSQL)

### Local Setup
```bash
git clone https://github.com/Arpitm544/finbench.git
cd finbench

# Setup virtual environment
uv venv --python 3.12
source .venv/bin/activate
uv pip install -e .

# Run Tests
pytest -v
```
