from app.database import SessionLocal
from app.models import User, UserRole
from app.auth.security import get_password_hash

db = SessionLocal()
username = "admin"
password = "password"  # <-- Set your desired password here

user = db.query(User).filter(User.username == username).first()
if user:
    user.hashed_password = get_password_hash(password)
    user.role = UserRole.ADMIN
    user.is_active = True
    user.is_verified = True
    db.commit()
    print(f"Admin user '{username}' password reset to '{password}'.")
else:
    from app.models import User
    user = User(
        username=username,
        email="admin@example.com",
        full_name="Administrator",
        hashed_password=get_password_hash(password),
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True
    )
    db.add(user)
    db.commit()
    print(f"Admin user '{username}' created with password '{password}'.")
db.close()