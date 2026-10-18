-- Q18: Correlated Transfer vs Cashout Volume Ratio
WITH channel_daily AS (
    SELECT 
        (step / 24) + 1 AS sim_day,
        SUM(CASE WHEN type = 'TRANSFER' THEN amount ELSE 0 END) AS transfer_amount,
        SUM(CASE WHEN type = 'CASH_OUT' THEN amount ELSE 0 END) AS cash_out_amount,
        SUM(CASE WHEN type = 'TRANSFER' AND is_fraud = 1 THEN amount ELSE 0 END) AS fraud_transfer_amt,
        SUM(CASE WHEN type = 'CASH_OUT' AND is_fraud = 1 THEN amount ELSE 0 END) AS fraud_cashout_amt
    FROM transactions
    GROUP BY (step / 24) + 1
)
SELECT 
    sim_day,
    ROUND(transfer_amount, 2) AS transfer_amount,
    ROUND(cash_out_amount, 2) AS cash_out_amount,
    ROUND(fraud_transfer_amt, 2) AS fraud_transfer_amt,
    ROUND(fraud_cashout_amt, 2) AS fraud_cashout_amt,
    ROUND(cash_out_amount / NULLIF(transfer_amount, 0), 2) AS liquidation_ratio
FROM channel_daily
ORDER BY sim_day;
