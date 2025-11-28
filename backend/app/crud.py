from sqlalchemy.orm import Session
from . import models, schemas
import json

def get_question_by_qid(db: Session, question_id: str):
    return db.query(models.Question).filter(models.Question.question_id == question_id).first()

def upsert_question(db: Session, question_data: dict):
    # Check if exists
    db_question = get_question_by_qid(db, question_data["question_id"])
    if db_question:
        # Update
        for key, value in question_data.items():
            setattr(db_question, key, value)
        db.commit()
        db.refresh(db_question)
        return db_question, False # Updated
    else:
        # Insert
        db_question = models.Question(**question_data)
        db.add(db_question)
        db.commit()
        db.refresh(db_question)
        return db_question, True # Inserted

def get_questions(db: Session, skip: int = 0, limit: int = 1000):
    return db.query(models.Question).offset(skip).limit(limit).all()

def create_submission(db: Session, submission: schemas.SubmissionIn, summary: dict, report_html: str):
    db_submission = models.Submission(
        client_id=submission.client_id,
        answers=[a.model_dump() for a in submission.answers],
        summary=summary,
        report_html=report_html
    )
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    return db_submission

def get_submission(db: Session, submission_id: str):
    return db.query(models.Submission).filter(models.Submission.submission_id == submission_id).first()
