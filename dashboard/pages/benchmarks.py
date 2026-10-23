import streamlit as st
import pandas as pd
from finbench.database import SessionLocal, BenchmarkQuestion, BenchmarkAnswer
from finbench.benchmarks.generator import generate_retired_question_registry

st.set_page_config(page_title="Benchmark Explorer — FinBench", layout="wide")
st.title("🎯 Page 4: AI Benchmark Explorer (100 Questions)")

with SessionLocal() as session:
    questions = session.query(BenchmarkQuestion, BenchmarkAnswer).outerjoin(
        BenchmarkAnswer, BenchmarkQuestion.id == BenchmarkAnswer.question_id
    ).all()

df_bq = pd.DataFrame([
    {
        "ID": bq.id,
        "Category": bq.category,
        "Difficulty": bq.difficulty,
        "Question": bq.question,
        "Method": bq.evaluation_method,
        "Freshness": bq.freshness_category,
        "Expected Answer": ba.expected_answer if ba else None,
        "Status": bq.status,
    }
    for bq, ba in questions
])

col_filter1, col_filter2 = st.columns(2)
with col_filter1:
    cat_filter = st.multiselect("Filter by Category:", options=df_bq["Category"].unique(), default=df_bq["Category"].unique())
with col_filter2:
    diff_filter = st.multiselect("Filter by Difficulty:", options=df_bq["Difficulty"].unique(), default=df_bq["Difficulty"].unique())

filtered = df_bq[df_bq["Category"].isin(cat_filter) & df_bq["Difficulty"].isin(diff_filter)]
st.metric("Displayed Benchmarks", f"{len(filtered)} / {len(df_bq)}")
st.dataframe(filtered, use_container_width=True, height=450)

st.divider()

# Retired Question Registry Section
st.subheader("🏛️ Retired Question Registry (Feature A Governance)")
retired = generate_retired_question_registry()
st.table(pd.DataFrame(retired))
