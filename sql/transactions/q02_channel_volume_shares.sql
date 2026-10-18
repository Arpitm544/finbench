-- Q02: Channel Volume and Value Market Share with Window Totals
SELECT 
    type,
    COUNT(*) AS tx_count,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS volume_share_pct,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 2) AS value_share_pct
FROM transactions
GROUP BY type
ORDER BY tx_count DESC;
