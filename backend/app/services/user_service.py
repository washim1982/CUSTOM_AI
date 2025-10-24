# backend/app/services/user_service.py

from sqlalchemy.orm import Session
from app.models import user as user_model
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str):
    """Fetches a single user by their email address."""
    return db.query(user_model.UserDB).filter(user_model.UserDB.email == email).first()

def create_user(db: Session, user: user_model.UserCreate):
    """Creates a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = user_model.UserDB(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# --- THIS IS THE MISSING FUNCTION ---
def authenticate_user(db: Session, email: str, password: str):
    """
    Authenticates a user. Returns the user object if successful, otherwise None.
    """
    user = get_user_by_email(db, email)
    if not user:
        # User not found
        return None
    if not verify_password(password, user.hashed_password):
        # Incorrect password
        return None
    
    # Authentication successful
    return user