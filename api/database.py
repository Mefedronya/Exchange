from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "server": os.getenv("DB_SERVER", "localhost"),
    "database": os.getenv("DB_NAME", "it_planet"),
    "username": os.getenv("DB_USER", "sa"),
    "password": os.getenv("DB_PASSWORD", "nikitos"),
    "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
    "trust_cert": os.getenv("DB_TRUST_CERT", "yes").lower() == "yes",
    "DB_PORT": os.getenv("DB_PORT", "1433")}
DB_CONNECTION_STRING = (
    f"DRIVER={{{DB_CONFIG['driver']}}};"
    f"SERVER={DB_CONFIG['server']},{DB_CONFIG['DB_PORT']};"
    f"DATABASE={DB_CONFIG['database']};"
    f"UID={DB_CONFIG['username']};"
    f"PWD={DB_CONFIG['password']};"
    f"TrustServerCertificate={'yes' if DB_CONFIG['trust_cert'] else 'no'};"
)
# raw connection string for use with pyodbc; keep in sync with SQLALCHEMY_DATABASE_URL

class DBManager:
    """Simple helper providing a context-managed pyodbc connection."""

    def __init__(self, conn_str: str):
        self._conn_str = conn_str

    def get_connection(self):
        # pyodbc.Connection is itself a context manager
        return pyodbc.connect(self._conn_str)


# single shared instance for import
db_manager = DBManager(DB_CONNECTION_STRING)

def simple_url_encode(s: str) -> str:
    """Простое экранирование без urllib"""
    return s.replace(" ", "+").replace(":", "%3A").replace(";", "%3B").replace("=", "%3D").replace("!", "%21")

encoded_conn_str = simple_url_encode(DB_CONNECTION_STRING)

SQLALCHEMY_DATABASE_URL = f"mssql+pyodbc:///?odbc_connect={simple_url_encode(DB_CONNECTION_STRING)}"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
pool_pre_ping=True,
pool_recycle=3600,
connect_args={"timeout":30	}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
