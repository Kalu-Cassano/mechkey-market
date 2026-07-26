from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app import create_app
from app.extensions import db
from app.models import User


app = create_app()

print(f"Configured server: {app.config['SQLALCHEMY_DATABASE_URI'].split('SERVER%3D')[1].split('%3B')[0] if 'SERVER%3D' in app.config['SQLALCHEMY_DATABASE_URI'] else 'unknown'}")
print("Expected driver: ODBC Driver 18 for SQL Server")

try:
    with app.app_context():
        database_name = db.session.execute(text("SELECT DB_NAME()")).scalar()
        driver_name = db.session.execute(
            text("SELECT client_interface_name FROM sys.dm_exec_sessions WHERE session_id = @@SPID")
        ).scalar()
        print(f"Database: {database_name}")
        print(f"Connection driver: {driver_name}")

        email = input("Email can kiem tra (Enter de bo qua): ").strip().lower()
        if email:
            account = db.session.scalar(db.select(User).where(User.email == email))
            if account:
                print("Account: FOUND")
                print(f"ID: {account.id}")
                print(f"Full name: {account.full_name}")
                print(f"Role: {account.role}")
                print(f"Active: {account.is_active_account}")
            else:
                print("Account: NOT FOUND")
except SQLAlchemyError as error:
    print("Database connection: FAILED")
    print(f"Error: {error.orig if hasattr(error, 'orig') else error}")
    raise SystemExit(1)
