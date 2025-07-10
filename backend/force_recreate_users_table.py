from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.execute(text("DROP TABLE IF EXISTS users"))
    print("Dropped users table (if it existed).")