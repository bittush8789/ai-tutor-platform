import os
import json
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

class QuizAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            temperature=0.5,
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def generate_quiz(self, subject, topic, num_questions=5, difficulty="Medium", quiz_type="MCQ"):
        prompt = f"""
        Generate a {quiz_type} quiz for the subject '{subject}' on the topic '{topic}'.
        Difficulty level: {difficulty}
        Number of questions: {num_questions}
        
        Format the output as a JSON list of objects. Each object should have:
        - "question": The question text.
        - "options": A list of 4 options (for MCQ) or an empty list (for short answer).
        - "answer": The correct answer.
        - "explanation": A brief explanation of why the answer is correct.

        Return ONLY the JSON code block.
        """
        
        response = self.llm.invoke(prompt)
        try:
            # Basic parsing of JSON from response
            content = response.content.strip()
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            return json.loads(content)
        except Exception as e:
            return [{"error": f"Failed to parse quiz: {str(e)}", "raw": response.content}]

    def evaluate_answer(self, question, user_answer, correct_answer):
        prompt = f"""
        Question: {question}
        User Answer: {user_answer}
        Correct Answer: {correct_answer}
        
        Is the user answer correct? Provide feedback.
        """
        response = self.llm.invoke(prompt)
        return response.content
