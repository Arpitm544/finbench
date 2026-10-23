import streamlit as st
import pandas as pd
import plotly.express as px
from finbench.database import SessionLocal, ModelTrainingRun
from finbench.analytics.fraud import FraudAnalyticsEngine

st.set_page_config(page_title="Fraud Detection & ML — FinBench", layout="wide")
st.title("🛡️ Page 3: Fraud Detection & Machine Learning Comparison")

with SessionLocal() as session:
    fraud_eng = FraudAnalyticsEngine(session)
    fraud_summary = fraud_eng.get_overall_fraud_metrics()
    by_channel = fraud_eng.get_fraud_rate_by_type()
    
    # Query model training runs
    model_runs = session.query(ModelTrainingRun).all()

# Headline metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Confirmed Fraud Cases", f"{fraud_summary['fraud_transactions_count']:,}")
c2.metric("Total Fraud Losses", f"${fraud_summary['total_fraud_loss_amount']:,.2f}")
c3.metric("Network Fraud Rate", f"{fraud_summary['overall_fraud_rate_percentage']:.4f}%")
c4.metric("Average Fraud Amount", f"${fraud_summary['average_fraud_amount']:,.2f}")

st.divider()

st.subheader("Fraud Incident Prevalence by Channel")
df_fraud_channel = pd.DataFrame(by_channel)
fig_bar = px.bar(
    df_fraud_channel,
    x="type",
    y="fraud_rate_pct",
    color="type",
    text_auto=".3f",
    title="Fraud Incident Rate (%) Across Payment Types",
    labels={"fraud_rate_pct": "Fraud Rate (%)", "type": "Channel"},
)
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Machine Learning Model Benchmark Comparison")
if model_runs:
    df_models = pd.DataFrame([
        {
            "Model Name": r.model_name.replace("_", " ").title(),
            "Precision": r.precision,
            "Recall": r.recall,
            "F1-Score": r.f1_score,
            "PR-AUC (Key)": r.pr_auc,
            "ROC-AUC": r.roc_auc,
            "Expected Cost ($)": r.expected_cost,
            "Duration (s)": r.training_duration_seconds,
        }
        for r in model_runs
    ])
    st.dataframe(df_models, use_container_width=True)

    fig_cmp = px.bar(
        df_models,
        x="Model Name",
        y="PR-AUC (Key)",
        color="Model Name",
        text_auto=".4f",
        title="Rare-Event Classification Performance (PR-AUC)",
    )
    st.plotly_chart(fig_cmp, use_container_width=True)
else:
    st.info("No trained models recorded in database yet.")
