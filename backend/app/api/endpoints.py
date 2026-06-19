from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from pydantic import BaseModel
from starlette.concurrency import run_in_threadpool
from typing import List, Optional
import os
import uuid
import shutil
import tempfile
import logging
from pathlib import Path

from app.services.pdf_parser import PDFParser
from app.services.chunker import Chunker
from app.vectorstore.vector_store import VectorStore
from app.services.qa_engine import QAEngine
from app.services.risk_detector import RiskDetector

logger = logging.getLogger(__name__)

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
    index_path=str(RUNTIME_DIR / "search_index.npy"),
    meta_path=str(RUNTIME_DIR / "search_meta.pkl"),
)
chunker = Chunker()
qa_engine = QAEngine()
risk_detector = RiskDetector(
    rules_path=str(BASE_DIR / "risk_rules.yaml"),
    model_path=str(BASE_DIR / "risk_model.tflite"),
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
        logger.info(f"Processing document {document_id} from {filepath}")
        # Parse PDF
        parser = PDFParser(str(filepath))
        parsed_pages = parser.parse()
        logger.info(f"Parsed {len(parsed_pages)} pages from {document_id}")
        
        # Chunk
        chunks = chunker.process_document(document_id, parsed_pages)
        logger.info(f"Created {len(chunks)} chunks from {document_id}")
        
        # Add to vector store
        vector_store.add_documents(chunks)
        logger.info(f"Added chunks to vector store for {document_id}")
        
        # Detect risks
        detected_risks = risk_detector.detect_risks(chunks)
        risks_db.extend(detected_risks)
        logger.info(f"Detected {len(detected_risks)} risks for {document_id}")
        
        logger.info(f"Successfully processed document {document_id}")
    except Exception as e:
        logger.error(f"Error processing {document_id}: {str(e)}", exc_info=True)

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(background_tasks: BackgroundTasks, files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    responses = []
    
    for file in files:
        try:
            logger.info(f"Uploading file: {file.filename}")
            
            if not file.filename:
                raise HTTPException(status_code=400, detail="File must have a filename")
            
            document_id = str(uuid.uuid4())
            # Sanitize filename
            safe_filename = "".join(c for c in file.filename if c.isalnum() or c in "._- ")
            filepath = UPLOAD_DIR / f"{document_id}_{safe_filename}"
            
            # Save file
            logger.info(f"Saving file to {filepath}")
            content = await file.read()
            with open(filepath, "wb") as buffer:
                buffer.write(content)
            
            logger.info(f"File saved successfully for {document_id}")
            
            documents_db.append({
                "document_id": document_id,
                "filename": file.filename,
                "status": "processing"
            })
            
            # Add processing task
            background_tasks.add_task(process_upload_background, str(filepath), document_id)
            
            responses.append(DocumentResponse(document_id=document_id, filename=file.filename, status="processing"))
            logger.info(f"Upload response prepared for {document_id}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error uploading file {file.filename}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")
    
    return responses

@router.post("/ask", response_model=AnswerResponse)
async def ask_question(request: AskRequest):
    top_chunks = vector_store.search(request.question, top_k=5)
    
    if not top_chunks:
        return AnswerResponse(answer="No relevant information found in documents.", confidence=0.0, citations=[])
        
    result = await run_in_threadpool(
        qa_engine.get_answer,
        request.question,
        top_chunks,
    )
    
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
