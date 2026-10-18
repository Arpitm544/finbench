-- Q12: Running Cumulative Fraud Loss Curve Over Simulation Steps
WITH daily_fraud AS (
    SELECT 
        (step / 24) + 1 AS sim_day,
        COUNT(CASE WHEN is_fraud = 1 THEN 1 END) AS daily_fraud_count,
        COALESCE(SUM(CASE WHEN is_fraud = 1 THEN amount END), 0) AS daily_fraud_loss
    FROM transactions
    GROUP BY (step / 24) + 1
)
SELECT 
    sim_day,
    daily_fraud_count,
    ROUND(daily_fraud_loss, 2) AS daily_fraud_loss,
    ROUND(SUM(daily_fraud_loss) OVER (ORDER BY sim_day), 2) AS cumulative_fraud_loss,
    SUM(daily_fraud_count) OVER (ORDER BY sim_day) AS cumulative_fraud_count
FROM daily_fraud
ORDER BY sim_day;
