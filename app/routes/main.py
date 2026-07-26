from flask import Blueprint, render_template, request
from sqlalchemy import or_

from app.extensions import db
from app.models import Category, Product

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    products = db.session.scalars(
        db.select(Product).where(Product.is_active == True).order_by(Product.created_at.desc()).limit(8)  # noqa: E712
    ).all()
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return render_template("main/index.html", products=products, categories=categories)


@main_bp.route("/products")
def products():
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)
    statement = db.select(Product).where(Product.is_active == True)  # noqa: E712
    if search:
        statement = statement.where(
            or_(Product.name.ilike(f"%{search}%"), Product.description.ilike(f"%{search}%"))
        )
    if category_id:
        statement = statement.where(Product.category_id == category_id)
    product_list = db.session.scalars(statement.order_by(Product.created_at.desc())).all()
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return render_template(
        "main/products.html",
        products=product_list,
        categories=categories,
        search=search,
        selected_category=category_id,
    )


@main_bp.route("/products/<int:product_id>")
def product_detail(product_id):
    product = db.get_or_404(Product, product_id)
    return render_template("main/product_detail.html", product=product)
