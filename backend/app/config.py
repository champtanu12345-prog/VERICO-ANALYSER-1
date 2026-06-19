import os
from dotenv import load_dotenv

load_dotenv()

# Database Configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/qa_risk_db"
)

# For development with SQLite as fallback
# DATABASE_URL = "sqlite:///./qa_risk.db"

# API Configuration
API_KEY = os.getenv("OPENAI_API_KEY", "")

# Environment
ENV = os.getenv("ENV", "development")
