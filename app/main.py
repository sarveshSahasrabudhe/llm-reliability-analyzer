from fastapi import FastAPI
from logging_config import setup_logging
from app.routes import runs
from db.models import Base
from db.session import engine

# Create tables on startup (simple approach for dev)
Base.metadata.create_all(bind=engine)

logger = setup_logging()

app = FastAPI(title="LLM Reliability Analyzer", version="0.1.0")

app.include_router(runs.router, tags=["runs"])

@app.get("/")
def read_root():
    logger.info("Root endpoint called")
    return {"message": "Welcome to LLM Failure & Reliability Analyzer"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
