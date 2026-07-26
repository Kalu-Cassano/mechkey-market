from app import create_app
from app.extensions import db
from app.models import Category, Product, User
from config import TestConfig


def make_app():
    app = create_app(TestConfig)
    with app.app_context():
        db.create_all()
    return app


def test_home_page_loads():
    app = make_app()
    response = app.test_client().get("/")
    assert response.status_code == 200
    assert "MechKey Market" in response.get_data(as_text=True)


def test_password_hashing():
    app = make_app()
    with app.app_context():
        user = User(full_name="Test", email="test@example.com", role="customer")
        user.set_password("secret123")
        assert user.check_password("secret123")
        assert not user.check_password("wrong")


def test_product_listing():
    app = make_app()
    with app.app_context():
        vendor = User(full_name="Vendor", email="v@example.com", role="vendor")
        vendor.set_password("secret123")
        category = Category(name="Test category")
        db.session.add_all([vendor, category])
        db.session.flush()
        db.session.add(Product(vendor_id=vendor.id, category_id=category.id, name="Test product", price=10, stock=1))
        db.session.commit()
    response = app.test_client().get("/products")
    assert "Test product" in response.get_data(as_text=True)
