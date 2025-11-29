from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from .db import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, unique=True, index=True)
    section_id = Column(String)
    question_text = Column(Text)
    iam_domain = Column(String)
    answer_type = Column(String, default="yes_no_partial_with_text")
    question_type = Column(String)
    iso_27001_2022 = Column(String)
    nist_800_53_rev5 = Column(String)
    soc_2_tsc = Column(String)
    gdpr = Column(String)
    pci_dss_4_0 = Column(String)
    hipaa = Column(String)
    cis_controls = Column(String)
    notes = Column(Text)
    meta = Column(JSON)

class Submission(Base):
    __tablename__ = "submissions"

    submission_id = Column(String, primary_key=True, default=generate_uuid)
    client_id = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    answers = Column(JSON)
    summary = Column(JSON)
    report_html = Column(Text)
