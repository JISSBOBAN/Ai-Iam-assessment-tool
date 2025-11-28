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
        "ISO_27001_2022", "NIST_800_53_Rev5", "SOC_2_TSC", 
        "GDPR", "PCI_DSS_4_0", "HIPAA", "CIS_Controls"
    ]

    with open(csv_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            # Extract basic fields
            question_id = row.get("Question_ID")
            if not question_id:
                continue # Skip empty rows
                
            question_text = row.get("Question", "")
            iam_domain = row.get("IAM_Domain", "")
            sub_domain = row.get("Sub_Domain", "")
            answer_type = row.get("Answer_Type", "")
            if not answer_type:
                answer_type = "yes_no_na"
            notes = row.get("Notes", "")
            
            # Extract standards
            standards = {}
            for std in STANDARD_COLS:
                val = row.get(std, "").strip()
                if val:
                    standards[std] = val
            
            # Prepare data
            question_data = {
                "question_id": question_id,
                "question_text": question_text,
                "iam_domain": iam_domain,
                "sub_domain": sub_domain,
                "answer_type": answer_type,
                "notes": notes,
                "standards": standards,
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
    from .db import SessionLocal
    db = SessionLocal()
    try:
        stats = import_questions_from_csv(db)
        print(f"Import completed: {stats}")
    finally:
        db.close()
