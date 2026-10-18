-- Q25: Two-Hop Money Mule Chain Reconstruction (Transfer In -> Cash Out)
SELECT 
    t1.step AS stage1_step,
    t1.type AS stage1_type,
    t1.name_orig AS victim_account,
    t1.name_dest AS intermediary_mule,
    ROUND(t1.amount, 2) AS exfiltration_amount,
    t2.step AS stage2_step,
    t2.type AS stage2_type,
    t2.name_dest AS liquidation_point,
    ROUND(t2.amount, 2) AS liquidation_amount,
    (t2.step - t1.step) AS turnaround_hours
FROM transactions t1
JOIN transactions t2 
  ON t1.name_dest = t2.name_orig
WHERE t1.type = 'TRANSFER' 
  AND t2.type = 'CASH_OUT'
  AND t2.step >= t1.step 
  AND t2.step <= t1.step + 24
LIMIT 20;
