USE MarketplaceDB;
GO

CREATE TABLE users (
    id INT IDENTITY(1,1) PRIMARY KEY,
    full_name NVARCHAR(120) NOT NULL,
    email NVARCHAR(255) NOT NULL UNIQUE,
    password_hash NVARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'customer'
        CHECK (role IN ('customer', 'vendor', 'admin')),
    store_name NVARCHAR(120) NULL,
    is_active_account BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME()
);

CREATE TABLE categories (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name NVARCHAR(100) NOT NULL UNIQUE,
    description NVARCHAR(500) NULL
);

CREATE TABLE products (
    id INT IDENTITY(1,1) PRIMARY KEY,
    vendor_id INT NOT NULL,
    category_id INT NOT NULL,
    name NVARCHAR(160) NOT NULL,
    description NVARCHAR(MAX) NULL,
    price DECIMAL(12,2) NOT NULL CHECK (price >= 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    image_filename NVARCHAR(255) NULL,
    is_active BIT NOT NULL DEFAULT 1,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_products_vendor FOREIGN KEY (vendor_id) REFERENCES users(id),
    CONSTRAINT FK_products_category FOREIGN KEY (category_id) REFERENCES categories(id)
);

CREATE TABLE orders (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending','Confirmed','Shipping','Completed','Cancelled')),
    shipping_address NVARCHAR(500) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    payment_method VARCHAR(30) NOT NULL DEFAULT 'COD',
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0 CHECK (total_amount >= 0),
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_orders_customer FOREIGN KEY (customer_id) REFERENCES users(id)
);

CREATE TABLE order_items (
    id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    vendor_id INT NOT NULL,
    product_name NVARCHAR(160) NOT NULL,
    unit_price DECIMAL(12,2) NOT NULL CHECK (unit_price >= 0),
    quantity INT NOT NULL CHECK (quantity > 0),
    status VARCHAR(30) NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending','Confirmed','Shipping','Completed','Cancelled')),
    CONSTRAINT FK_order_items_order FOREIGN KEY (order_id) REFERENCES orders(id),
    CONSTRAINT FK_order_items_product FOREIGN KEY (product_id) REFERENCES products(id),
    CONSTRAINT FK_order_items_vendor FOREIGN KEY (vendor_id) REFERENCES users(id)
);

CREATE TABLE payments (
    id INT IDENTITY(1,1) PRIMARY KEY,
    order_id INT NOT NULL UNIQUE,
    method VARCHAR(30) NOT NULL CHECK (method IN ('COD','BANK')),
    status VARCHAR(30) NOT NULL DEFAULT 'Pending'
        CHECK (status IN ('Pending','Paid','Cancelled','Refunded')),
    amount DECIMAL(12,2) NOT NULL CHECK (amount >= 0),
    transaction_code VARCHAR(80) NULL UNIQUE,
    paid_at DATETIME2 NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT FK_payments_order FOREIGN KEY (order_id) REFERENCES orders(id)
);

CREATE TABLE reviews (
    id INT IDENTITY(1,1) PRIMARY KEY,
    customer_id INT NOT NULL,
    product_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment NVARCHAR(1000) NULL,
    created_at DATETIME2 NOT NULL DEFAULT SYSUTCDATETIME(),
    CONSTRAINT UQ_reviews_customer_product UNIQUE (customer_id, product_id),
    CONSTRAINT FK_reviews_customer FOREIGN KEY (customer_id) REFERENCES users(id),
    CONSTRAINT FK_reviews_product FOREIGN KEY (product_id) REFERENCES products(id)
);

CREATE INDEX IX_products_vendor ON products(vendor_id);
CREATE INDEX IX_products_category ON products(category_id);
CREATE INDEX IX_orders_customer ON orders(customer_id);
CREATE INDEX IX_order_items_order ON order_items(order_id);
GO
