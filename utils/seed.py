import sqlite3
import random
from datetime import datetime, timedelta

from utils.db import init_db, DB_PATH

def seed_data():
    init_db()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if data already exists
    cursor.execute("SELECT count(*) FROM students")
    if cursor.fetchone()[0] > 0:
        print("Data already exists. Skipping seeding.")
        conn.close()
        return

    # Add a demo student
    cursor.execute("INSERT INTO students (name, level, subject) VALUES (?, ?, ?)", 
                   ("Demo Student", "Intermediate", "Physics"))
    student_id = cursor.lastrowid
    
    # Add a streak
    cursor.execute("INSERT INTO streaks (student_id, current_streak, last_study_date) VALUES (?, ?, ?)",
                   (student_id, 5, (datetime.now() - timedelta(days=1)).date()))
    
    # Add some progress history
    subjects = ["Physics", "Math", "Coding", "English"]
    topics = {
        "Physics": ["Mechanics", "Thermodynamics", "Optics"],
        "Math": ["Calculus", "Algebra", "Geometry"],
        "Coding": ["Python", "Data Structures", "Algorithms"],
        "English": ["Grammar", "Vocabulary", "Literature"]
    }
    
    for i in range(10):
        sub = random.choice(subjects)
        top = random.choice(topics[sub])
        score = random.randint(40, 100)
        date = (datetime.now() - timedelta(days=random.randint(0, 10))).strftime('%Y-%m-%d %H:%M:%S')
        
        cursor.execute("INSERT INTO progress (student_id, subject, topic, score, total_questions, completed_at) VALUES (?, ?, ?, ?, ?, ?)",
                       (student_id, sub, top, score, 5, date))
    
    conn.commit()
    conn.close()
    print("Demo data seeded successfully.")

if __name__ == "__main__":
    seed_data()
