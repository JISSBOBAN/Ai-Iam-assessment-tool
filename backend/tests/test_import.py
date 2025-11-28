import pytest
import csv
import os
from app.import_csv import import_questions_from_csv
from app import models

# Mock CSV content
MOCK_CSV_CONTENT = """Question_ID,Question,IAM_Domain,Sub_Domain,ISO_27001_2022,NIST_800_53_Rev5,SOC_2_TSC,GDPR,PCI_DSS_4_0,HIPAA,CIS_Controls,Answer_Type,Notes
Q-001,Do you have MFA?,Access Control,MFA,A.9.4.1,,,,,,,yes_no_na,
Q-002,Is data encrypted?,Cryptography,Encryption,,SC-28,,,,,,,yes_no_na,
"""

@pytest.fixture
def mock_csv_file(tmp_path):
    d = tmp_path / "mnt" / "data"
    d.mkdir(parents=True, exist_ok=True)
    p = d / "questions.csv"
    p.write_text(MOCK_CSV_CONTENT, encoding='utf-8-sig')
    return str(p)

def test_import_csv(db, mock_csv_file):
    # Run import
    stats = import_questions_from_csv(db, csv_path=mock_csv_file)
    
    assert stats["inserted"] == 2
    assert stats["updated"] == 0
    
    # Verify DB content
    q1 = db.query(models.Question).filter(models.Question.question_id == "Q-001").first()
    assert q1 is not None
    assert q1.question_text == "Do you have MFA?"
    assert q1.standards["ISO_27001_2022"] == "A.9.4.1"
    
    q2 = db.query(models.Question).filter(models.Question.question_id == "Q-002").first()
    assert q2 is not None
    assert "NIST_800_53_Rev5" in q2.standards

def test_import_idempotency(db, mock_csv_file):
    # First import
    import_questions_from_csv(db, csv_path=mock_csv_file)
    
    # Second import
    stats = import_questions_from_csv(db, csv_path=mock_csv_file)
    
    assert stats["inserted"] == 0
    assert stats["updated"] == 2 # Should update existing rows
    
    # Verify count
    count = db.query(models.Question).count()
    assert count == 2
