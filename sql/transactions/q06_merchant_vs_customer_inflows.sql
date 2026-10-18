-- Q06: Merchant vs Customer Destination Liquidity
SELECT 
    CASE 
        WHEN name_dest LIKE 'M%' THEN 'Merchant'
        ELSE 'Customer'
    END AS destination_entity_type,
    type,
    COUNT(*) AS tx_count,
    ROUND(SUM(amount), 2) AS total_amount,
    ROUND(AVG(amount), 2) AS avg_amount
FROM transactions
GROUP BY 
    CASE WHEN name_dest LIKE 'M%' THEN 'Merchant' ELSE 'Customer' END,
    type
ORDER BY destination_entity_type, tx_count DESC;
