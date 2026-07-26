from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user

from app.extensions import db
from app.forms import LoginForm, RegisterForm
from app.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.lower().strip()
        if db.session.scalar(db.select(User).where(User.email == email)):
            flash("Email này đã được sử dụng.", "danger")
        elif form.role.data == "vendor" and not form.store_name.data:
            flash("Người bán cần nhập tên cửa hàng.", "danger")
        else:
            user = User(
                full_name=form.full_name.data.strip(),
                email=email,
                role=form.role.data,
                store_name=form.store_name.data.strip() if form.store_name.data else None,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash("Đăng ký thành công. Bạn có thể đăng nhập.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(db.select(User).where(User.email == form.email.data.lower().strip()))
        if user and user.check_password(form.password.data) and user.is_active:
            login_user(user, remember=form.remember.data)
            target = request.args.get("next")
            return redirect(target or url_for("main.index"))
        flash("Email hoặc mật khẩu không đúng.", "danger")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    logout_user()
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("main.index"))

