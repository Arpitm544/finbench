-- Q01: 7-Day Rolling Moving Average of Transaction Volume
WITH daily_aggregates AS (
    SELECT 
        (step / 24) + 1 AS sim_day,
        COUNT(*) AS daily_tx_count,
        SUM(amount) AS daily_amount
    FROM transactions
    GROUP BY (step / 24) + 1
)
SELECT 
    sim_day,
    daily_tx_count,
    ROUND(AVG(daily_tx_count) OVER (
        ORDER BY sim_day 
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ), 2) AS moving_avg_7d_tx_count,
    ROUND(daily_amount, 2) AS daily_amount
FROM daily_aggregates
ORDER BY sim_day;
