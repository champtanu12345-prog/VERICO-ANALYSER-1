from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import shutil
import tempfile
from pathlib import Path

from app.services.pdf_parser import PDFParser
from app.services.chunker import Chunker
from app.vectorstore.vector_store import VectorStore
from app.services.qa_engine import QAEngine
from app.services.risk_detector import RiskDetector

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parents[2]
RUNTIME_DIR = (
    Path(tempfile.gettempdir()) / "verico"
    if os.getenv("VERCEL")
    else BASE_DIR
)
UPLOAD_DIR = RUNTIME_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Global instances (simplified for this assignment, in production use dependency injection)
vector_store = VectorStore(
    index_path=str(RUNTIME_DIR / "faiss_index.bin"),
    meta_path=str(RUNTIME_DIR / "faiss_meta.pkl"),
)
chunker = Chunker()
qa_engine = QAEngine(use_qa_model=False)
risk_detector = RiskDetector(
    rules_path=str(BASE_DIR / "risk_rules.yaml"),
    model_path=str(BASE_DIR / "risk_model.keras"),
    labels_path=str(BASE_DIR / "risk_labels.json"),
)

# In-memory storage for simplicity (use DB in production)
documents_db = []
risks_db = []

# Pydantic Models
class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    status: str

class AskRequest(BaseModel):
    question: str

class Citation(BaseModel):
    document: str
    page: int
    excerpt: str

class AnswerResponse(BaseModel):
    answer: str
    confidence: float
    citations: List[Citation]

class RiskItem(BaseModel):
    risk_type: str
    severity: str
    page: int
    source: str
    text: str
    method: str

class RiskResponse(BaseModel):
    risks: List[RiskItem]

def process_upload_background(filepath: str, document_id: str):
    try:
        # Parse PDF
        parser = PDFParser(filepath)
        parsed_pages = parser.parse()
        
        # Chunk
        chunks = chunker.process_document(document_id, parsed_pages)
        
        # Add to vector store
        vector_store.add_documents(chunks)
        
        # Detect risks
        detected_risks = risk_detector.detect_risks(chunks)
        risks_db.extend(detected_risks)
        
        print(f"Processed document {document_id}")
    except Exception as e:
        print(f"Error processing {document_id}: {e}")

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    responses = []
    
    for file in files:
        document_id = str(uuid.uuid4())
        filepath = UPLOAD_DIR / f"{document_id}_{file.filename}"
        
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        documents_db.append({
            "document_id": document_id,
            "filename": file.filename,
            "status": "processed" # Usually would be "processing", but we process synchronous/fast for demo
        })
        
        # We can run processing in background
        background_tasks.add_task(process_upload_background, filepath, document_id)
        
        responses.append(DocumentResponse(document_id=document_id, filename=file.filename, status="processing"))
        
    return responses

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: AskRequest):
    top_chunks = vector_store.search(request.question, top_k=5)
    
    if not top_chunks:
        return AnswerResponse(answer="No relevant information found in documents.", confidence=0.0, citations=[])
        
    result = qa_engine.get_answer(request.question, top_chunks)
    
    citations = [Citation(**cit) for cit in result["citations"]]
    return AnswerResponse(answer=result["answer"], confidence=result["confidence"], citations=citations)

@router.get("/documents")
async def get_documents():
    return documents_db

@router.get("/risks", response_model=List[RiskItem])
async def get_risks():
    return [RiskItem(**risk) for risk in risks_db]

@router.post("/detect-risk", response_model=RiskResponse)
async def manual_detect_risk(filepath: str):
    # Endpoint to trigger risk detection manually if needed
    parser = PDFParser(filepath)
    parsed_pages = parser.parse()
    chunks = chunker.process_document("manual", parsed_pages)
    risks = risk_detector.detect_risks(chunks)
    return RiskResponse(risks=[RiskItem(**risk) for risk in risks])

@router.post("/reset")
async def reset_system():
    global documents_db, risks_db
    documents_db.clear()
    risks_db.clear()
    vector_store.clear()
    
    # clear uploads directory
    for filename in os.listdir(UPLOAD_DIR):
        file_path = UPLOAD_DIR / filename
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            pass
            
    return {"message": "System reset successfully"}
