import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
# Use SQLite for development, PostgreSQL for production
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./qa_risk.db" if os.getenv("ENV", "development") == "development" else "postgresql://user:password@localhost:5432/qa_risk_db"
)

# API Configuration
API_KEY = os.getenv("OPENAI_API_KEY", "")

# Environment
ENV = os.getenv("ENV", "development")
