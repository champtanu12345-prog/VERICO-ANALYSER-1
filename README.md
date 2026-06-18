# Multi-Document Question Answering & Risk Detection System

An end-to-end system for intelligent document analysis, capable of answering
questions from uploaded PDFs and automatically detecting risks using rules and
TensorFlow text classification.

## Features

- **Intelligent Chunking**: Recursive and overlapping text chunking for optimal context retrieval.
- **Semantic Search**: FAISS vector database powered by `all-MiniLM-L6-v2` embeddings.
- **Question Answering**: DistilBERT model for answer extraction from documents.
- **Risk Detection**: Dual-engine detection using YAML rules and a TensorFlow/Keras classifier.
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
4. Install dependencies: `pip install -r requirements.txt`
5. Train the TensorFlow risk model: `python train_risk_model.py`
6. Start the API: `uvicorn app.main:app --reload`

#### Frontend

1. Navigate to the `frontend` directory.
2. Install dependencies: `npm install`
3. Start the Vite server: `npm run dev`

### Vercel Services

The root `vercel.json` defines the Vite frontend at `/` and the FastAPI backend
at `/api`. In Vercel project settings, select the **Services** framework.

Vercel's Python functions have a 500 MB uncompressed bundle limit. The current
TensorFlow and PyTorch dependencies can exceed that limit, so production
deployment may require hosting the backend on a container platform and setting
`VITE_API_URL` to that backend URL.

## API Endpoints

- `POST /upload`: Upload one or more PDF documents.
- `POST /ask`: Ask a question about the uploaded documents.
- `GET /risks`: Retrieve detected risks.
- `GET /documents`: List uploaded documents.
- `POST /detect-risk`: Run risk detection manually.
- `POST /reset`: Clear the in-memory application state.
- `GET /health`: Check backend health.
