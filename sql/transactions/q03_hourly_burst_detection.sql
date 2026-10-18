-- Q03: Hourly Burst Detection with LAG Window Function
WITH hourly_stats AS (
    SELECT 
        step,
        COUNT(*) AS tx_count,
        SUM(amount) AS step_amount
    FROM transactions
    GROUP BY step
)
SELECT 
    step,
    tx_count,
    LAG(tx_count, 1) OVER (ORDER BY step) AS prev_step_count,
    ROUND((tx_count - LAG(tx_count, 1) OVER (ORDER BY step)) * 100.0 / 
          NULLIF(LAG(tx_count, 1) OVER (ORDER BY step), 0), 2) AS pct_change_velocity
FROM hourly_stats
ORDER BY pct_change_velocity DESC NULLS LAST
LIMIT 20;
