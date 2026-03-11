from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyodbc

# raw connection string for use with pyodbc; keep in sync with SQLALCHEMY_DATABASE_URL
DB_CONNECTION_STRING = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=DESKTOP-P5B9MPU\\SQLEXPRESS;"
    "DATABASE=it_planet;"
    "Trusted_Connection=yes;"
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
    "mssql+pyodbc://DESKTOP-P5B9MPU\\SQLEXPRESS/it_planet"
    "driver=ODBC+Driver+17+for+SQL+Server&"
    "trusted_connection=yes"
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