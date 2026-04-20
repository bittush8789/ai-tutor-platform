import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()

class TutorAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile", level="Beginner", subject="General"):
        self.llm = ChatGroq(
            temperature=0.7,
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )
        self.level = level
        self.subject = subject
        # Memory is managed externally via session state
        
        self.system_prompt = f"""
        You are an expert AI Tutor specializing in {subject}. 
        Your goal is to explain concepts to a {level} level student.
        Use clear language, relatable analogies, and step-by-step breakdowns.
        If the student asks a question outside of {subject}, politely remind them that you are their {subject} tutor but try to help if it's related.
        Always encourage the student and provide positive reinforcement.
        """

    def get_response(self, user_input, chat_history=[]):
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=self.system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessage(content=user_input)
        ])
        
        chain = prompt | self.llm
        
        response = chain.invoke({"chat_history": chat_history})
        return response.content

class DoubtSolverAgent:
    def __init__(self, model_name="llama-3.3-70b-versatile"):
        self.llm = ChatGroq(
            temperature=0.2,
            model_name=model_name,
            groq_api_key=os.getenv("GROQ_API_KEY")
        )

    def solve(self, doubt, level="Intermediate"):
        prompt = f"""
        You are a highly efficient AI Doubt Solver. 
        Solve the following doubt for a student at the {level} level.
        Doubt: {doubt}
        
        Provide:
        1. A brief summary of the concept.
        2. A detailed step-by-step explanation or solution.
        3. A "Pro-Tip" for remembering or applying this concept.
        """
        response = self.llm.invoke(prompt)
        return response.content
