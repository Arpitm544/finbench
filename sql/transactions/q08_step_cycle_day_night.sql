-- Q08: Diurnal 24-Hour Cycle Activity Distribution
SELECT 
    (step % 24) AS hour_of_day,
    COUNT(*) AS tx_count,
    ROUND(SUM(amount), 2) AS hourly_volume,
    ROUND(AVG(amount), 2) AS avg_hourly_amount,
    SUM(is_fraud) AS fraud_count
FROM transactions
GROUP BY (step % 24)
ORDER BY hour_of_day;
