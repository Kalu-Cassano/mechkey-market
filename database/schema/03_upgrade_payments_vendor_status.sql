USE MarketplaceDB;
GO

IF COL_LENGTH('dbo.order_items', 'status') IS NULL
BEGIN
    EXEC(N'ALTER TABLE dbo.order_items
        ADD status VARCHAR(30) NOT NULL
            CONSTRAINT DF_order_items_status DEFAULT ''Pending'';');
END;
GO

IF COL_LENGTH('dbo.order_items', 'status') IS NOT NULL
   AND NOT EXISTS (
       SELECT 1 FROM sys.check_constraints
       WHERE name = 'CK_order_items_status'
   )
BEGIN
    EXEC(N'ALTER TABLE dbo.order_items
        ADD CONSTRAINT CK_order_items_status
            CHECK (status IN (
                ''Pending'',''Confirmed'',''Shipping'',''Completed'',''Cancelled''
            ));');
END;
GO

IF OBJECT_ID(N'dbo.payments', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.payments (
        id INT IDENTITY(1,1) PRIMARY KEY,
        order_id INT NOT NULL UNIQUE,
        method VARCHAR(30) NOT NULL
            CONSTRAINT CK_payments_method CHECK (method IN ('COD','BANK')),
        status VARCHAR(30) NOT NULL
            CONSTRAINT DF_payments_status DEFAULT 'Pending'
            CONSTRAINT CK_payments_status CHECK (status IN ('Pending','Paid','Cancelled','Refunded')),
        amount DECIMAL(12,2) NOT NULL
            CONSTRAINT CK_payments_amount CHECK (amount >= 0),
        transaction_code VARCHAR(80) NULL UNIQUE,
        paid_at DATETIME2 NULL,
        created_at DATETIME2 NOT NULL
            CONSTRAINT DF_payments_created_at DEFAULT SYSUTCDATETIME(),
        CONSTRAINT FK_payments_order FOREIGN KEY (order_id) REFERENCES dbo.orders(id)
    );

    INSERT INTO dbo.payments(order_id, method, status, amount)
    SELECT id, payment_method, 'Pending', total_amount
    FROM dbo.orders;
END;
GO
