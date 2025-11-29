from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuestionBase(BaseModel):
    question_id: str
    section_id: Optional[str] = None
    question_text: str
    iam_domain: Optional[str] = None
    answer_type: str = "yes_no_partial_with_text"
    question_type: Optional[str] = None
    iso_27001_2022: Optional[str] = None
    nist_800_53_rev5: Optional[str] = None
    soc_2_tsc: Optional[str] = None
    gdpr: Optional[str] = None
    pci_dss_4_0: Optional[str] = None
    hipaa: Optional[str] = None
    cis_controls: Optional[str] = None
    notes: Optional[str] = None
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
