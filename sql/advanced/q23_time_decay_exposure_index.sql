-- Q23: Time-Decay Window Exposure Calculation
SELECT 
    name_dest,
    COUNT(*) AS total_tx,
    ROUND(SUM(amount * (1.0 / (1.0 + (744.0 - step) / 100.0))), 2) AS recency_weighted_volume,
    SUM(is_fraud) AS fraud_events
FROM transactions
WHERE is_fraud = 1
GROUP BY name_dest
ORDER BY recency_weighted_volume DESC
LIMIT 15;
