import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class PlannerAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            temperature=0.4,
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def generate_plan(self, goal, exam_date, daily_hours, weak_subjects):
        prompt = f"""
        You are an Expert Academic Planner. Create a personalized study plan based on the following:
        Goal: {goal}
        Exam Date: {exam_date}
        Daily Availability: {daily_hours} hours
        Weak Subjects: {weak_subjects}
        
        Provide a detailed weekly breakdown with specific focus areas, revision slots, and mock test timings.
        Include productivity tips and a suggested daily routine.
        """
        response = self.llm.invoke(prompt)
        return response.content

class RevisionAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            temperature=0.3,
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def generate_notes(self, topic, subject):
        prompt = f"""
        Generate comprehensive revision notes for the topic '{topic}' in '{subject}'.
        Include:
        1. Key Concepts (Bullet points)
        2. Important Formulas (if applicable)
        3. A "Mental Sandbox" (A relatable scenario to visualize the concept)
        4. Summary (2-3 sentences)
        5. 3 Flashcard questions & answers
        """
        response = self.llm.invoke(prompt)
        return response.content

class MotivationAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            temperature=0.9,
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def get_quote(self, mood="Neutral"):
        prompt = f"""
        Provide a powerful motivational quote and a 2-sentence productivity tip for a student who feels {mood}.
        """
        response = self.llm.invoke(prompt)
        return response.content
