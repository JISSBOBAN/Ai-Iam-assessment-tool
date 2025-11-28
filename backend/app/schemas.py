from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuestionBase(BaseModel):
    question_id: str
    question_text: str
    iam_domain: Optional[str] = None
    sub_domain: Optional[str] = None
    answer_type: str = "yes_no_na"
    notes: Optional[str] = None
    standards: Dict[str, str] = {}
    meta: Dict[str, Any] = {}

class QuestionOut(QuestionBase):
    id: int

    class Config:
        from_attributes = True

class AnswerIn(BaseModel):
    question_id: str
    answer: str
    notes: Optional[str] = None

class SubmissionIn(BaseModel):
    client_id: str
    answers: List[AnswerIn]

class SubmissionOut(BaseModel):
    submission_id: str
    client_id: str
    created_at: datetime
    summary: Dict[str, Any]
    report_html: str

    class Config:
        from_attributes = True

class ImportStats(BaseModel):
    inserted: int
    updated: int
