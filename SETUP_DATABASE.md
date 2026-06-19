# Database Setup Guide

## Overview

The project now includes a PostgreSQL database for storing:
- **Documents**: Uploaded PDF files and metadata
- **Users**: User information and session tracking
- **QA Interactions**: Question-answer pairs with confidence scores
- **Risk Assessments**: Risk detection results and analysis

## Quick Start

### 1. Install Dependencies

The required packages have been added to `requirements.txt`:
- `sqlalchemy` - ORM for database operations
- `psycopg2-binary` - PostgreSQL driver
- `python-dotenv` - Environment variable management

```bash
pip install -r requirements.txt
```

### 2. Configure Database

#### Option A: PostgreSQL (Recommended for Production)

1. Install PostgreSQL (if not already installed)
2. Create a database:
   ```bash
   createdb qa_risk_db
   ```

3. Copy `.env.example` to `.env` and update with your credentials:
   ```env
   DATABASE_URL=postgresql://username:password@localhost:5432/qa_risk_db
   OPENAI_API_KEY=your_api_key_here
   ```

#### Option B: SQLite (For Development)

SQLite requires no setup and works locally. Uncomment this in `.env`:
```env
DATABASE_URL=sqlite:///./qa_risk.db
```

### 3. Initialize Database

The database tables are automatically created when the FastAPI app starts. The `init_db()` function runs on startup and creates all tables based on the SQLAlchemy models.

### 4. Run Backend

```bash
uvicorn app.main:app --reload
```

The database will be initialized automatically. Check the health endpoint to confirm:
```bash
curl http://localhost:8000/health
```

## Database Schema

### Documents Table
- `id`: Primary key
- `filename`: Original file name
- `file_path`: Path to stored file
- `upload_date`: When uploaded
- `file_size`: Size in bytes
- `status`: processing/processed/failed
- `user_id`: Associated user (optional)

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Optional email
- `created_at`: Account creation date
- `last_login`: Last login timestamp

### QA Interactions Table
- `id`: Primary key
- `document_id`: Reference to document
- `user_id`: Reference to user (optional)
- `question`: User's question
- `answer`: LLM generated answer
- `confidence`: Answer confidence score (0-1)
- `created_at`: When Q&A occurred
- `metadata`: Additional JSON data

### Risk Assessments Table
- `id`: Primary key
- `document_id`: Reference to document
- `risk_level`: low/medium/high/critical
- `risk_score`: Numerical score (0-1)
- `identified_risks`: JSON list of risk categories
- `detailed_analysis`: Detailed findings
- `created_at`: When assessment was performed
- `updated_at`: Last update time

## API Usage

### Store QA Result
```python
from app import crud, schemas
from app.database import SessionLocal

db = SessionLocal()

# Create QA interaction
qa_data = schemas.QAInteractionCreate(
    document_id=1,
    question="What are the main risks?",
    answer="The document identifies...",
    confidence=0.95
)
crud.create_qa_interaction(db, qa_data)
```

### Retrieve Document History
```python
document = crud.get_document(db, document_id=1)
qa_history = crud.get_qa_interactions(db, document_id=1)
risk_results = crud.get_all_risk_assessments(db, document_id=1)
```

## Docker Setup

If using Docker Compose, add a PostgreSQL service to `docker-compose.yml`:

```yaml
db:
  image: postgres:15-alpine
  environment:
    POSTGRES_USER: user
    POSTGRES_PASSWORD: password
    POSTGRES_DB: qa_risk_db
  volumes:
    - postgres_data:/var/lib/postgresql/data
  ports:
    - "5432:5432"

volumes:
  postgres_data:
```

Update the DATABASE_URL in your `.env` file accordingly.

## Troubleshooting

**Connection Error**: Ensure PostgreSQL is running and credentials are correct
**Import Error**: Run `pip install -r requirements.txt` to install SQLAlchemy
**Table Creation Failed**: Check database permissions and ensure the database exists

## Next Steps

1. Integrate database storage into your endpoints in `app/api/endpoints.py`
2. Add user authentication if needed
3. Create database backups for production
4. Consider adding indexes for frequently queried fields
