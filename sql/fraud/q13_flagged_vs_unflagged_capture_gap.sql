-- Q13: Flagged vs Unflagged High-Value Fraud Detection Gap
SELECT 
    CASE 
        WHEN is_flagged_fraud = 1 THEN 'Flagged by Rule'
        ELSE 'Missed by Rule'
    END AS detection_status,
    COUNT(*) AS fraud_incident_count,
    ROUND(SUM(amount), 2) AS total_financial_loss,
    ROUND(AVG(amount), 2) AS avg_incident_size,
    ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (), 2) AS incident_percentage,
    ROUND(SUM(amount) * 100.0 / SUM(SUM(amount)) OVER (), 2) AS loss_percentage
FROM transactions
WHERE is_fraud = 1
GROUP BY CASE WHEN is_flagged_fraud = 1 THEN 'Flagged by Rule' ELSE 'Missed by Rule' END;
