import streamlit as st
import pandas as pd
import plotly.express as px
from finbench.database import SessionLocal, Transaction
from finbench.analytics.transactions import TransactionAnalyticsEngine

st.set_page_config(page_title="Transaction Analytics — FinBench", layout="wide")
st.title("💳 Page 2: Transaction Analytics & Tail Analysis")

with SessionLocal() as session:
    tx_eng = TransactionAnalyticsEngine(session)
    percentiles = tx_eng.get_high_value_percentiles()
    
    # Query sample transactions for interactive table
    sample_txs = session.query(
        Transaction.transaction_id,
        Transaction.step,
        Transaction.type,
        Transaction.amount,
        Transaction.name_orig,
        Transaction.oldbalance_org,
        Transaction.newbalance_orig,
        Transaction.name_dest,
        Transaction.is_fraud,
    ).limit(500).all()

p = percentiles.get("percentiles", {})
c1, c2, c3, c4 = st.columns(4)
c1.metric("50th Percentile (P50)", f"${p.get('p50', 0):,.2f}")
c2.metric("90th Percentile (P90)", f"${p.get('p90', 0):,.2f}")
c3.metric("99th Percentile (P99)", f"${p.get('p99', 0):,.2f}")
c4.metric("P99 Volume Share", f"{percentiles.get('p99_share_of_total_value_pct', 0)}%")

st.divider()

st.subheader("Interactive Transaction Explorer")
df_tx = pd.DataFrame([dict(r._mapping) for r in sample_txs])

filter_channel = st.multiselect(
    "Filter by Payment Channel:",
    options=df_tx["type"].unique(),
    default=df_tx["type"].unique(),
)

df_filtered = df_tx[df_tx["type"].isin(filter_channel)]
st.dataframe(df_filtered, use_container_width=True, height=400)

st.subheader("Transaction Amount Distribution (Log Scaled)")
fig_hist = px.histogram(
    df_filtered,
    x="amount",
    color="type",
    nbins=50,
    log_x=True,
    title="Log-Scale Monetary Size by Type",
    labels={"amount": "Amount ($ Log Scale)"},
)
st.plotly_chart(fig_hist, use_container_width=True)
