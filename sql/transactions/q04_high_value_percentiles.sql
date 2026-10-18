-- Q04: Percentile Quartile Segmentation using NTILE
WITH ranked_transactions AS (
    SELECT 
        transaction_id,
        type,
        amount,
        NTILE(4) OVER (ORDER BY amount) AS quartile
    FROM transactions
)
SELECT 
    quartile,
    COUNT(*) AS tx_count,
    ROUND(MIN(amount), 2) AS min_amount,
    ROUND(MAX(amount), 2) AS max_amount,
    ROUND(AVG(amount), 2) AS avg_amount,
    ROUND(SUM(amount), 2) AS total_amount
FROM ranked_transactions
GROUP BY quartile
ORDER BY quartile;
