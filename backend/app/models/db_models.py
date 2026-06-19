from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(512), nullable=False)
    upload_date = Column(DateTime, default=datetime.utcnow, index=True)
    file_size = Column(Integer)  # in bytes
    status = Column(String(50), default="processed")  # processed, processing, failed
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    qa_interactions = relationship("QAInteraction", back_populates="document", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="document", cascade="all, delete-orphan")
    user = relationship("User", back_populates="documents")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    qa_interactions = relationship("QAInteraction", back_populates="user", cascade="all, delete-orphan")


class QAInteraction(Base):
    __tablename__ = "qa_interactions"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    confidence = Column(Float, nullable=True)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    context_data = Column(JSON, nullable=True)  # Store additional context

    # Relationships
    document = relationship("Document", back_populates="qa_interactions")
    user = relationship("User", back_populates="qa_interactions")


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False, index=True)
    risk_level = Column(String(50), nullable=False)  # low, medium, high, critical
    risk_score = Column(Float, nullable=False)  # 0.0 to 1.0
    identified_risks = Column(JSON, nullable=False)  # List of detected risk categories
    detailed_analysis = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="risk_assessments")
