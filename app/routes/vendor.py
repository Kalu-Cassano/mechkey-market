import os

from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func

from app.extensions import db
from app.forms import ProductForm
from app.models import Category, Order, OrderItem, Product
from app.utils import roles_required, unique_filename
from app.services.order_service import sync_order_status

vendor_bp = Blueprint("vendor", __name__)


def set_category_choices(form):
    categories = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    form.category_id.choices = [(category.id, category.name) for category in categories]


@vendor_bp.route("/")
@login_required
@roles_required("vendor")
def dashboard():
    products_count = db.session.scalar(
        db.select(func.count(Product.id)).where(Product.vendor_id == current_user.id)
    )
    sales = db.session.scalar(
        db.select(func.coalesce(func.sum(OrderItem.unit_price * OrderItem.quantity), 0)).where(
            OrderItem.vendor_id == current_user.id
        )
    )
    recent_items = db.session.scalars(
        db.select(OrderItem)
        .join(Order)
        .where(OrderItem.vendor_id == current_user.id)
        .order_by(Order.created_at.desc())
        .limit(8)
    ).all()
    return render_template(
        "vendor/dashboard.html", products_count=products_count, sales=sales, recent_items=recent_items
    )


@vendor_bp.route("/products")
@login_required
@roles_required("vendor")
def products():
    product_list = db.session.scalars(
        db.select(Product)
        .where(Product.vendor_id == current_user.id)
        .order_by(Product.created_at.desc())
    ).all()
    return render_template("vendor/products.html", products=product_list)


@vendor_bp.route("/orders")
@login_required
@roles_required("vendor")
def orders():
    items = db.session.scalars(
        db.select(OrderItem)
        .join(Order)
        .where(OrderItem.vendor_id == current_user.id)
        .order_by(Order.created_at.desc())
    ).all()
    return render_template("vendor/orders.html", items=items)


@vendor_bp.post("/orders/items/<int:item_id>/status")
@login_required
@roles_required("vendor")
def order_item_status(item_id):
    item = db.get_or_404(OrderItem, item_id)
    if item.vendor_id != current_user.id:
        return "", 403

    allowed_transitions = {
        "Pending": {"Confirmed", "Cancelled"},
        "Confirmed": {"Shipping", "Cancelled"},
        "Shipping": {"Completed"},
        "Completed": set(),
        "Cancelled": set(),
    }
    new_status = request.form.get("status")
    if new_status not in allowed_transitions.get(item.status, set()):
        flash("Không thể chuyển sang trạng thái này.", "danger")
        return redirect(url_for("vendor.orders"))

    if new_status == "Cancelled" and item.status != "Cancelled":
        item.product.stock += item.quantity
    item.status = new_status
    sync_order_status(item.order)
    db.session.commit()
    flash("Đã cập nhật trạng thái đơn hàng.", "success")
    return redirect(url_for("vendor.orders"))


@vendor_bp.route("/products/create", methods=["GET", "POST"])
@login_required
@roles_required("vendor")
def product_create():
    form = ProductForm()
    set_category_choices(form)
    if form.validate_on_submit():
        product = Product(vendor_id=current_user.id)
        save_product(product, form)
        flash("Đã tạo sản phẩm.", "success")
        return redirect(url_for("vendor.products"))
    return render_template("vendor/product_form.html", form=form, title="Thêm sản phẩm")


@vendor_bp.route("/products/<int:product_id>/edit", methods=["GET", "POST"])
@login_required
@roles_required("vendor")
def product_edit(product_id):
    product = db.get_or_404(Product, product_id)
    if product.vendor_id != current_user.id:
        return "", 403
    form = ProductForm(obj=product)
    set_category_choices(form)
    if form.validate_on_submit():
        save_product(product, form)
        flash("Đã cập nhật sản phẩm.", "success")
        return redirect(url_for("vendor.products"))
    return render_template("vendor/product_form.html", form=form, title="Sửa sản phẩm")


@vendor_bp.post("/products/<int:product_id>/delete")
@login_required
@roles_required("vendor")
def product_delete(product_id):
    product = db.get_or_404(Product, product_id)
    if product.vendor_id != current_user.id:
        return "", 403

    if product.order_items:
        product.is_active = False
        db.session.commit()
        flash(
            "Sản phẩm đã có trong đơn hàng nên được ẩn thay vì xoá để giữ lịch sử.",
            "warning",
        )
    else:
        image_filename = product.image_filename
        db.session.delete(product)
        db.session.commit()
        if image_filename:
            image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], image_filename)
            if os.path.isfile(image_path):
                os.remove(image_path)
        flash("Đã xoá sản phẩm.", "success")
    return redirect(url_for("vendor.products"))


def save_product(product, form):
    product.name = form.name.data.strip()
    product.category_id = form.category_id.data
    product.description = form.description.data
    product.price = form.price.data
    product.stock = form.stock.data
    product.is_active = form.is_active.data
    if form.image.data:
        filename = unique_filename(form.image.data.filename)
        form.image.data.save(os.path.join(current_app.config["UPLOAD_FOLDER"], filename))
        product.image_filename = filename
    db.session.add(product)
    db.session.commit()
