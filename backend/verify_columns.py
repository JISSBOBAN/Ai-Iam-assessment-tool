import csv
from app.db import SessionLocal
from app.models import Question
from sqlalchemy import inspect

def verify_data():
    # 1. Get CSV Headers
    with open('question.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        csv_headers = reader.fieldnames
        # Get first row for data verification
        first_row = next(reader)

    print(f"CSV Headers: {csv_headers}")

    # 2. Get DB Columns
    db = SessionLocal()
    inspector = inspect(db.get_bind())
    db_columns = [c['name'] for c in inspector.get_columns('questions')]
    print(f"DB Columns: {db_columns}")

    # 3. Compare Columns
    missing_in_db = [h for h in csv_headers if h and h not in db_columns]
    # Note: 'meta' and 'id' are in DB but not CSV, which is fine.
    # We are checking if CSV columns are present in DB.
    
    if missing_in_db:
        print(f"WARNING: The following CSV columns are MISSING in the Database: {missing_in_db}")
    else:
        print("SUCCESS: All named CSV columns are present in the Database.")

    # 4. Verify Data Content for the first row
    db_question = db.query(Question).filter(Question.question_id == first_row['question_id']).first()
    
    if not db_question:
        print(f"ERROR: Record {first_row['question_id']} not found in DB!")
        return

    print(f"\nVerifying data for Question ID: {first_row['question_id']}")
    mismatch = False
    for col in csv_headers:
        if not col: continue # Skip empty header if any
        
        csv_val = first_row[col]
        db_val = getattr(db_question, col, None)
        
        # Normalize for comparison (None vs empty string)
        if db_val is None: db_val = ""
        if csv_val is None: csv_val = ""
        
        if str(db_val).strip() != str(csv_val).strip():
            print(f"MISMATCH for column '{col}': CSV='{csv_val}' vs DB='{db_val}'")
            mismatch = True
        else:
            # print(f"MATCH for column '{col}'")
            pass
            
    if not mismatch:
        print("SUCCESS: Data content matches perfectly for the sample record.")
    else:
        print("WARNING: Data mismatches found.")

    db.close()

if __name__ == "__main__":
    verify_data()
