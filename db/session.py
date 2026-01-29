from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# SQLite database file
DATABASE_URL = "sqlite:///./llm_reliability.db"

# Create engine
engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} # Needed for SQLite + FastAPI/Async
)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Scoped session for thread safety
db_session = scoped_session(SessionLocal)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
