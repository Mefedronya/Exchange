from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc
import os

# raw connection string for use with pyodbc; keep in sync with SQLALCHEMY_DATABASE_URL

DB_CONFIG = {
    "server": os.getenv("DB_SERVER", "DESKTOP-P5B9MPU\\SQLEXPRESS"),
    "database": os.getenv("DB_NAME", "it_planet"),
    "username": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
    "trust_cert": os.getenv("DB_TRUST_CERT", "yes").lower() == "yes",
}
DB_CONNECTION_STRING = (
    f"DRIVER={{{DB_CONFIG['driver']}}};"
    f"SERVER={DB_CONFIG['server']};"
    f"DATABASE={DB_CONFIG['database']};"
    f"UID={DB_CONFIG['username']};"
    f"PWD={DB_CONFIG['password']};"
    f"TrustServerCertificate={'yes' if DB_CONFIG['trust_cert'] else 'no'};"
)

class DBManager:
    """Simple helper providing a context-managed pyodbc connection."""

    def __init__(self, conn_str: str):
        self._conn_str = conn_str

    def get_connection(self):
        # pyodbc.Connection is itself a context manager
        return pyodbc.connect(self._conn_str)


# single shared instance for import
db_manager = DBManager(DB_CONNECTION_STRING)

SQLALCHEMY_DATABASE_URL = (
    "mssql+pyodbc://DESKTOP-P5B9MPU\\SQLEXPRESS/it_planet?"
    "driver=ODBC+Driver+17+for+SQL+Server&"
)

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True  
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
def _create_pyodbc_connection():
    """Фабрика подключений для SQLAlchemy через pyodbc."""
    return pyodbc.connect(DB_CONNECTION_STRING)