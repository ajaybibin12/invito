from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.user import User
from app.core.config import settings


def create_admin_if_not_exists(db: Session):
    admin_email = settings.ADMIN_EMAIL
    admin_password = settings.ADMIN_PASSWORD
    admin_role = settings.ADMIN_ROLE

    if not admin_email or not admin_password:
        print("⚠️ Admin credentials not set. Skipping admin creation.")
        return

    admin = db.query(User).filter(User.email == admin_email).first()

    if admin:
        print("✅ Admin already exists.")
        return

    new_admin = User(
        email=admin_email,
        hashed_password=get_password_hash(admin_password),
        role=admin_role,
        is_active=True,
    )

    db.add(new_admin)
    db.commit()
    db.refresh(new_admin)

    print(f"🚀 Admin user created: {admin_email}")
