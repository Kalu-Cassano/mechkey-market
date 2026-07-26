from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from wtforms import (
    BooleanField,
    DecimalField,
    IntegerField,
    PasswordField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange, Optional


class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField("Mật khẩu", validators=[DataRequired()])
    remember = BooleanField("Ghi nhớ đăng nhập")
    submit = SubmitField("Đăng nhập")


class RegisterForm(FlaskForm):
    full_name = StringField("Họ và tên", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=255)])
    role = SelectField(
        "Loại tài khoản",
        choices=[("customer", "Người mua"), ("vendor", "Người bán")],
        validators=[DataRequired()],
    )
    store_name = StringField("Tên cửa hàng", validators=[Optional(), Length(max=120)])
    password = PasswordField("Mật khẩu", validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(
        "Nhập lại mật khẩu", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Đăng ký")


class ProductForm(FlaskForm):
    name = StringField("Tên sản phẩm", validators=[DataRequired(), Length(max=160)])
    category_id = SelectField("Danh mục", coerce=int, validators=[DataRequired()])
    description = TextAreaField("Mô tả", validators=[Optional(), Length(max=4000)])
    price = DecimalField("Giá", places=2, validators=[DataRequired(), NumberRange(min=0)])
    stock = IntegerField("Tồn kho", validators=[DataRequired(), NumberRange(min=0)])
    image = FileField(
        "Ảnh sản phẩm",
        validators=[Optional(), FileAllowed(["jpg", "jpeg", "png", "webp"], "Chỉ chấp nhận ảnh.")],
    )
    is_active = BooleanField("Đang bán", default=True)
    submit = SubmitField("Lưu sản phẩm")


class CheckoutForm(FlaskForm):
    shipping_address = TextAreaField(
        "Địa chỉ giao hàng", validators=[DataRequired(), Length(min=10, max=500)]
    )
    phone = StringField("Số điện thoại", validators=[DataRequired(), Length(min=8, max=30)])
    payment_method = RadioField(
        "Thanh toán",
        choices=[("COD", "Thanh toán khi nhận hàng"), ("BANK", "Chuyển khoản mô phỏng")],
        default="COD",
        validators=[DataRequired()],
    )
    submit = SubmitField("Đặt hàng")


class ReviewForm(FlaskForm):
    rating = SelectField(
        "Số sao",
        choices=[(5, "5 - Tuyệt vời"), (4, "4 - Tốt"), (3, "3 - Khá"), (2, "2 - Tạm"), (1, "1 - Kém")],
        coerce=int,
        validators=[DataRequired()],
    )
    comment = TextAreaField("Nhận xét", validators=[Optional(), Length(max=1000)])
    submit = SubmitField("Gửi đánh giá")

