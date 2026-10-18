-- Q24: Multi-Threshold Decision Tradeoff Analysis (Operational Simulation)
SELECT 
    threshold,
    COUNT(*) AS flagged_volume,
    SUM(is_fraud) AS true_positives,
    COUNT(*) - SUM(is_fraud) AS false_positives,
    ROUND(SUM(is_fraud) * 100.0 / NULLIF(COUNT(*), 0), 2) AS precision_pct,
    ROUND(SUM(is_fraud) * 100.0 / NULLIF(total_fraud, 0), 2) AS recall_pct
FROM (
    SELECT 
        amount, 
        is_fraud,
        (SELECT SUM(is_fraud) FROM transactions) AS total_fraud,
        CASE 
            WHEN amount >= 500000 THEN '500k_Cutoff'
            WHEN amount >= 200000 THEN '200k_Cutoff'
            WHEN amount >= 100000 THEN '100k_Cutoff'
            WHEN amount >= 50000  THEN '050k_Cutoff'
            ELSE 'Below_50k'
        END AS threshold
    FROM transactions
    WHERE type IN ('TRANSFER', 'CASH_OUT')
) sub
WHERE threshold != 'Below_50k'
GROUP BY threshold, total_fraud
ORDER BY threshold DESC;
