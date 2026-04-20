import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = "data/tutor_app.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        level TEXT,
        subject TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Progress table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS progress (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT,
        topic TEXT,
        score REAL,
        total_questions INTEGER,
        completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    ''')
    
    # Study Plans table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS study_plans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        plan_json TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    ''')

    # Streak table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS streaks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        current_streak INTEGER DEFAULT 0,
        last_study_date DATE,
        FOREIGN KEY (student_id) REFERENCES students (id)
    )
    ''')

    conn.commit()
    conn.close()

def get_db_connection():
    return sqlite3.connect(DB_PATH)

def add_student(name, level, subject):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO students (name, level, subject) VALUES (?, ?, ?)", (name, level, subject))
    student_id = cursor.lastrowid
    # Initialize streak
    cursor.execute("INSERT INTO streaks (student_id, current_streak, last_study_date) VALUES (?, 0, NULL)", (student_id,))
    conn.commit()
    conn.close()
    return student_id

def log_progress(student_id, subject, topic, score, total_questions):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO progress (student_id, subject, topic, score, total_questions) VALUES (?, ?, ?, ?, ?)", 
                   (student_id, subject, topic, score, total_questions))
    
    # Update streak logic
    today = datetime.now().date()
    cursor.execute("SELECT current_streak, last_study_date FROM streaks WHERE student_id = ?", (student_id,))
    res = cursor.fetchone()
    if res:
        current_streak, last_date_str = res
        if last_date_str:
            last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
            if last_date == today:
                pass # Already updated today
            elif (today - last_date).days == 1:
                cursor.execute("UPDATE streaks SET current_streak = current_streak + 1, last_study_date = ? WHERE student_id = ?", (today, student_id))
            else:
                cursor.execute("UPDATE streaks SET current_streak = 1, last_study_date = ? WHERE student_id = ?", (today, student_id))
        else:
            cursor.execute("UPDATE streaks SET current_streak = 1, last_study_date = ? WHERE student_id = ?", (today, student_id))
    
    conn.commit()
    conn.close()

def get_student_progress(student_id):
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM progress WHERE student_id = ?", conn, params=(student_id,))
    conn.close()
    return df

def get_streak(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_streak FROM streaks WHERE student_id = ?", (student_id,))
    res = cursor.fetchone()
    conn.close()
    return res[0] if res else 0
