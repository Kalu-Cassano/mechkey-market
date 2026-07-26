USE MarketplaceDB;
GO
CREATE OR ALTER PROCEDURE sp_get_vendor_orders @VendorId INT
AS
BEGIN
    SET NOCOUNT ON;
    SELECT o.id, o.created_at, o.status, oi.product_name, oi.quantity,
           oi.unit_price, oi.quantity * oi.unit_price AS subtotal
    FROM orders o
    INNER JOIN order_items oi ON oi.order_id = o.id
    WHERE oi.vendor_id = @VendorId
    ORDER BY o.created_at DESC;
END;
GO

