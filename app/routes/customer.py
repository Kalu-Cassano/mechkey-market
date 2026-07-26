from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.forms import CheckoutForm, ReviewForm
from app.models import Order, OrderItem, Product, Review
from app.services.cart_service import add_to_cart, cart_details, remove_from_cart, update_cart
from app.services.order_service import create_order
from app.utils import roles_required

customer_bp = Blueprint("customer", __name__)


@customer_bp.post("/cart/add/<int:product_id>")
def cart_add(product_id):
    product = db.get_or_404(Product, product_id)
    quantity = max(1, request.form.get("quantity", 1, type=int))
    if not product.is_active or product.stock < quantity:
        flash("Sản phẩm không đủ tồn kho.", "danger")
    else:
        add_to_cart(product.id, quantity)
        flash("Đã thêm sản phẩm vào giỏ.", "success")
    return redirect(request.referrer or url_for("main.products"))


@customer_bp.route("/cart")
def cart():
    items, total = cart_details()
    return render_template("customer/cart.html", items=items, total=total)


@customer_bp.post("/cart/update/<int:product_id>")
def cart_update(product_id):
    product = db.get_or_404(Product, product_id)
    quantity = request.form.get("quantity", 1, type=int)
    update_cart(product_id, min(quantity, product.stock))
    flash("Đã cập nhật giỏ hàng.", "success")
    return redirect(url_for("customer.cart"))


@customer_bp.post("/cart/remove/<int:product_id>")
def cart_remove(product_id):
    remove_from_cart(product_id)
    return redirect(url_for("customer.cart"))


@customer_bp.route("/checkout", methods=["GET", "POST"])
@login_required
@roles_required("customer")
def checkout():
    items, total = cart_details()
    if not items:
        flash("Giỏ hàng đang trống.", "warning")
        return redirect(url_for("customer.cart"))
    form = CheckoutForm()
    if form.validate_on_submit():
        try:
            order = create_order(
                current_user, form.shipping_address.data, form.phone.data, form.payment_method.data
            )
            session["cart"] = {}
            flash(f"Đặt hàng #{order.id} thành công.", "success")
            return redirect(url_for("customer.orders"))
        except ValueError as error:
            db.session.rollback()
            flash(str(error), "danger")
    return render_template("customer/checkout.html", form=form, items=items, total=total)


@customer_bp.route("/orders")
@login_required
@roles_required("customer")
def orders():
    order_list = db.session.scalars(
        db.select(Order).where(Order.customer_id == current_user.id).order_by(Order.created_at.desc())
    ).all()
    return render_template("customer/orders.html", orders=order_list)


@customer_bp.route("/review/<int:product_id>", methods=["GET", "POST"])
@login_required
@roles_required("customer")
def review(product_id):
    product = db.get_or_404(Product, product_id)
    purchased = db.session.scalar(
        db.select(OrderItem.id)
        .join(Order)
        .where(Order.customer_id == current_user.id, OrderItem.product_id == product_id)
    )
    if not purchased:
        flash("Bạn chỉ có thể đánh giá sản phẩm đã mua.", "warning")
        return redirect(url_for("main.product_detail", product_id=product_id))
    existing = db.session.scalar(
        db.select(Review).where(
            Review.customer_id == current_user.id, Review.product_id == product_id
        )
    )
    form = ReviewForm(obj=existing)
    if form.validate_on_submit():
        review_record = existing or Review(customer_id=current_user.id, product_id=product_id)
        review_record.rating = form.rating.data
        review_record.comment = form.comment.data
        db.session.add(review_record)
        db.session.commit()
        flash("Cảm ơn đánh giá của bạn.", "success")
        return redirect(url_for("main.product_detail", product_id=product_id))
    return render_template("customer/review.html", form=form, product=product)

