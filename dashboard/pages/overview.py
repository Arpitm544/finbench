import streamlit as st
import pandas as pd
import plotly.express as px
from finbench.database import SessionLocal
from finbench.analytics.transactions import TransactionAnalyticsEngine
from finbench.analytics.fraud import FraudAnalyticsEngine

st.set_page_config(page_title="Financial Overview — FinBench", layout="wide")
st.title("📈 Page 1: Financial Overview")

with SessionLocal() as session:
    tx_eng = TransactionAnalyticsEngine(session)
    fraud_eng = FraudAnalyticsEngine(session)
    
    summary = tx_eng.get_summary_metrics()
    by_channel = tx_eng.get_volume_by_type()
    trends = tx_eng.get_time_series_trends()

# Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Transaction Volume", f"{summary['total_transactions']:,}")
c2.metric("Total Value", f"${summary['total_transaction_amount']:,.2f}")
c3.metric("Average Transaction", f"${summary['average_transaction_amount']:,.2f}")
c4.metric("Median Transaction", f"${summary['median_transaction_amount']:,.2f}")

st.divider()

col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Transaction Volume by Payment Channel")
    df_channel = pd.DataFrame(by_channel)
    fig_pie = px.pie(
        df_channel,
        names="type",
        values="count",
        hole=0.4,
        title="Channel Volume Distribution",
        color_discrete_sequence=px.colors.qualitative.Prism,
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with col_b:
    st.subheader("Transaction Value Share ($)")
    fig_bar = px.bar(
        df_channel,
        x="type",
        y="total_amount",
        color="type",
        text_auto=".2s",
        title="Gross Monetary Volume by Type",
        labels={"total_amount": "Total Volume ($)", "type": "Payment Channel"},
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("Daily Transaction Volume & Fraud Trajectory")
df_trends = pd.DataFrame(trends)
if not df_trends.empty:
    fig_line = px.line(
        df_trends,
        x="day",
        y="volume",
        title="31-Day Simulated Transaction Velocity (Steps 1-744)",
        markers=True,
        labels={"day": "Simulation Day (24hr Buckets)", "volume": "Daily Transaction Count"},
    )
    st.plotly_chart(fig_line, use_container_width=True)
