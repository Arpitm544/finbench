# FinBench — Financial Transaction Analytics Report

**Analytics Scope:** Complete Ingested Transaction Population  
**Total Volume:** 10,000 records  
**Total Value:** $261,435,540.47  
**Average Transaction Size:** $26,143.55  
**Median Transaction Size:** $5,048.11  

---

## 1. Transaction Volume & Liquidity by Channel

Financial transactions are segmented across five primary operational payment and settlement channels:

| Transaction Type | Volume Count | Volume Share | Gross Volume ($) | Average Amount ($) |
| :--- | :--- | :--- | :--- | :--- |
| `CASH_OUT` | 3,555 | 35.55% | $107,564,352.97 | $30,257.20 |
| `PAYMENT` | 3,450 | 34.5% | $80,681,919.15 | $23,386.06 |
| `CASH_IN` | 2,129 | 21.29% | $51,885,368.91 | $24,370.77 |
| `TRANSFER` | 780 | 7.8% | $18,329,986.23 | $23,499.98 |
| `DEBIT` | 86 | 0.86% | $2,973,913.21 | $34,580.39 |

---

## 2. High-Value Tail Analysis & Skewness

Transaction amounts exhibit severe positive skewness characteristic of real-world money movement networks:

- **50th Percentile (Median):** $5,048.11
- **90th Percentile:** $51,017.53
- **95th Percentile:** $97,354.29
- **99th Percentile:** $328,905.74
- **99.9th Percentile:** $1,856,306.38

> [!IMPORTANT]
> The top 1% of transactions (`P99` cutoff at **$328,905.74**) account for **31.74%** of gross network volume. Fraud mitigation rules targeting high-value thresholds must balance capital preservation with customer friction.
