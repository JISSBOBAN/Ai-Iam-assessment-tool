import pytest
from app import models

# Reuse mock CSV fixture logic or just insert data directly
@pytest.fixture
def seed_questions(db):
    q1 = models.Question(
        question_id="Q-001",
        question_text="Do you have MFA?",
        standards={"ISO_27001_2022": "A.9.4.1"},
        answer_type="yes_no_na",
        meta={}
    )
    q2 = models.Question(
        question_id="Q-002",
        question_text="Is data encrypted?",
        standards={"ISO_27001_2022": "A.10.1.1"},
        answer_type="yes_no_na",
        meta={}
    )
    db.add(q1)
    db.add(q2)
    db.commit()

def test_get_questions(client, seed_questions):
    response = client.get("/questions")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["question_id"] == "Q-001"

def test_submit_answers(client, seed_questions):
    payload = {
        "client_id": "test-client",
        "answers": [
            {"question_id": "Q-001", "answer": "yes"},
            {"question_id": "Q-002", "answer": "n/a", "notes": "Not needed"}
        ]
    }
    response = client.post("/submit", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "submission_id" in data
    assert data["summary"]["ISO_27001_2022"]["status"] == "partial"
    # Wait, logic:
    # if no_count > 0 -> non_compliant
    # else if na_count > 0 and yes_count == (total - na) -> partial
    # else if yes_count == total -> compliant
    
    # Here: total=2, yes=1, na=1. yes == 2-1 (1). So "partial".
    
    assert data["summary"]["ISO_27001_2022"]["status"] == "partial"
    assert data["report_html"] is not None

def test_submit_invalid_question(client, seed_questions):
    payload = {
        "client_id": "test-client",
        "answers": [
            {"question_id": "INVALID", "answer": "yes"}
        ]
    }
    response = client.post("/submit", json=payload)
    assert response.status_code == 400

def test_get_report(client, seed_questions):
    # Submit first
    payload = {
        "client_id": "test-client",
        "answers": [
            {"question_id": "Q-001", "answer": "yes"}
        ]
    }
    res = client.post("/submit", json=payload)
    sub_id = res.json()["submission_id"]
    
    # Get report
    response = client.get(f"/report/{sub_id}")
    assert response.status_code == 200
    assert "Compliance Report" in response.text
