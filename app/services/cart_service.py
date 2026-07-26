from decimal import Decimal

from flask import session

from app.extensions import db
from app.models import Product


def get_cart():
    return session.setdefault("cart", {})


def add_to_cart(product_id, quantity=1):
    cart = get_cart()
    key = str(product_id)
    cart[key] = cart.get(key, 0) + quantity
    session.modified = True


def update_cart(product_id, quantity):
    cart = get_cart()
    key = str(product_id)
    if quantity <= 0:
        cart.pop(key, None)
    else:
        cart[key] = quantity
    session.modified = True


def remove_from_cart(product_id):
    cart = get_cart()
    cart.pop(str(product_id), None)
    session.modified = True


def cart_details():
    cart = get_cart()
    ids = [int(value) for value in cart.keys()]
    products = db.session.scalars(db.select(Product).where(Product.id.in_(ids))).all() if ids else []
    items, total = [], Decimal("0")
    for product in products:
        quantity = min(int(cart[str(product.id)]), product.stock)
        subtotal = Decimal(product.price) * quantity
        items.append({"product": product, "quantity": quantity, "subtotal": subtotal})
        total += subtotal
    return items, total

