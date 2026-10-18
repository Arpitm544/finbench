-- Q11: Anomaly of Zero Recipient Balance Post Large Inflow
SELECT 
    transaction_id,
    step,
    type,
    name_orig,
    name_dest,
    ROUND(amount, 2) AS amount,
    ROUND(oldbalance_dest, 2) AS old_dest_balance,
    ROUND(newbalance_dest, 2) AS new_dest_balance,
    is_fraud
FROM transactions
WHERE amount > 50000 
  AND oldbalance_dest = 0 
  AND newbalance_dest = 0
ORDER BY amount DESC
LIMIT 25;
