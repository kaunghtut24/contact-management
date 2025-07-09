
import os
import sys
from sqlalchemy.orm import Session
try:
    from app.database import SessionLocal
    from app.models.user import User, UserRole
    from app.auth.security import get_password_hash
except ImportError:
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
    from app.database import SessionLocal
    from app.models.user import User, UserRole
    from app.auth.security import get_password_hash

ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')


def create_admin():
    db: Session = SessionLocal()
    try:
        user = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if user:
            print(f"Admin user '{ADMIN_USERNAME}' already exists.")
            return
        admin_user = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            full_name='Administrator',
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user '{ADMIN_USERNAME}' created successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
