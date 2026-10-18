-- Q09: Fraud Value Share vs Fraud Rate Ranking Disparity
WITH channel_stats AS (
    SELECT 
        type,
        COUNT(*) AS total_count,
        SUM(is_fraud) AS fraud_count,
        SUM(amount) AS total_channel_amount,
        SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) AS fraud_amount
    FROM transactions
    GROUP BY type
),
ranked_channels AS (
    SELECT 
        type,
        total_count,
        fraud_count,
        ROUND((fraud_count * 100.0 / NULLIF(total_count, 0)), 4) AS fraud_rate_pct,
        ROUND(fraud_amount, 2) AS fraud_amount,
        ROUND((fraud_amount * 100.0 / NULLIF(SUM(fraud_amount) OVER (), 0)), 2) AS fraud_value_share_pct,
        RANK() OVER (ORDER BY (fraud_count * 1.0 / NULLIF(total_count, 0)) DESC) AS rank_by_fraud_rate,
        RANK() OVER (ORDER BY fraud_amount DESC) AS rank_by_fraud_value
    FROM channel_stats
)
SELECT 
    type,
    total_count,
    fraud_count,
    fraud_rate_pct,
    fraud_amount,
    fraud_value_share_pct,
    rank_by_fraud_rate,
    rank_by_fraud_value,
    (rank_by_fraud_rate - rank_by_fraud_value) AS ranking_disparity
FROM ranked_channels
ORDER BY rank_by_fraud_value;
