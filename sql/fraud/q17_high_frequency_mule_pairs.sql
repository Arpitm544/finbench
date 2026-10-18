-- Q17: High-Risk Recipient Accounts with Suspicious Ratio of Inflows
SELECT 
    name_dest,
    COUNT(*) AS total_transfers_received,
    SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) AS fraudulent_inflows,
    ROUND(SUM(amount), 2) AS total_inflow_volume,
    ROUND(
        SUM(CASE WHEN is_fraud = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
        2
    ) AS fraud_inflow_ratio_pct
FROM transactions
WHERE type IN ('TRANSFER', 'CASH_OUT')
GROUP BY name_dest
HAVING COUNT(*) >= 1
ORDER BY fraudulent_inflows DESC, total_inflow_volume DESC
LIMIT 20;
