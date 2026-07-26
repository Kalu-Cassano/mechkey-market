# Hướng dẫn cài đặt và chạy MechKey Market

Tài liệu này dành cho người tải project lần đầu từ GitHub trên máy Windows.

Repository:

```text
https://github.com/Kalu-Cassano/mechkey-market
```

## 1. Phần mềm cần cài

- Git
- Python 3.11 hoặc Python 3.12
- Microsoft SQL Server Developer hoặc Express
- SQL Server Management Studio (SSMS)
- Microsoft ODBC Driver 18 for SQL Server
- Visual Studio Code

Khi cài Python, nên chọn **Add Python to PATH**.

## 2. Tải source code

Mở PowerShell:

```powershell
git clone https://github.com/Kalu-Cassano/mechkey-market.git
cd mechkey-market
```

Nếu đã clone trước đó:

```powershell
git pull origin main
```

## 3. Kết nối SQL Server trong SSMS

Mở SSMS và chọn **Connect → Database Engine**.

Thiết lập khuyến nghị:

```text
Server Name: localhost
Authentication: Windows Authentication
Database Name: <default>
Encrypt: Mandatory
Trust Server Certificate: bật
```

Không chọn `(localdb)\MSSQLLocalDB` nếu file `.env` dùng `localhost`.

Nếu máy sử dụng SQL Server Express, Server Name có thể là:

```text
localhost\SQLEXPRESS
```

## 4. Tạo database

Trong SSMS, mở và Execute lần lượt:

1. `database/schema/01_create_database.sql`
2. `database/schema/02_create_tables.sql`
3. `database/seed/01_categories.sql`
4. `database/views/01_vendor_sales_summary.sql`
5. `database/procedures/01_get_vendor_orders.sql`

Không cần chạy `03_upgrade_payments_vendor_status.sql` khi tạo database mới.
File `03` chỉ dùng để nâng cấp database được tạo từ phiên bản cũ.

Kiểm tra:

```sql
USE MarketplaceDB;
GO

SELECT name
FROM sys.tables
ORDER BY name;
```

Kết quả cần có:

```text
categories
order_items
orders
payments
products
reviews
users
```

## 5. Tạo môi trường Python

Trong PowerShell tại thư mục project:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Nếu PowerShell chặn việc kích hoạt:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Khi kích hoạt thành công, đầu dòng terminal sẽ có `(.venv)`.

## 6. Tạo file cấu hình

```powershell
Copy-Item .env.example .env
```

Mở `.env` và cấu hình:

```env
SECRET_KEY=thay-bang-mot-chuoi-bi-mat-rieng
DB_SERVER=localhost
DB_NAME=MarketplaceDB
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUSTED_CONNECTION=yes
DB_TRUST_SERVER_CERTIFICATE=yes
DB_ENCRYPT=yes
```

Nếu SSMS kết nối bằng `localhost\SQLEXPRESS`, sửa:

```env
DB_SERVER=localhost\SQLEXPRESS
```

Không commit file `.env` lên GitHub.

## 7. Tạo dữ liệu demo

Sau khi tạo bảng trong SSMS:

```powershell
python -m scripts.seed_demo
```

Tài khoản demo:

| Vai trò | Email | Mật khẩu |
|---|---|---|
| Admin | `admin@unimarket.com` | `Admin123!` |
| Người bán | `vendor@unimarket.com` | `Vendor123!` |
| Khách hàng | `customer@unimarket.com` | `Customer123!` |

Mật khẩu phân biệt chữ hoa/chữ thường và kết thúc bằng dấu `!`.

## 8. Kiểm tra kết nối

```powershell
python -m scripts.check_connection
```

Kết quả cần có:

```text
Configured server: localhost
Expected driver: ODBC Driver 18 for SQL Server
Database: MarketplaceDB
```

Khi script hỏi email, có thể nhấn Enter để bỏ qua.

## 9. Chạy website

```powershell
python run.py
```

Mở trình duyệt:

```text
http://127.0.0.1:5000
```

Nhấn `Ctrl + C` trong terminal để dừng server.

## 10. Kiểm tra dữ liệu trong SSMS

```sql
USE MarketplaceDB;
GO

SELECT * FROM dbo.users ORDER BY id DESC;
SELECT * FROM dbo.products ORDER BY id DESC;
SELECT * FROM dbo.orders ORDER BY id DESC;
SELECT * FROM dbo.order_items ORDER BY id DESC;
SELECT * FROM dbo.payments ORDER BY id DESC;
SELECT * FROM dbo.reviews ORDER BY id DESC;
```

SSMS không tự cập nhật bảng kết quả. Hãy nhấn **Execute** lại để xem dữ liệu mới.

## 11. Các lỗi thường gặp

### `No module named app`

Terminal đang đứng sai thư mục. Chạy:

```powershell
cd đường-dẫn-đến\mechkey-market
```

Thư mục hiện tại phải chứa `app`, `run.py` và `requirements.txt`.

### Không thấy bảng hoặc dữ liệu trong SSMS

Kiểm tra Object Explorer đang kết nối `localhost`, không phải
`(localdb)\MSSQLLocalDB`.

### `ODBC Driver 18 ... not found`

Cài **Microsoft ODBC Driver 18 for SQL Server (x64)** và mở lại terminal.

### Lỗi chứng chỉ hoặc mã hóa

Kiểm tra `.env`:

```env
DB_TRUST_SERVER_CERTIFICATE=yes
DB_ENCRYPT=yes
```

### Cổng 5000 đang được sử dụng

Dừng Flask cũ bằng `Ctrl + C`. Nếu cần:

```powershell
Get-NetTCPConnection -LocalPort 5000 -State Listen -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty OwningProcess -Unique |
    ForEach-Object { Stop-Process -Id $_ -Force }
```

### Ảnh sản phẩm không có sau khi clone

Ảnh upload local không được lưu trên GitHub. Người dùng cần upload ảnh mới, hoặc
nhận riêng thư mục:

```text
app/static/uploads/products/
```

## 12. Ghi chú

- Thanh toán ngân hàng trong project là mô phỏng, không phát sinh giao dịch thật.
- GitHub chứa code và script tạo database, không chứa dữ liệu SQL Server của máy tác giả.
- Đây là sản phẩm phục vụ môn Hệ quản trị cơ sở dữ liệu.

