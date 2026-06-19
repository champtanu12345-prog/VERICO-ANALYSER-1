from sqlalchemy.orm import Session
from app.models.db_models import Document, User, QAInteraction, RiskAssessment
from app import schemas


# User CRUD
def create_user(db: Session, user: schemas.UserCreate):
    db_user = User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()


# Document CRUD
def create_document(db: Session, document: schemas.DocumentCreate, file_path: str, user_id: int = None):
    db_document = Document(
        filename=document.filename,
        file_path=file_path,
        file_size=document.file_size,
        user_id=user_id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document


def get_document(db: Session, document_id: int):
    return db.query(Document).filter(Document.id == document_id).first()


def get_all_documents(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Document).offset(skip).limit(limit).all()


def update_document_status(db: Session, document_id: int, status: str):
    db_document = db.query(Document).filter(Document.id == document_id).first()
    if db_document:
        db_document.status = status
        db.commit()
        db.refresh(db_document)
    return db_document


# QA Interaction CRUD
def create_qa_interaction(db: Session, qa: schemas.QAInteractionCreate):
    db_qa = QAInteraction(
        document_id=qa.document_id,
        user_id=qa.user_id,
        question=qa.question,
        answer=qa.answer,
        confidence=qa.confidence,
        context_data=qa.context_data
    )
    db.add(db_qa)
    db.commit()
    db.refresh(db_qa)
    return db_qa


def get_qa_interactions(db: Session, document_id: int):
    return db.query(QAInteraction).filter(QAInteraction.document_id == document_id).all()


# Risk Assessment CRUD
def create_risk_assessment(db: Session, risk: schemas.RiskAssessmentCreate):
    db_risk = RiskAssessment(
        document_id=risk.document_id,
        risk_level=risk.risk_level,
        risk_score=risk.risk_score,
        identified_risks=risk.identified_risks,
        detailed_analysis=risk.detailed_analysis
    )
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    return db_risk


def get_risk_assessment(db: Session, document_id: int):
    return db.query(RiskAssessment).filter(RiskAssessment.document_id == document_id).order_by(RiskAssessment.created_at.desc()).first()


def get_all_risk_assessments(db: Session, document_id: int):
    return db.query(RiskAssessment).filter(RiskAssessment.document_id == document_id).all()
