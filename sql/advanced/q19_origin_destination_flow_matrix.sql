-- Q19: Origin vs Destination Balance Tier Flow Matrix
WITH balance_tiers AS (
    SELECT 
        transaction_id,
        amount,
        is_fraud,
        CASE 
            WHEN oldbalance_org = 0 THEN '01_Zero'
            WHEN oldbalance_org < 10000 THEN '02_Low (<10k)'
            WHEN oldbalance_org < 100000 THEN '03_Medium (10k-100k)'
            ELSE '04_High (>100k)'
        END AS orig_tier,
        CASE 
            WHEN oldbalance_dest = 0 THEN '01_Zero'
            WHEN oldbalance_dest < 10000 THEN '02_Low (<10k)'
            WHEN oldbalance_dest < 100000 THEN '03_Medium (10k-100k)'
            ELSE '04_High (>100k)'
        END AS dest_tier
    FROM transactions
)
SELECT 
    orig_tier,
    dest_tier,
    COUNT(*) AS total_tx_count,
    SUM(is_fraud) AS fraud_count,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_rate_pct,
    ROUND(SUM(amount), 2) AS total_volume
FROM balance_tiers
GROUP BY orig_tier, dest_tier
ORDER BY orig_tier, dest_tier;
