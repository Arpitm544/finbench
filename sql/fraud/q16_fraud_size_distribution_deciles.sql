-- Q16: Fraud Amount Decile Distribution
WITH fraud_deciles AS (
    SELECT 
        transaction_id,
        amount,
        NTILE(10) OVER (ORDER BY amount) AS decile
    FROM transactions
    WHERE is_fraud = 1
)
SELECT 
    decile,
    COUNT(*) AS fraud_tx_count,
    ROUND(MIN(amount), 2) AS min_amount,
    ROUND(MAX(amount), 2) AS max_amount,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(SUM(amount), 2) AS total_decile_loss
FROM fraud_deciles
GROUP BY decile
ORDER BY decile;
