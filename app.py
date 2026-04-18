import base64
from flask import Flask, jsonify, request  
from flask_cors import CORS
import mysql.connector
import ollama
import json

app = Flask(__name__)
CORS(app)

# =========================
# DATABASE CONNECTION
# =========================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ai_life_coach_db"
    )

# =========================
# ROUTE: GENERATE PLAN
# =========================
@app.route("/generate-plan/<int:student_id>")
def generate_plan(student_id):

    conn = get_db()
    cursor = conn.cursor()

    # =========================
    # GET STUDENT
    # =========================
    cursor.execute("""
        SELECT full_name, age, field_of_study, sleep_hours_avg, stress_level
        FROM student WHERE id=%s
    """, (student_id,))
    student = cursor.fetchone()

    # =========================
    # GET STUDY SESSIONS
    # =========================
    cursor.execute("""
        SELECT subject, study_date, duration_hours
        FROM study_sessions
        WHERE student_id=%s
    """, (student_id,))
    sessions = cursor.fetchall()

    study_history = "\n".join([
        f"{s[0]} on {s[1]} ({s[2]}h)" for s in sessions
    ])

    # =========================
    # GET EXAMS
    # =========================
    cursor.execute("""
        SELECT subject, exam_date, importance_level, preparation_status
        FROM exam_schedule
        WHERE student_id=%s
    """, (student_id,))
    exams = cursor.fetchall()

    exam_info = "\n".join([
        f"{e[0]} - {e[1]} - importance {e[2]} - {e[3]}"
        for e in exams
    ])

    # =========================
    # BUILD PROMPT
    # =========================
    prompt = f"""
You are an AI Student Performance Analyst.

Return ONLY valid JSON.
No explanation. No extra text. No repetition.

IMPORTANT RULES:
- Keep answers VERY short (max 10 words per field)
- Maximum 3 items per list
- Ensure JSON is complete and valid

OUTPUT FORMAT:
{{
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
  ]
}}

STUDENT:
Name: {student[0]}
Age: {student[1]}
Field: {student[2]}
Sleep: {student[3]}
Stress: {student[4]}

STUDY HISTORY:
{study_history}

EXAMS:
{exam_info}
"""

    # =========================
    # CALL OLLAMA
    # =========================
    response = ollama.chat(
        model="gemma4:e2b",
        options={
            "temperature": 0.2,
            "num_predict": 1200
        },
        messages=[{"role": "user", "content": prompt}]
    )

    # =========================
    # PARSE JSON 
    # =========================
    raw = response['message']['content']

    cleaned = raw.replace("```json", "").replace("```", "").strip()

    if not cleaned.endswith("}"):
        cleaned += "}"

    try:
        data = json.loads(cleaned)
        print("JSON parsed successfully")

    except Exception as e:
        print("JSON ERROR:", e)
        print("\nRAW OUTPUT:\n", raw)

        data = {
            "error": "Invalid JSON",
            "raw": raw
        }

    # =========================
    # CLOSE CONNECTION
    # =========================
    cursor.close()
    conn.close()

    return jsonify(data)


# =========================
# Image processing
# =========================
@app.route("/analyze-meal/<int:student_id>", methods=["POST"])
def analyze_meal(student_id):
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image_file = request.files["image"]
    meal_type = request.form.get("meal_type", "lunch")
    image_data = base64.b64encode(image_file.read()).decode("utf-8")

    prompt = f"""
You are analyzing a photo of a student's {meal_type}.
Return ONLY valid JSON, no extra text, no markdown.

{{
  "meal_description": "",
  "is_healthy": true,
  "estimated_calories": 0,
  "nutrients_detected": [],
  "health_score": 0,
  "suggestion": ""
}}

Rules:
- health_score: 1 to 10
- nutrients_detected: list proteins, carbs, vegetables visible
- suggestion: one short tip to improve the meal if needed
- meal_description: short description of what you see on the plate
"""

    response = ollama.chat(
        model="gemma4:e2b",
        messages=[{
            "role": "user",
            "content": prompt,
            "images": [image_data]
        }],
        options={"temperature": 0.2}
    )

    raw = response["message"]["content"]
    cleaned = raw.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(cleaned)
    except Exception as e:
        return jsonify({"error": "Invalid JSON", "raw": raw}), 500

    conn = get_db()
    cursor = conn.cursor()
    col = meal_type

    cursor.execute(f"""
        INSERT INTO nutrition (student_id, meal_date, {col})
        VALUES (%s, CURDATE(), %s)
        ON DUPLICATE KEY UPDATE {col} = %s
    """, (student_id, data.get("meal_description"), data.get("meal_description")))

    conn.commit()
    cursor.close()
    conn.close()

    data["meal_type"] = meal_type
    return jsonify(data)

# =========================
# RUN SERVER
# =========================
if __name__ == "__main__":
    app.run(debug=True)