from datetime import datetime, timezone
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc).replace(tzinfo=None)


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.Unicode(120), nullable=False)
    email = db.Column(db.Unicode(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.Unicode(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="customer")
    store_name = db.Column(db.Unicode(120))
    is_active_account = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    products = db.relationship("Product", back_populates="vendor")
    orders = db.relationship("Order", back_populates="customer")
    reviews = db.relationship("Review", back_populates="customer")

    @property
    def is_active(self):
        return self.is_active_account

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Unicode(100), unique=True, nullable=False)
    description = db.Column(db.Unicode(500))
    products = db.relationship("Product", back_populates="category")


class Product(db.Model):
    __tablename__ = "products"
    __table_args__ = (
        db.CheckConstraint("price >= 0", name="ck_products_price"),
        db.CheckConstraint("stock >= 0", name="ck_products_stock"),
    )

    id = db.Column(db.Integer, primary_key=True)
    vendor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=False)
    name = db.Column(db.Unicode(160), nullable=False)
    description = db.Column(db.UnicodeText)
    price = db.Column(db.Numeric(12, 2), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=0)
    image_filename = db.Column(db.Unicode(255))
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    vendor = db.relationship("User", back_populates="products")
    category = db.relationship("Category", back_populates="products")
    order_items = db.relationship("OrderItem", back_populates="product")
    reviews = db.relationship("Review", back_populates="product", cascade="all, delete-orphan")

    @property
    def average_rating(self):
        if not self.reviews:
            return 0
        return round(sum(review.rating for review in self.reviews) / len(self.reviews), 1)


class Order(db.Model):
    __tablename__ = "orders"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    shipping_address = db.Column(db.Unicode(500), nullable=False)
    phone = db.Column(db.String(30), nullable=False)
    payment_method = db.Column(db.String(30), nullable=False, default="COD")
    total_amount = db.Column(db.Numeric(12, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    customer = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = db.relationship(
        "Payment", back_populates="order", uselist=False, cascade="all, delete-orphan"
    )


class OrderItem(db.Model):
    __tablename__ = "order_items"
    __table_args__ = (
        db.CheckConstraint("quantity > 0", name="ck_order_items_quantity"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_name = db.Column(db.Unicode(160), nullable=False)
    unit_price = db.Column(db.Numeric(12, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")

    order = db.relationship("Order", back_populates="items")
    product = db.relationship("Product", back_populates="order_items")
    vendor = db.relationship("User", foreign_keys=[vendor_id])

    @property
    def subtotal(self):
        return Decimal(self.unit_price) * self.quantity


class Payment(db.Model):
    __tablename__ = "payments"
    __table_args__ = (
        db.CheckConstraint("amount >= 0", name="ck_payments_amount"),
    )

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey("orders.id"), unique=True, nullable=False)
    method = db.Column(db.String(30), nullable=False)
    status = db.Column(db.String(30), nullable=False, default="Pending")
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    transaction_code = db.Column(db.String(80), unique=True)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    order = db.relationship("Order", back_populates="payment")


class Review(db.Model):
    __tablename__ = "reviews"
    __table_args__ = (
        db.UniqueConstraint("customer_id", "product_id", name="uq_review_customer_product"),
        db.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_reviews_rating"),
    )

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Unicode(1000))
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    customer = db.relationship("User", back_populates="reviews")
    product = db.relationship("Product", back_populates="reviews")
