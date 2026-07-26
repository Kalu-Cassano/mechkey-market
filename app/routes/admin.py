from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models import Category, Order, Product, User
from app.utils import roles_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
@roles_required("admin")
def dashboard():
    stats = {
        "users": db.session.scalar(db.select(func.count(User.id))),
        "vendors": db.session.scalar(db.select(func.count(User.id)).where(User.role == "vendor")),
        "products": db.session.scalar(db.select(func.count(Product.id))),
        "orders": db.session.scalar(db.select(func.count(Order.id))),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/users")
@login_required
@roles_required("admin")
def users():
    user_list = db.session.scalars(db.select(User).order_by(User.created_at.desc())).all()
    return render_template("admin/users.html", users=user_list)


@admin_bp.post("/users/<int:user_id>/toggle")
@login_required
@roles_required("admin")
def user_toggle(user_id):
    user = db.get_or_404(User, user_id)
    if user.role != "admin":
        user.is_active_account = not user.is_active_account
        db.session.commit()
        flash("Đã cập nhật trạng thái tài khoản.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/categories", methods=["GET", "POST"])
@login_required
@roles_required("admin")
def categories():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if name and not db.session.scalar(db.select(Category).where(Category.name == name)):
            db.session.add(Category(name=name, description=request.form.get("description", "").strip()))
            db.session.commit()
            flash("Đã thêm danh mục.", "success")
        else:
            flash("Tên danh mục không hợp lệ hoặc đã tồn tại.", "danger")
    category_list = db.session.scalars(db.select(Category).order_by(Category.name)).all()
    return render_template("admin/categories.html", categories=category_list)


@admin_bp.route("/orders")
@login_required
@roles_required("admin")
def orders():
    order_list = db.session.scalars(db.select(Order).order_by(Order.created_at.desc())).all()
    return render_template("admin/orders.html", orders=order_list)


@admin_bp.post("/orders/<int:order_id>/status")
@login_required
@roles_required("admin")
def order_status(order_id):
    order = db.get_or_404(Order, order_id)
    allowed = {"Pending", "Confirmed", "Shipping", "Completed", "Cancelled"}
    status = request.form.get("status")
    if status in allowed:
        order.status = status
        db.session.commit()
        flash("Đã cập nhật đơn hàng.", "success")
    return redirect(url_for("admin.orders"))

