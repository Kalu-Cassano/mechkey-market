from app import create_app
from app.extensions import db
from app.models import Category, Product, User

app = create_app()

with app.app_context():
    db.create_all()
    categories = db.session.scalars(db.select(Category)).all()
    if not categories:
        categories = [
            Category(name="Điện tử", description="Thiết bị và phụ kiện điện tử"),
            Category(name="Thời trang", description="Quần áo và phụ kiện"),
            Category(name="Gia dụng", description="Sản phẩm sử dụng trong gia đình"),
            Category(name="Sách", description="Sách học tập và giải trí"),
        ]
        db.session.add_all(categories)
        db.session.flush()

    def ensure_user(email, name, role, password, store=None):
        user = db.session.scalar(db.select(User).where(User.email == email))
        if not user:
            user = User(email=email)
            db.session.add(user)
        user.full_name = name
        user.role = role
        user.store_name = store
        user.is_active_account = True
        user.set_password(password)
        return user

    ensure_user("admin@unimarket.com", "Quản trị viên", "admin", "Admin123!")
    vendor = ensure_user(
        "vendor@unimarket.com", "Nguyễn Người Bán", "vendor", "Vendor123!", "Tech Store"
    )
    ensure_user("customer@unimarket.com", "Trần Khách Hàng", "customer", "Customer123!")
    db.session.flush()

    legacy_vendor = db.session.scalar(
        db.select(User).where(User.email == "vendor@unimarket.local")
    )
    if legacy_vendor:
        demo_products = db.session.scalars(
            db.select(Product).where(
                Product.vendor_id == legacy_vendor.id,
                Product.name.in_(["Bàn phím cơ học", "Chuột không dây"]),
            )
        ).all()
        for product in demo_products:
            product.vendor_id = vendor.id

    if not db.session.scalar(db.select(Product.id)):
        db.session.add_all(
            [
                Product(
                    vendor_id=vendor.id,
                    category_id=categories[0].id,
                    name="Bàn phím cơ học",
                    description="Bàn phím gọn nhẹ dành cho học tập và làm việc.",
                    price=750000,
                    stock=25,
                ),
                Product(
                    vendor_id=vendor.id,
                    category_id=categories[0].id,
                    name="Chuột không dây",
                    description="Chuột không dây kết nối ổn định.",
                    price=320000,
                    stock=40,
                ),
            ]
        )
    db.session.commit()
    print("Đã tạo dữ liệu demo.")
