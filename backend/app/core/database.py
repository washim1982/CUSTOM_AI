# backend/app/core/database.py

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# --- SQLite Configuration ---
# Create the data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

# The path points to a file inside the container at /code/data/app.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/app.db"

# The 'connect_args' is required for SQLite to work with FastAPI
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# --- The Missing Function ---
# This is a dependency for FastAPI routes to get a DB session.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()