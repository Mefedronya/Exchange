# test_sa.py
from database import engine
from sqlalchemy import text
print("🔄 Тест SQLAlchemy подключения...")
try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT @@VERSION"))  # ← text() обязателен
        version = result.fetchone()[0]
        print("✅ SQLAlchemy подключился успешно!")
        print(f"📦 {version[:60]}...")
        
        # Дополнительно: проверим базу данных
        result = conn.execute(text("SELECT DB_NAME()"))
        db_name = result.fetchone()[0]
        print(f"💾 Текущая БД: {db_name}")
        
except Exception as e:
    print(f"❌ Ошибка: {e}")
