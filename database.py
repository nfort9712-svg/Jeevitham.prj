from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

# Use environment variables for safety
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:Chidhu%40123@localhost/project")

engine = create_engine(DATABASE_URL, echo=True)  # echo=True for SQL logging in dev
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
