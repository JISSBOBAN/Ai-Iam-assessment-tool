import csv
import json
from sqlalchemy.orm import Session
from . import crud, models
from .config import settings

def import_questions_from_csv(db: Session, csv_path: str = settings.CSV_PATH):
    inserted_count = 0
    updated_count = 0
    
    # Standards columns mapping
    STANDARD_COLS = [
        "iso_27001_2022", "nist_800_53_rev5", "soc_2_tsc", 
        "gdpr", "pci_dss_4_0", "hipaa", "cis_controls"
    ]

    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Extract basic fields
            question_id = row.get("question_id")
            if not question_id:
                continue # Skip empty rows
                
            question_data = {
                "question_id": question_id,
                "section_id": row.get("section_id", ""),
                "question_text": row.get("question_text", ""),
                "iam_domain": row.get("iam_domain", ""),
                "answer_type": row.get("answer_type", "yes_no_partial_with_text"),
                "question_type": row.get("question_type", ""),
                "iso_27001_2022": row.get("iso_27001_2022", ""),
                "nist_800_53_rev5": row.get("nist_800_53_rev5", ""),
                "soc_2_tsc": row.get("soc_2_tsc", ""),
                "gdpr": row.get("gdpr", ""),
                "pci_dss_4_0": row.get("pci_dss_4_0", ""),
                "hipaa": row.get("hipaa", ""),
                "cis_controls": row.get("cis_controls", ""),
                "notes": row.get("notes", ""),
                "meta": row # Store full row
            }
            
            # Upsert
            _, is_new = crud.upsert_question(db, question_data)
            if is_new:
                inserted_count += 1
            else:
                updated_count += 1
                
    return {"inserted": inserted_count, "updated": updated_count}

if __name__ == "__main__":
    from .db import SessionLocal, engine
    models.Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        stats = import_questions_from_csv(db)
        print(f"Import completed: {stats}")
    finally:
        db.close()
