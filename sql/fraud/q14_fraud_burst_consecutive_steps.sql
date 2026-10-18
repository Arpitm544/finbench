-- Q14: Temporal Spikes in Fraud Rate Across Rolling Windows
WITH windowed_activity AS (
    SELECT 
        step,
        COUNT(*) AS total_tx,
        SUM(is_fraud) AS fraud_tx
    FROM transactions
    GROUP BY step
)
SELECT 
    step,
    total_tx,
    fraud_tx,
    ROUND((fraud_tx * 100.0 / NULLIF(total_tx, 0)), 4) AS step_fraud_rate_pct,
    ROUND(AVG(fraud_tx) OVER (
        ORDER BY step 
        ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
    ), 2) AS rolling_12h_avg_fraud_count
FROM windowed_activity
ORDER BY fraud_tx DESC
LIMIT 20;
