# AI Student Life Coach – Full Stack AI Application

This project is a full-stack AI application that analyzes student data and generates structured recommendations for study, exams, wellbeing, and nutrition using a local AI model.

---
## Tech Stack

* Frontend: React
* Backend: Flask (Python)
* Database: MySQL
* AI Engine: Ollama (Phi / Gemma models)
* Languages: Python, JavaScript

---
## Architecture

```
React UI → Flask API → MySQL + Ollama → JSON → UI
```

---

## Installation

### Clone repository

```
git clone https://github.com/HajerMaraoui/AI_Student_Life_Coach_HCG.git
AI_Student_Life_Coach_HCG
```

### Create virtual environment

```
python -m venv venv
```

Activate:

Windows:

```
venv\Scripts\activate
```

Mac/Linux:

```
source venv/bin/activate
```

### Install dependencies

```
pip install flask flask-cors mysql-connector-python ollama
```

### Run AI model

```
ollama pull gemma4:e2b
```
(in this example)
---

## Configuration

Update database credentials in `app.py`:

```
host="localhost"
user="your_user"
password="your_password"
database="ai_life_coach_db"
```

---

## Run Application

Backend:

```
python app.py
```

## API Endpoint

```
GET /generate-plan/<student_id>
```

Example:

```
http://127.0.0.1:5000/generate-plan/1
```

---

## Response Example

```
{
  "performance_analysis": [
    {
      "subject": "Mathematics",
      "avg_study_hours": "2.0",
      "productivity_score": "Medium",
      "weakness": "Low practice",
      "recommendation": "Increase exercises"
    }
  ]
}
```

---

## Workflow

1. Frontend sends request
2. Flask processes data
3. MySQL provides data
4. Ollama generates response
5. JSON returned to UI

---

## Common Issues

Ollama not recognized
→ reinstall and restart terminal

Model too heavy
→ use:

```
ollama run phi
```

Invalid JSON
→ clean response in backend

API not responding
→ check server and port

---

## License

Educational use only.

---

## Author

AI workshop.
