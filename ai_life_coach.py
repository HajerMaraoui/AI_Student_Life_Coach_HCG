import mysql.connector
import ollama
import json

# =========================
# 1. CONNECT TO DATABASE
# =========================
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="ai_life_coach_db"
)
cursor = conn.cursor()

student_id = 1

# =========================
# 2. GET STUDENT PROFILE
# =========================
cursor.execute("""
    SELECT full_name, age, field_of_study, sleep_hours_avg, stress_level
    FROM student
    WHERE id = %s
""", (student_id,))
student = cursor.fetchone()

# =========================
# 3. GET STUDY SESSIONS
# =========================
cursor.execute("""
    SELECT subject, study_date, duration_hours, productivity_score
    FROM study_sessions
    WHERE student_id = %s
""", (student_id,))
sessions = cursor.fetchall()

study_history = ""
for s in sessions:
    study_history += f"Subject: {s[0]}, Date: {s[1]}, Duration: {s[2]}h, Productivity: {s[3]}/10\n"

# =========================
# 4. GET DAILY ACTIVITIES
# =========================
cursor.execute("""
    SELECT activity_type, activity_date, start_time, end_time
    FROM daily_activities
    WHERE student_id = %s
""", (student_id,))
activities = cursor.fetchall()

activity_history = ""
for a in activities:
    activity_history += f"{a[1]} - {a[0]} from {a[2]} to {a[3]}\n"

# =========================
# 5. GET EXAMS SCHEDULE
# =========================
cursor.execute("""
    SELECT subject, exam_date, importance_level, preparation_status
    FROM exam_schedule
    WHERE student_id = %s
""", (student_id,))
exams = cursor.fetchall()

exam_info = ""
for e in exams:
    exam_info += f"Exam: {e[0]} on {e[1]}, Importance: {e[2]}/5, Status: {e[3]}\n"

# =========================
# 6. GET WELLBEING DATA
# =========================
cursor.execute("""
    SELECT record_date, sleep_hours, stress_level, energy_level
    FROM wellbeing
    WHERE student_id = %s
""", (student_id,))
wellbeing = cursor.fetchall()

wellbeing_history = ""
for w in wellbeing:
    wellbeing_history += f"{w[0]} - Sleep: {w[1]}h, Stress: {w[2]}/10, Energy: {w[3]}/10\n"

# =========================
# 7. BUILD PROMPT
# =========================
prompt = f"""
You are an AI Student Performance Analyst and Life Coach.

Your goal is to analyze student data deeply and return structured, actionable insights.

STRICT RULES:
- Output ONLY valid JSON
- No explanations
- No repetition
- No extra text
- Ensure JSON is valid and clean

OUTPUT FORMAT:
{{
  "student_profile": {{
    "name": "",
    "age": "",
    "field": ""
  }},
  "performance_analysis": [
    {{
      "subject": "",
      "avg_study_hours": "",
      "productivity_score": "",
      "weakness": "",
      "recommendation": ""
    }}
  ],
  "exam_strategy": [
    {{
      "subject": "",
      "exam_date": "",
      "priority": "",
      "study_plan": ""
    }}
  ],
  "daily_schedule": [
    {{
      "time_block": "morning",
      "activity": ""
    }},
    {{
      "time_block": "afternoon",
      "activity": ""
    }},
    {{
      "time_block": "evening",
      "activity": ""
    }}
  ],
  "wellbeing_analysis": {{
    "sleep_quality": "",
    "stress_level": "",
    "risk": "",
    "improvement_plan": ""
  }},
  "nutrition_plan": [
    {{
      "meal": "breakfast",
      "suggestion": ""
    }},
    {{
      "meal": "lunch",
      "suggestion": ""
    }},
    {{
      "meal": "dinner",
      "suggestion": ""
    }}
  ],
  "productivity_tips": [
    "",
    "",
    ""
  ]
}}

CONTEXT DATA:

Student:
Name: {student[0]}
Age: {student[1]}
Field: {student[2]}
Average Sleep: {student[3]} hours
Stress Level: {student[4]}/10

Study History:
{study_history}

Daily Activities:
{activity_history}

Exam Schedule:
{exam_info}

Wellbeing Data:
{wellbeing_history}

Now generate the JSON output.
"""

# =========================
# 8. CALL OLLAMA
# =========================
response = ollama.chat(
    model="phi", 
    options={"temperature": 0.2},
    messages=[{"role": "user", "content": prompt}]
)

try:
    data = json.loads(response['message']['content'])
except Exception as e:
    print("Invalid JSON:", e)
    print(response['message']['content'])
    data = {}

print(data)

# =========================
# 9. CLOSE CONNECTION
# =========================
cursor.close()
conn.close()