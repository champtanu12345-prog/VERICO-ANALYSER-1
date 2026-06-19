# Multi-Document Question Answering & Risk Detection System

An end-to-end system for intelligent document analysis, capable of answering
questions from uploaded PDFs and automatically detecting risks using rules and
TensorFlow text classification.

## Features

- **Intelligent Chunking**: Recursive and overlapping text chunking for optimal context retrieval.
- **Document Search**: Lightweight hashed text features and cosine similarity.
- **LLM Question Answering**: Uses OpenAI to answer from retrieved document passages with citations.
- **Risk Detection**: YAML rules plus a TensorFlow-trained LiteRT classifier.
- **Modern Dashboard**: React frontend with Tailwind CSS and Recharts.

## Setup Instructions

### Prerequisites

- Docker and Docker Compose
- Node.js for local frontend development
- Python 3.11+ for local backend development

### Running with Docker

1. Build and start the containers:

   ```bash
   docker-compose up --build
   ```

2. Open the frontend at `http://localhost:5173`.
3. Open the backend API documentation at `http://localhost:8000/docs`.

### Local Setup

#### Backend

1. Navigate to the `backend` directory.
2. Create a virtual environment: `python -m venv .venv`
3. Activate the virtual environment.
4. Install runtime dependencies: `pip install -r requirements.txt`
5. Set `OPENAI_API_KEY` in your environment. Optionally set `OPENAI_MODEL`
   (defaults to `gpt-5.4-mini`) and `USE_QA_MODEL` (defaults to `true`).
6. To retrain the risk model, install `requirements-train.txt` and run `python train_risk_model.py`
7. Start the API: `uvicorn app.main:app --reload`

For Docker Compose, copy `.env.example` to `.env`, add your API key, and run
`docker-compose up --build`. For Vercel, configure `OPENAI_API_KEY` as a project
environment variable. Never expose the API key in the frontend.

If the key is absent or the API request fails, question answering safely falls
back to returning the most relevant retrieved passage.

#### Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`
3. Start the Vite server: `npm run dev`

### Vercel Services

The root `vercel.json` defines the Vite frontend at `/` and the FastAPI backend
at `/api`. In Vercel project settings, select the **Services** framework.

The deployed backend uses the compact LiteRT runtime and a `.tflite` model.
Full TensorFlow is only required when retraining the classifier and is excluded
from the Vercel runtime bundle.

After changing backend dependencies, create a new deployment from the latest
Git commit rather than redeploying an older failed deployment. The lightweight
service is named `api-lite` in Vercel build logs.

## API Endpoints

- `POST /upload`: Upload one or more PDF documents.
- `POST /ask`: Ask a question about the uploaded documents.
- `GET /risks`: Retrieve detected risks.
- `GET /documents`: List uploaded documents.
- `POST /detect-risk`: Run risk detection manually.
- `POST /reset`: Clear the in-memory application state.
- `GET /health`: Check backend health.
