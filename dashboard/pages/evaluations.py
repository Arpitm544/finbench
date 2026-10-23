import streamlit as st
import pandas as pd
import plotly.express as px
from finbench.database import SessionLocal, EvaluationRun, EvaluationResult
from finbench.evaluation.runner import BenchmarkEvaluationRunner

st.set_page_config(page_title="AI Evaluation — FinBench", layout="wide")
st.title("🤖 Page 5: AI Model Evaluation & Leaderboard")

with SessionLocal() as session:
    eval_runs = session.query(EvaluationRun).order_by(EvaluationRun.created_at.desc()).all()

col_btn, col_select = st.columns([1, 2])
with col_select:
    target_model = st.selectbox(
        "Select Model Persona to Evaluate:",
        options=["finbench-expert-v1", "finbench-standard-llm", "naive-heuristic-llm"],
    )

with col_btn:
    if st.button("🚀 Trigger Full 100-Question Evaluation Run"):
        with st.spinner(f"Evaluating {target_model} across all 100 benchmark questions..."):
            runner = BenchmarkEvaluationRunner()
            res = runner.run_evaluation(model_name=target_model, persist=True)
            runner.close()
            st.success(f"Evaluation Completed! Accuracy: {res['accuracy_percentage']}% | Latency: {res['average_latency_ms']}ms")
            st.rerun()

st.divider()

if eval_runs:
    st.subheader("Model Evaluation History & Leaderboard")
    df_runs = pd.DataFrame([
        {
            "Run ID": r.id,
            "Model Name": r.model_name,
            "Accuracy (%)": r.accuracy_percentage,
            "Passed": f"{r.passed_questions}/{r.total_questions}",
            "Avg Latency (ms)": r.average_latency_ms,
            "Duration (s)": r.total_duration_seconds,
            "Date": r.created_at.strftime("%Y-%m-%d %H:%M"),
        }
        for r in eval_runs
    ])
    st.dataframe(df_runs, use_container_width=True)

    # Latest run category breakdown
    latest_run = eval_runs[0]
    st.subheader(f"Category Breakdown for Latest Run: {latest_run.model_name}")
    cat_scores = latest_run.category_scores or {}
    if cat_scores:
        df_cat = pd.DataFrame([
            {"Category": k.replace("_", " ").title(), "Accuracy (%)": v["accuracy_pct"], "Passed": f"{v['passed']}/{v['total']}"}
            for k, v in cat_scores.items()
        ])
        fig_cat = px.bar(
            df_cat,
            x="Category",
            y="Accuracy (%)",
            color="Category",
            text_auto=".1f",
            title="Accuracy by Analytical Category",
        )
        st.plotly_chart(fig_cat, use_container_width=True)
else:
    st.info("No AI evaluation runs recorded yet. Click 'Trigger Full 100-Question Evaluation Run' above to launch.")
