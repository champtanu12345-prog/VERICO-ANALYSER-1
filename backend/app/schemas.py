from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any


# User Schemas
class UserBase(BaseModel):
    username: str
    email: Optional[str] = None


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


# Document Schemas
class DocumentBase(BaseModel):
    filename: str
    file_size: Optional[int] = None


class DocumentCreate(DocumentBase):
    pass


class DocumentResponse(DocumentBase):
    id: int
    upload_date: datetime
    status: str
    user_id: Optional[int]

    class Config:
        from_attributes = True


# QA Interaction Schemas
class QAInteractionBase(BaseModel):
    question: str
    answer: str
    confidence: Optional[float] = None
    context_data: Optional[Dict[str, Any]] = None


class QAInteractionCreate(QAInteractionBase):
    document_id: int
    user_id: Optional[int] = None


class QAInteractionResponse(QAInteractionBase):
    id: int
    document_id: int
    user_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True


# Risk Assessment Schemas
class RiskAssessmentBase(BaseModel):
    risk_level: str
    risk_score: float
    identified_risks: List[str]
    detailed_analysis: Optional[str] = None


class RiskAssessmentCreate(RiskAssessmentBase):
    document_id: int


class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    document_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
