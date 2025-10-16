from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# IMPORTANT: Replace with your actual PostgreSQL connection details
# For local development, it might be "postgresql://localhost/proximity_db"
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@hostname/dbname"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get a DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
