from app.extensions import db
from app.models import Order, OrderItem, Payment
from .cart_service import cart_details


def create_order(customer, shipping_address, phone, payment_method):
    items, total = cart_details()
    if not items:
        raise ValueError("Giỏ hàng đang trống.")

    order = Order(
        customer=customer,
        shipping_address=shipping_address,
        phone=phone,
        payment_method=payment_method,
        total_amount=total,
    )
    db.session.add(order)

    for item in items:
        product = item["product"]
        quantity = item["quantity"]
        if not product.is_active or quantity <= 0 or product.stock < quantity:
            raise ValueError(f"Sản phẩm '{product.name}' không đủ tồn kho.")
        product.stock -= quantity
        order.items.append(
            OrderItem(
                product=product,
                vendor_id=product.vendor_id,
                product_name=product.name,
                unit_price=product.price,
                quantity=quantity,
                status="Pending",
            )
        )
    payment = Payment(
        order=order,
        method=payment_method,
        status="Paid" if payment_method == "BANK" else "Pending",
        amount=total,
    )
    if payment_method == "BANK":
        from datetime import datetime, timezone
        from uuid import uuid4

        payment.transaction_code = f"SIM-{uuid4().hex[:12].upper()}"
        payment.paid_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.session.add(payment)
    db.session.commit()
    return order


def sync_order_status(order):
    from datetime import datetime, timezone
    from uuid import uuid4

    statuses = {item.status for item in order.items}
    if statuses == {"Cancelled"}:
        order.status = "Cancelled"
    elif statuses == {"Completed"}:
        order.status = "Completed"
    elif "Shipping" in statuses or "Completed" in statuses:
        order.status = "Shipping"
    elif "Confirmed" in statuses:
        order.status = "Confirmed"
    else:
        order.status = "Pending"

    if order.payment:
        if order.status == "Completed" and order.payment.method == "COD":
            order.payment.status = "Paid"
            order.payment.transaction_code = order.payment.transaction_code or f"COD-{uuid4().hex[:12].upper()}"
            order.payment.paid_at = datetime.now(timezone.utc).replace(tzinfo=None)
        elif order.status == "Cancelled" and order.payment.status == "Pending":
            order.payment.status = "Cancelled"
