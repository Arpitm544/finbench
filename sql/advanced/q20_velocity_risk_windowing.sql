-- Q20: Multi-Transaction Velocity Acceleration using LEAD
WITH ordered_account_tx AS (
    SELECT 
        transaction_id,
        name_orig,
        step,
        amount,
        is_fraud,
        LEAD(step, 1) OVER (PARTITION BY name_orig ORDER BY step) AS next_step,
        LEAD(amount, 1) OVER (PARTITION BY name_orig ORDER BY step) AS next_amount
    FROM transactions
)
SELECT 
    name_orig,
    step AS initial_step,
    amount AS initial_amount,
    next_step,
    next_amount,
    (next_step - step) AS step_gap,
    is_fraud
FROM ordered_account_tx
WHERE next_step IS NOT NULL AND (next_step - step) <= 3
ORDER BY step_gap ASC, initial_amount DESC
LIMIT 20;
