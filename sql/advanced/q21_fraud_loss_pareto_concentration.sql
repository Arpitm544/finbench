-- Q21: Pareto Cumulative Concentration of Realized Fraud Losses
WITH sorted_frauds AS (
    SELECT 
        transaction_id,
        amount,
        ROW_NUMBER() OVER (ORDER BY amount DESC) AS fraud_rank,
        COUNT(*) OVER () AS total_fraud_count,
        SUM(amount) OVER () AS total_fraud_amount,
        SUM(amount) OVER (ORDER BY amount DESC) AS cumulative_loss
    FROM transactions
    WHERE is_fraud = 1
)
SELECT 
    fraud_rank,
    ROUND(amount, 2) AS incident_amount,
    ROUND(fraud_rank * 100.0 / total_fraud_count, 2) AS pct_of_incidents,
    ROUND(cumulative_loss * 100.0 / total_fraud_amount, 2) AS pct_of_total_loss
FROM sorted_frauds
WHERE fraud_rank IN (1, 5, 10, 20, 50, 100) OR (fraud_rank * 100 / total_fraud_count) >= 80
ORDER BY fraud_rank
LIMIT 15;
