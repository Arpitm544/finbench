-- Q26: Statistical Moments and Skewness Proxy by Payment Type
WITH base_stats AS (
    SELECT 
        type,
        COUNT(*) AS n,
        AVG(amount) AS mean_amount,
        AVG(amount * amount) AS mean_sq_amount
    FROM transactions
    GROUP BY type
)
SELECT 
    type,
    n,
    ROUND(mean_amount, 2) AS sample_mean,
    ROUND(SQRT(NULLIF(mean_sq_amount - (mean_amount * mean_amount), 0)), 2) AS sample_std_dev,
    ROUND(
        SQRT(NULLIF(mean_sq_amount - (mean_amount * mean_amount), 0)) / NULLIF(mean_amount, 0), 
        3
    ) AS coefficient_of_variation
FROM base_stats
ORDER BY sample_mean DESC;
