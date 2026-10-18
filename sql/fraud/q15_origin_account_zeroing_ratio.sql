-- Q15: Complete Account Balance Zeroing Propensity
SELECT 
    is_fraud,
    COUNT(*) AS total_transactions,
    SUM(CASE WHEN oldbalance_org > 0 AND newbalance_orig = 0 THEN 1 ELSE 0 END) AS zeroed_accounts,
    ROUND(
        SUM(CASE WHEN oldbalance_org > 0 AND newbalance_orig = 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) AS zeroing_propensity_pct
FROM transactions
WHERE type IN ('TRANSFER', 'CASH_OUT')
GROUP BY is_fraud;
