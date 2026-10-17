# FinBench — Financial Fraud Analytics & Loss Accounting Report

**Analytics Domain:** Financial Transaction Fraud Vulnerability  
**Dataset Population:** 10,000 records  
**Confirmed Fraudulent Transactions:** 20  
**Network Fraud Prevalence:** **0.2%** (20.0 bps)  
**Total Realized Financial Losses:** **$296,335.11**  
**Loss Share of Total Volume:** **0.11%**  

---

## 1. Channel-Specific Fraud Vulnerability

An empirical breakdown of fraudulent activities across transaction types:

| Channel Type | Total Volume | Fraud Incidents | Fraud Rate (%) | Gross Fraud Loss ($) |
| :--- | :--- | :--- | :--- | :--- |
| `CASH_OUT` | 3,555 | 18 | **0.5063%** | $283,959.96 |
| `TRANSFER` | 780 | 2 | **0.2564%** | $12,375.15 |
| `CASH_IN` | 2,129 | 0 | **0.0%** | $0.00 |
| `DEBIT` | 86 | 0 | **0.0%** | $0.00 |
| `PAYMENT` | 3,450 | 0 | **0.0%** | $0.00 |

> [!IMPORTANT]
> **Key Domain Finding:** In the PaySim environment, fraud is exclusively confined to two operational modalities:
> 1. `TRANSFER`: Primary attack vector for unauthorized funds exfiltration from victim accounts.
> 2. `CASH_OUT`: Secondary liquidation vector where compromised balances are withdrawn from the financial network.
> `PAYMENT`, `CASH_IN`, and `DEBIT` exhibit a 0.0% fraud incident rate.

---

## 2. Legacy Rule Disparity vs. Realized Fraud

The baseline simulation rule (`isFlaggedFraud`), which triggers only on single transfers exceeding $200,000, shows substantial detection disparity:

- **True Fraud Incidents:** 20
- **Simulation Rule Flagged:** 0
- **Legacy Rule Sensitivity (Recall):** **0.00%**

> [!WARNING]
> Simple static threshold filters miss over 90% of sophisticated fraud attempts. Advanced machine learning classifiers and behavioral graph indicators are necessary to protect assets without introducing excessive false positive friction.
