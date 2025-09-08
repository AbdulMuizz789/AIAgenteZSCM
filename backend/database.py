# -------------------------------------------------------------------------
# database.py - SQLAlchemy setup
# -------------------------------------------------------------------------
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Replace with your PostgreSQL connection string
SQLALCHEMY_DATABASE_URL = f"{os.getenv('DATABASE_URL')}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()