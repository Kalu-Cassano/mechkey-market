import os
from urllib.parse import quote_plus

from dotenv import load_dotenv

load_dotenv(override=True)


def build_database_uri():
    driver = os.getenv("DB_DRIVER", "ODBC Driver 18 for SQL Server")
    server = os.getenv("DB_SERVER", r"localhost\SQLEXPRESS")
    database = os.getenv("DB_NAME", "MarketplaceDB")
    trusted = os.getenv("DB_TRUSTED_CONNECTION", "yes").lower() == "yes"
    trust_certificate = os.getenv("DB_TRUST_SERVER_CERTIFICATE", "yes")
    encrypt = os.getenv("DB_ENCRYPT", "no")

    parts = [
        f"DRIVER={{{driver}}}",
        f"SERVER={server}",
        f"DATABASE={database}",
        f"Encrypt={encrypt}",
        f"TrustServerCertificate={trust_certificate}",
    ]
    if trusted:
        parts.append("Trusted_Connection=yes")
    else:
        parts.extend(
            [
                f"UID={os.getenv('DB_USERNAME', '')}",
                f"PWD={os.getenv('DB_PASSWORD', '')}",
            ]
        )
    return "mssql+pyodbc:///?odbc_connect=" + quote_plus(";".join(parts))


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = build_database_uri()
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024
    UPLOAD_FOLDER = os.path.join("app", "static", "uploads", "products")


class TestConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
