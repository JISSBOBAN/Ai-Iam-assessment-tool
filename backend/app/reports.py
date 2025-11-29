from typing import List, Dict, Any
from jinja2 import Template
from . import schemas, models

STANDARD_COLS = [
    "iso_27001_2022", "nist_800_53_rev5", "soc_2_tsc", 
    "gdpr", "pci_dss_4_0", "hipaa", "cis_controls"
]

def compute_summary(answers: List[schemas.AnswerIn], questions: List[models.Question]) -> Dict[str, Any]:
    # Map question_id to answer
    answer_map = {a.question_id: a for a in answers}
    
    # Map question_id to question object
    question_map = {q.question_id: q for q in questions}
    
    summary = {}
    
    for std in STANDARD_COLS:
        total_questions = 0
        yes_count = 0
        no_count = 0
        na_count = 0
        unanswered_count = 0
        na_notes = []
        
        # Find questions relevant to this standard
        # Check if the standard column has a value (not None and not empty string)
        relevant_questions = [q for q in questions if getattr(q, std) and getattr(q, std).strip()]
        
        total_questions = len(relevant_questions)
        
        if total_questions == 0:
            summary[std] = {
                "status": "not_applicable",
                "counts": {
                    "total": 0, "yes": 0, "no": 0, "na": 0, "unanswered": 0
                },
                "na_notes": []
            }
            continue
            
        for q in relevant_questions:
            ans_obj = answer_map.get(q.question_id)
            if not ans_obj:
                unanswered_count += 1
                continue
                
            ans_val = ans_obj.answer.lower()
            if ans_val == "yes":
                yes_count += 1
            elif ans_val == "no":
                no_count += 1
            elif ans_val == "n/a" or ans_val == "na":
                na_count += 1
                if ans_obj.notes:
                    na_notes.append(f"{q.question_id}: {ans_obj.notes}")
            else:
                # Treat unknown/other as unanswered or handle? 
                # Requirement says "yes"|"no"|"n/a"
                unanswered_count += 1

        # Determine status
        status = "unknown"
        if no_count > 0:
            status = "non_compliant"
        elif na_count > 0 and yes_count == (total_questions - na_count):
            status = "partial" # or needs_review per requirement
        elif yes_count == total_questions:
            status = "compliant"
        else:
            # If there are unanswered questions, it might be unknown or partial.
            # Requirement: "Else -> unknown" covers cases not matched above.
            # If yes_count + na_count < total (meaning some unanswered), it falls here.
            status = "unknown"
            
        summary[std] = {
            "status": status,
            "counts": {
                "total": total_questions,
                "yes": yes_count,
                "no": no_count,
                "na": na_count,
                "unanswered": unanswered_count
            },
            "na_notes": na_notes
        }
        
    return summary

REPORT_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Compliance Report - {{ submission.client_id }}</title>
    <style>
        body { font-family: sans-serif; margin: 20px; }
        h1, h2 { color: #333; }
        table { border-collapse: collapse; width: 100%; margin-bottom: 20px; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f4f4f4; }
        .status-compliant { color: green; font-weight: bold; }
        .status-non_compliant { color: red; font-weight: bold; }
        .status-partial { color: orange; font-weight: bold; }
        .status-not_applicable { color: gray; }
        .status-unknown { color: blue; }
    </style>
</head>
<body>
    <h1>Compliance Report</h1>
    <p><strong>Client ID:</strong> {{ submission.client_id }}</p>
    <p><strong>Submission ID:</strong> {{ submission.submission_id }}</p>
    <p><strong>Date:</strong> {{ submission.created_at }}</p>

    <h2>Executive Summary</h2>
    <table>
        <thead>
            <tr>
                <th>Standard</th>
                <th>Status</th>
                <th>Total</th>
                <th>Yes</th>
                <th>No</th>
                <th>N/A</th>
                <th>Unanswered</th>
            </tr>
        </thead>
        <tbody>
            {% for std, data in summary.items() %}
            <tr>
                <td>{{ std }}</td>
                <td class="status-{{ data.status }}">{{ data.status }}</td>
                <td>{{ data.counts.total }}</td>
                <td>{{ data.counts.yes }}</td>
                <td>{{ data.counts.no }}</td>
                <td>{{ data.counts.na }}</td>
                <td>{{ data.counts.unanswered }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>

    {% for std, data in summary.items() %}
        {% if data.na_notes %}
        <h3>N/A Notes for {{ std }}</h3>
        <ul>
            {% for note in data.na_notes %}
            <li>{{ note }}</li>
            {% endfor %}
        </ul>
        {% endif %}
    {% endfor %}

    <h2>Detailed Responses</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>Question</th>
                <th>Standards</th>
                <th>Answer</th>
                <th>Notes</th>
            </tr>
        </thead>
        <tbody>
            {% for item in details %}
            <tr>
                <td>{{ item.question_id }}</td>
                <td>{{ item.question_text }}</td>
                <td>{{ item.standards }}</td>
                <td>{{ item.answer }}</td>
                <td>{{ item.notes }}</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</body>
</html>
"""

def generate_html_report(submission: models.Submission, summary: Dict[str, Any], questions: List[models.Question]) -> str:
    # Prepare details list
    question_map = {q.question_id: q for q in questions}
    details = []
    
    # Create a map of answers
    answers_map = {a['question_id']: a for a in submission.answers}
    
    for q in questions:
        ans = answers_map.get(q.question_id)
        
        # Collect relevant standards for this question
        q_standards = []
        for std in STANDARD_COLS:
            val = getattr(q, std)
            if val and val.strip():
                q_standards.append(f"{std}: {val}")
        
        details.append({
            "question_id": q.question_id,
            "question_text": q.question_text,
            "standards": ", ".join(q_standards),
            "answer": ans['answer'] if ans else "-",
            "notes": ans['notes'] if ans and ans.get('notes') else ""
        })
        
    template = Template(REPORT_TEMPLATE)
    return template.render(submission=submission, summary=summary, details=details)
