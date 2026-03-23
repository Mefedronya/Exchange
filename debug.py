# debug_db.py
import os
from dotenv import load_dotenv
import pyodbc

load_dotenv()

print("=" * 60)
print("🔍 ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ К БД")
print("=" * 60)

# Показываем переменные (пароль маскируем)
print(f"\n📋 Переменные окружения:")
print(f"  DB_SERVER: {os.getenv('DB_SERVER', 'NOT SET')}")
print(f"  DB_PORT: {os.getenv('DB_PORT', 'NOT SET')}")
print(f"  DB_NAME: {os.getenv('DB_NAME', 'NOT SET')}")
print(f"  DB_USER: {os.getenv('DB_USER', 'NOT SET')}")
print(f"  DB_PASSWORD: {'****' if os.getenv('DB_PASSWORD') else 'NOT SET'}")
print(f"  DB_DRIVER: {os.getenv('DB_DRIVER', 'NOT SET')}")
print(f"  DB_TRUST_CERT: {os.getenv('DB_TRUST_CERT', 'NOT SET')}")

# Проверяем драйверы
print(f"\n📦 Доступные ODBC драйверы:")
try:
    drivers = pyodbc.drivers()
    sql_drivers = [d for d in drivers if 'SQL Server' in d]
    for driver in sql_drivers:
        print(f"  ✅ {driver}")
    if not sql_drivers:
        print(f"  ❌ Драйверы SQL Server не найдены!")
except Exception as e:
    print(f"  ❌ Ошибка: {e}")

# Формируем строку подключения
DB_CONFIG = {
    "server": os.getenv("DB_SERVER", "localhost"),
    "database": os.getenv("DB_NAME", "it_planet"),
    "username": os.getenv("DB_USER", "sa"),
    "password": os.getenv("DB_PASSWORD", ""),
    "driver": os.getenv("DB_DRIVER", "ODBC Driver 17 for SQL Server"),
    "trust_cert": os.getenv("DB_TRUST_CERT", "yes").lower() == "yes",
    "DB_PORT": os.getenv("DB_PORT", "1433"),
}

conn_str = (
    f"DRIVER={{{DB_CONFIG['driver']}}};"
    f"SERVER={DB_CONFIG['server']},{DB_CONFIG['DB_PORT']};"
    f"DATABASE={DB_CONFIG['database']};"
    f"UID={DB_CONFIG['username']};"
    f"PWD={DB_CONFIG['password']};"
    f"TrustServerCertificate={'yes' if DB_CONFIG['trust_cert'] else 'no'};"
    f"Connection Timeout=30;"
)

print(f"\n🔗 Строка подключения (без пароля):")
safe_str = conn_str.replace(DB_CONFIG['password'], '****')
print(f"  {safe_str}")

# Пробуем подключиться
print(f"\n🔄 Попытка подключения...")
try:
    conn = pyodbc.connect(conn_str)
    print(f"✅ ПОДКЛЮЧЕНИЕ УСПЕШНО!")
    
    cursor = conn.cursor()
    cursor.execute("SELECT @@VERSION")
    version = cursor.fetchone()[0]
    print(f"\n📦 Версия SQL Server:")
    print(f"  {version[:80]}...")
    
    cursor.execute("SELECT name FROM sys.databases")
    databases = [row[0] for row in cursor.fetchall()]
    print(f"\n💾 Доступные базы данных:")
    for db in databases:
        marker = "← ТЕКУЩАЯ" if db == DB_CONFIG['database'] else ""
        print(f"  {db} {marker}")
    
    conn.close()
    
except pyodbc.Error as e:
    print(f"❌ ОШИБКА ПОДКЛЮЧЕНИЯ:")
    print(f"  {str(e)}")
    
    # Дополнительные проверки
    print(f"\n🔧 Рекомендации:")
    print(f"  1. Проверьте, что контейнер запущен: docker ps | grep sqlserver")
    print(f"  2. Проверьте логи: docker logs sqlserver | tail -20")
    print(f"  3. Проверьте порт: ss -tlnp | grep 1433")
    print(f"  4. Попробуйте sqlcmd: sqlcmd -S localhost,1433 -U sa -P 'Nikitos123!' -C -Q 'SELECT 1'")
    
except Exception as e:
    print(f"❌ НЕИЗВЕСТНАЯ ОШИБКА: {type(e).__name__}: {e}")

print("=" * 60)
