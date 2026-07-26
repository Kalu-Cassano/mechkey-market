# MechKey Market — Multi-Vendor Marketplace

Đồ án Flask + Bootstrap 5 + Microsoft SQL Server dành cho môn Hệ quản trị cơ sở dữ liệu.

Hướng dẫn chi tiết cho máy mới: [HUONG_DAN_CAI_DAT.md](HUONG_DAN_CAI_DAT.md)

## Chức năng

- Đăng ký, đăng nhập và ba vai trò: customer, vendor, admin.
- Danh mục, tìm kiếm, sản phẩm, tồn kho và ảnh sản phẩm.
- Giỏ hàng, checkout mô phỏng, lịch sử đơn và đánh giá.
- Thanh toán COD/chuyển khoản mô phỏng, có trạng thái và mã giao dịch.
- Người bán xác nhận, huỷ, giao và hoàn tất phần đơn hàng của cửa hàng.
- Dashboard người bán và trang quản trị.
- SQL schema, seed, view, stored procedure và ERD.

## 1. Chuẩn bị

Cài Python 3.11+, SQL Server, SSMS và **ODBC Driver 18 for SQL Server**.

Trong SSMS, chạy lần lượt:

1. `database/schema/01_create_database.sql`
2. `database/schema/02_create_tables.sql`
3. `database/seed/01_categories.sql`
4. Các script trong `database/views/` và `database/procedures/`

Không chạy script tạo bảng nhiều lần trên cùng database.

Nếu `MarketplaceDB` đã được tạo từ phiên bản cũ, chỉ chạy thêm một lần:

```text
database/schema/03_upgrade_payments_vendor_status.sql
```

## 2. Cấu hình Python

Trong PowerShell tại thư mục dự án:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Mở `.env` và sửa `DB_SERVER` đúng với **Server name** hiển thị trong SSMS,
ví dụ `DESKTOP-ABC\SQLEXPRESS`.

Windows Authentication:

```env
DB_TRUSTED_CONNECTION=yes
```

SQL Server Authentication:

```env
DB_TRUSTED_CONNECTION=no
DB_USERNAME=your_username
DB_PASSWORD=your_password
```

## 3. Dữ liệu demo và chạy ứng dụng

Sau khi đã tạo bảng bằng SSMS:

```powershell
python -m scripts.seed_demo
python run.py
```

Truy cập `http://127.0.0.1:5000`.

Tài khoản demo:

| Vai trò | Email | Mật khẩu |
|---|---|---|
| Admin | admin@unimarket.com | Admin123! |
| Vendor | vendor@unimarket.com | Vendor123! |
| Customer | customer@unimarket.com | Customer123! |

Các mật khẩu này chỉ dành cho môi trường demo.

## 4. Chạy kiểm tra

```powershell
pytest
```

Tests dùng SQLite trong bộ nhớ, vì vậy không làm thay đổi dữ liệu SQL Server.

## Ghi chú kết nối

Flask kết nối trực tiếp tới SQL Server qua SQLAlchemy và pyodbc; SSMS là công cụ
quản trị cùng database đó. ODBC Driver 18 mã hóa mặc định, nên cấu hình phát triển
cục bộ dùng `TrustServerCertificate=yes`.
