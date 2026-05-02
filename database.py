from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# For Homebrew PostgreSQL, the default connection URL requires no password and infers your OS username.
SQLALCHEMY_DATABASE_URL = "postgresql://localhost/movie_reservation_db"

# The engine establishes the core TCP connection to the PostgreSQL database.
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# SessionLocal is a factory that generates new database sessions for each request.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base is the parent class for your ORM models.
Base = declarative_base()

# Manage Database Sessions

# This function creates a new database session when a request arrives,
# yields it to the route, and guarantees the session is closed when the request finishes, 
# even if an exception occurs.

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()