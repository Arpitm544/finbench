import streamlit as st
import pandas as pd
import plotly.express as px
from finbench.database import SessionLocal, Transaction, BenchmarkQuestion, EvaluationRun, ModelTrainingRun
from finbench.analytics.transactions import TransactionAnalyticsEngine
from finbench.analytics.fraud import FraudAnalyticsEngine

st.set_page_config(
    page_title="FinBench — Financial Risk & AI Benchmark Evaluation",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("🏦 FinBench: Financial Risk Analytics & AI Benchmark Evaluation")
st.markdown(
    """
    **FinBench** is an enterprise financial risk platform that processes millions of transactions, detects fraud patterns, 
    and systematically evaluates how accurately artificial intelligence models solve complex financial problems.
    """
)

# Fetch high level overview stats
with SessionLocal() as session:
    tx_eng = TransactionAnalyticsEngine(session)
    fraud_eng = FraudAnalyticsEngine(session)
    tx_stats = tx_eng.get_summary_metrics()
    fraud_stats = fraud_eng.get_overall_fraud_metrics()
    total_benchmarks = session.query(BenchmarkQuestion).count()
    verified_benchmarks = session.query(BenchmarkQuestion).filter(BenchmarkQuestion.status == "verified").count()
    total_eval_runs = session.query(EvaluationRun).count()

# Key metrics row
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Total Transactions", f"{tx_stats['total_transactions']:,}")
col2.metric("Gross Volume", f"${tx_stats['total_transaction_amount']:,.0f}")
col3.metric("Network Fraud Rate", f"{fraud_stats['overall_fraud_rate_percentage']:.4f}%", f"{fraud_stats['fraud_rate_basis_points']} bps")
col4.metric("Verified Benchmarks", f"{verified_benchmarks}/{total_benchmarks}")
col5.metric("Evaluation Sessions", f"{total_eval_runs}")

st.divider()

# System Architecture & Navigation Guide
st.subheader("System Architecture & Analytics Flow")
st.markdown(
    """
    ```
    PaySim Dataset ──► Chunk Ingestion ──► PostgreSQL / SQLite ──► Financial Risk Analytics
                                                                         │
    AI Evaluation Dashboard ◄── Scoring Engine ◄── Model Client ◄── 100 AI Benchmarks
    ```
    """
)

col_left, col_right = st.columns(2)

with col_left:
    st.info("### 📊 Financial & Fraud Analytics Modules")
    st.markdown(
        """
        - **Overview:** High-level liquidity, payment channel distribution, and temporal activity.
        - **Transaction Analytics:** Value percentiles, heavy-tail skewness, and account velocity.
        - **Fraud & ML Detection:** Logistic Regression, Random Forest, and LightGBM models with operational cost optimization.
        """
    )

with col_right:
    st.success("### 🧠 AI Benchmark Evaluation System")
    st.markdown(
        """
        - **Benchmark Explorer:** 100 verified questions across Advanced SQL, Financial Statistics, Risk Assessment, and Contradictory Evidence.
        - **AI Evaluation Engine:** Multi-method scoring (numeric tolerance, rubric evaluation, and contradictory business advice).
        - **Governance:** Retired Question Registry & Freshness-aware categorization.
        """
    )
