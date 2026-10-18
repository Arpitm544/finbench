-- Q07: Balance Depletion Velocity (Total Account Draining)
SELECT 
    transaction_id,
    step,
    type,
    name_orig,
    ROUND(oldbalance_org, 2) AS old_balance,
    ROUND(amount, 2) AS drained_amount,
    ROUND(newbalance_orig, 2) AS remaining_balance,
    is_fraud
FROM transactions
WHERE oldbalance_org > 10000 
  AND newbalance_orig = 0 
  AND amount >= oldbalance_org
ORDER BY amount DESC
LIMIT 25;
