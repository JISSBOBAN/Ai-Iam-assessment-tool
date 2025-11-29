import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    print("Testing GET /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)


def test_import_csv():
    print("Testing POST /import-csv...")
    try:
        response = requests.post(f"{BASE_URL}/import-csv")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

def test_get_questions():
    print("Testing GET /questions...")
    try:
        response = requests.get(f"{BASE_URL}/questions?limit=5")
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Count: {len(data)}")
        if data:
            print(f"Sample Question: {data[0]['question_id']}")
            return data[0]['question_id']
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
    return None

def test_get_single_question(qid):
    if not qid: return
    print(f"Testing GET /questions/{qid}...")
    try:
        response = requests.get(f"{BASE_URL}/questions/{qid}")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json().get('question_text')[:50]}...")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

def test_submit(qid):
    if not qid: return
    print("Testing POST /submit...")
    payload = {
        "client_id": "test-doc-user",
        "answers": [
            {
                "question_id": qid,
                "answer": "yes",
                "notes": "Test note"
            }
        ]
    }
    try:
        response = requests.post(f"{BASE_URL}/submit", json=payload)
        print(f"Status: {response.status_code}")
        data = response.json()
        print(f"Submission ID: {data.get('submission_id')}")
        return data.get('submission_id')
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)
    return None

def test_get_report(sub_id):
    if not sub_id: return
    print(f"Testing GET /report/{sub_id}...")
    try:
        response = requests.get(f"{BASE_URL}/report/{sub_id}")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Length: {len(response.text)}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

def test_get_summary(sub_id):
    if not sub_id: return
    print(f"Testing GET /standards/summary/{sub_id}...")
    try:
        response = requests.get(f"{BASE_URL}/standards/summary/{sub_id}")
        print(f"Status: {response.status_code}")
        print(f"Keys: {list(response.json().keys())}")
    except Exception as e:
        print(f"Error: {e}")
    print("-" * 20)

if __name__ == "__main__":
    test_health()
    test_import_csv()
    qid = test_get_questions()
    test_get_single_question(qid)
    sub_id = test_submit(qid)
    test_get_report(sub_id)
    test_get_summary(sub_id)
