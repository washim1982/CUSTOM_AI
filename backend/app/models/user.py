# backend/app/models/user.py

from sqlalchemy import Column, Integer, String
from pydantic import BaseModel
from typing import Optional

from app.core.database import Base

# --- SQLAlchemy Model ---
# This defines the 'users' table in your database.
class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)

# --- Pydantic Models ---
# These define the shape of data for API requests and responses.

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str
    firstName: str | None = None
    lastName: str | None = None

# This is the missing class that the error is referring to.
# It defines the data returned to the client (without the password).
class User(UserBase):
    id: int

    class Config:
        from_attributes = True # Allows Pydantic to read data from ORM models

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
