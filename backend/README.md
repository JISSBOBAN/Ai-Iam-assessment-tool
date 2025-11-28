# Vanta-like Questionnaire Backend

This is a FastAPI backend for a Vanta-like questionnaire system. It supports CSV import of questions, submission of answers, and generation of compliance reports (ISO 27001, SOC 2, etc.).

## Prerequisites

- Python 3.11+
- Docker & Docker Compose (optional)

## Setup & Run (Local)

1.  **Install Dependencies**:
    ```bash
    cd backend
    python -m venv venv
    # Windows:
    .\venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    
    pip install -r requirements.txt
    ```

2.  **Initialize Database**:
    ```bash
    python -m app.init_db
    ```

3.  **Run Server**:
    ```bash
    uvicorn app.main:app --reload --port 8000
    ```

## Setup & Run (Docker)

1.  **Build and Run**:
    ```bash
    cd backend
    docker-compose up --build
    ```
    The API will be available at `http://localhost:8000`.
    The database will be persisted in `./db`.
    The CSV file is expected at `/mnt/data/questions.csv`. Ensure this path exists or update `docker-compose.yml`.

## API Usage

### 1. Import CSV
Import questions from the configured CSV path.
```bash
curl -X POST http://localhost:8000/import-csv
```

### 2. List Questions
Get all questions with their details.
```bash
curl http://localhost:8000/questions
```

### 3. Submit Answers
Submit answers for a client.
```bash
curl -X POST http://localhost:8000/submit -H "Content-Type: application/json" -d '{
  "client_id":"acme-corp",
  "answers":[
    {"question_id":"Q-001","answer":"yes"},
    {"question_id":"Q-002","answer":"n/a","notes":"outsourced"}
  ]
}'
```

### 4. Get Report
Download the HTML report for a submission.
```bash
curl http://localhost:8000/report/<submission_id> > report.html
```

### 5. Get Summary JSON
Get the compliance summary JSON.
```bash
curl http://localhost:8000/standards/summary/<submission_id>
```

## Testing

To run the tests:

```bash
cd backend
python -m pytest tests
```
