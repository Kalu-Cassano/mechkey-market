USE MarketplaceDB;
GO
CREATE OR ALTER VIEW vw_vendor_sales_summary AS
SELECT
    u.id AS vendor_id,
    COALESCE(u.store_name, u.full_name) AS store_name,
    COUNT(DISTINCT oi.order_id) AS total_orders,
    SUM(oi.quantity) AS items_sold,
    SUM(oi.unit_price * oi.quantity) AS revenue
FROM users u
LEFT JOIN order_items oi ON oi.vendor_id = u.id
WHERE u.role = 'vendor'
GROUP BY u.id, u.store_name, u.full_name;
GO

