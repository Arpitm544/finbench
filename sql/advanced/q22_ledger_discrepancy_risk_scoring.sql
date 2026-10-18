-- Q22: Ledger Discrepancy Anomaly Composite Risk Indicator
WITH discrepancy_table AS (
    SELECT 
        transaction_id,
        type,
        amount,
        is_fraud,
        ROUND((newbalance_orig + amount) - oldbalance_org, 2) AS orig_ledger_error,
        ROUND((newbalance_dest - oldbalance_dest) - amount, 2) AS dest_ledger_error
    FROM transactions
    WHERE type IN ('TRANSFER', 'CASH_OUT')
)
SELECT 
    CASE 
        WHEN ABS(orig_ledger_error) > 1.0 AND ABS(dest_ledger_error) > 1.0 THEN 'Dual Ledger Error'
        WHEN ABS(orig_ledger_error) > 1.0 THEN 'Orig Ledger Error'
        WHEN ABS(dest_ledger_error) > 1.0 THEN 'Dest Ledger Error'
        ELSE 'Ledger Balanced'
    END AS error_category,
    COUNT(*) AS tx_count,
    SUM(is_fraud) AS fraud_count,
    ROUND(SUM(is_fraud) * 100.0 / COUNT(*), 3) AS fraud_rate_pct,
    ROUND(AVG(amount), 2) AS avg_transaction_size
FROM discrepancy_table
GROUP BY 
    CASE 
        WHEN ABS(orig_ledger_error) > 1.0 AND ABS(dest_ledger_error) > 1.0 THEN 'Dual Ledger Error'
        WHEN ABS(orig_ledger_error) > 1.0 THEN 'Orig Ledger Error'
        WHEN ABS(dest_ledger_error) > 1.0 THEN 'Dest Ledger Error'
        ELSE 'Ledger Balanced'
    END
ORDER BY fraud_rate_pct DESC;
