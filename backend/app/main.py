from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from typing import List

from . import models, schemas, crud, import_csv, reports, db

# Create tables
# models.Base.metadata.create_all(bind=db.engine)


app = FastAPI(title="Vanta-like Questionnaire Backend")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/import-csv", response_model=schemas.ImportStats)
def import_csv_endpoint(db: Session = Depends(db.get_db)):
    try:
        stats = import_csv.import_questions_from_csv(db)
        return stats
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSV file not found at configured path")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/questions", response_model=List[schemas.QuestionOut])
def get_questions(skip: int = 0, limit: int = 1000, db: Session = Depends(db.get_db)):
    questions = crud.get_questions(db, skip=skip, limit=limit)
    return questions

@app.get("/questions/{question_id}", response_model=schemas.QuestionOut)
def get_question(question_id: str, db: Session = Depends(db.get_db)):
    question = crud.get_question_by_qid(db, question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question

@app.post("/submit", response_model=schemas.SubmissionOut)
def submit_answers(submission: schemas.SubmissionIn, db: Session = Depends(db.get_db)):
    # Validate question_ids
    all_questions = crud.get_questions(db)
    valid_qids = {q.question_id for q in all_questions}
    
    for ans in submission.answers:
        if ans.question_id not in valid_qids:
            raise HTTPException(status_code=400, detail=f"Invalid question_id: {ans.question_id}")
        if ans.answer.lower() not in ["yes", "no", "n/a", "na"]:
            raise HTTPException(status_code=400, detail=f"Invalid answer for {ans.question_id}: {ans.answer}. Must be yes, no, or n/a")

    # Compute summary
    summary = reports.compute_summary(submission.answers, all_questions)
    
    # Generate UUID beforehand to include in report
    new_id = models.generate_uuid()
    
    # Create submission object
    db_submission = models.Submission(
        submission_id=new_id,
        client_id=submission.client_id,
        answers=[a.model_dump() for a in submission.answers],
        summary=summary,
        report_html="" # Placeholder
    )
    
    # Generate HTML report
    report_html = reports.generate_html_report(db_submission, summary, all_questions)
    db_submission.report_html = report_html
    
    # Save to DB
    db.add(db_submission)
    db.commit()
    db.refresh(db_submission)
    
    return db_submission

@app.get("/report/{submission_id}", response_class=HTMLResponse)
def get_report(submission_id: str, db: Session = Depends(db.get_db)):
    submission = crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission.report_html

@app.get("/standards/summary/{submission_id}")
def get_summary(submission_id: str, db: Session = Depends(db.get_db)):
    submission = crud.get_submission(db, submission_id)
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    return submission.summary
