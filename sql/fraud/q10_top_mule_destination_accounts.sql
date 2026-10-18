-- Q10: Top Destination Mule Accounts by Realized Fraud Inflow
SELECT 
    name_dest,
    COUNT(*) AS total_incoming_tx,
    SUM(is_fraud) AS fraud_incoming_tx,
    ROUND(SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END), 2) AS total_fraud_inflow,
    ROUND(AVG(CASE WHEN is_fraud = 1 THEN amount ELSE NULL END), 2) AS avg_fraud_tx_size,
    DENSE_RANK() OVER (ORDER BY SUM(CASE WHEN is_fraud = 1 THEN amount ELSE 0 END) DESC) AS rank_by_loss
FROM transactions
WHERE is_fraud = 1
GROUP BY name_dest
ORDER BY total_fraud_inflow DESC
LIMIT 20;
