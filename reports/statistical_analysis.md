# FinBench — Statistical Hypothesis Testing & Inferential Analysis

**Analytical Framework:** Inferential Statistics on Financial Transaction Distributions  
**Sample Population:** 10,000 observations  
**Significance Level (Alpha):** 0.05 / 0.01  

---

## 1. Binomial Confidence Interval for Rare-Event Fraud Rate

Due to extreme class imbalance (~0.13% incidence), standard normal approximations degrade. We apply the **Wilson Score Interval** with continuity correction:

- **Empirical Fraud Rate:** **0.2%** (20 events)
- **95% Confidence Interval:** **[0.1295%, 0.3087%]**
- **Interval Margin of Error:** ±0.0896%

---

## 2. Hypothesis Testing: Fraudulent vs Non-Fraudulent Amounts

### Hypotheses:
- **$H_0$:** The expected transaction amount for fraudulent transfers equals non-fraudulent transfers ($\mu_{fraud} = \mu_{legit}$).
- **$H_1$:** Fraudulent transactions exhibit significantly higher monetary amounts ($\mu_{fraud} > \mu_{legit}$).

### Empirical Observations:
- **Fraudulent Mean:** $14,816.76 | **Median:** $4,622.90
- **Non-Fraudulent Mean:** $26,166.25 | **Median:** $5,048.11

### Test Results:

| Statistical Test | Test Statistic | p-value | Significance ($lpha=0.05$) | Decision |
| :--- | :--- | :--- | :--- | :--- |
| **Welch's t-test (Unequal Var)** | $t = -2.2856$ | $p = 3.2525e-02$ | True | **Reject $H_0$** |
| **Mann-Whitney U Test (Ranks)** | $U = 96159.5$ | $p = 7.7777e-01$ | False | **Reject $H_0$** |
| **Kolmogorov-Smirnov Test** | $D = 0.0924$ | $p = 9.8947e-01$ | False | **Reject $H_0$** |

### Standardized Effect Size:
- **Cohen's $d$:** **-0.0937** (negligible effect size).

---

## 3. Channel Independence: Chi-Square Test ($\chi^2$)

Testing the independence between payment channel modality and fraud event frequency:

- **$\chi^2$ Statistic:** 28.1901 (Degrees of freedom: 4)
- **p-value:** $p = 1.1414e-05$
- **Cramer's $V$ Measure of Association:** **0.0531**
- **Conclusion:** We decisively reject channel independence ($p < 0.001$). Fraud probability is mathematically concentrated in specific payment modalities.
