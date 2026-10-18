-- Q05: Origin Account Turnover and Cumulative Outflows
WITH origin_metrics AS (
    SELECT 
        name_orig,
        COUNT(*) AS tx_count,
        SUM(amount) AS total_outflow,
        AVG(amount) AS avg_tx_size,
        DENSE_RANK() OVER (ORDER BY SUM(amount) DESC) AS rank_by_volume
    FROM transactions
    GROUP BY name_orig
)
SELECT 
    name_orig,
    tx_count,
    ROUND(total_outflow, 2) AS total_outflow,
    ROUND(avg_tx_size, 2) AS avg_tx_size,
    rank_by_volume
FROM origin_metrics
WHERE rank_by_volume <= 20
ORDER BY rank_by_volume;
