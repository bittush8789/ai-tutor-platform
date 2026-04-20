import streamlit as st
import pandas as pd
import os
import time
from datetime import datetime
from dotenv import load_dotenv

# Import custom modules
from utils.db import init_db, add_student, log_progress, get_student_progress, get_streak
from utils.tutor import TutorAgent, DoubtSolverAgent
from utils.quiz import QuizAgent
from utils.planner import PlannerAgent, RevisionAgent, MotivationAgent
from utils.rag_engine import RAGAgent
from utils.progress import AnalyticsAgent
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# Initialize Database
if not os.path.exists("data"):
    os.makedirs("data")
init_db()

# Page Config
st.set_page_config(page_title="AI Tutor - Personalized Study Assistant", page_icon="🎓", layout="wide")

# Custom CSS for Premium Look
st.markdown("""
<style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #4CAF50;
        color: white;
    }
    .stTextInput>div>div>input {
        border-radius: 10px;
    }
    .card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        text-align: center;
        padding: 15px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 12px;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("🎓 AI Tutor App")
    st.divider()
    
    student_name = st.text_input("Student Name", value="Bittu Sharma")
    level = st.selectbox("Current Level", ["Beginner", "Intermediate", "Advanced", "School", "College", "Job Seeker"])
    subject = st.selectbox("Focus Subject", [
        "DevOps", "MLOps", "Computer Science", "LLMOps", "Gen AI", "AI Engineering"
    ])
    model_choice = st.selectbox("LLM Model", [
        "llama-3.3-70b-versatile", 
        "llama-4-scout", 
        "gpt-oss-120b",
        "llama3-70b-8192", 
        "llama3-8b-8192", 
        "mixtral-8x7b-32768", 
        "gemma-7b-it"
    ])
    
    st.divider()
    if st.button("Save Profile"):
        sid = add_student(student_name, level, subject)
        st.session_state.student_id = sid
        st.success(f"Profile saved! ID: {sid}")

    st.divider()
    st.info("Upload your notes to ask specific questions.")
    uploaded_file = st.file_uploader("Upload Notes (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])

# Session State Initialization
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'student_id' not in st.session_state:
    st.session_state.student_id = 1 # Default or from DB
if 'vectorstore' not in st.session_state:
    st.session_state.vectorstore = None

# Main Tabs
tabs = st.tabs(["💬 Tutor Chat", "📝 Quiz Center", "📅 Study Planner", "📑 Revision Notes", "📊 Progress", "🔍 Doubt Solver", "🎓 Exam Mode"])

# --- Tab 1: Tutor Chat ---
with tabs[0]:
    st.header(f"Personalized {subject} Tutor")
    
    # RAG Support Check
    if uploaded_file and st.session_state.vectorstore is None:
        with st.spinner("Processing your notes..."):
            rag = RAGAgent(model_name=model_choice)
            # Save temp file
            temp_path = f"data/{uploaded_file.name}"
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.session_state.vectorstore = rag.process_file(temp_path)
            st.success("Notes processed! You can now ask questions about them.")

    # Chat Display
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask your study question..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            if st.session_state.vectorstore and "notes" in prompt.lower():
                rag = RAGAgent(model_name=model_choice)
                response = rag.ask_question(prompt, st.session_state.vectorstore)
            else:
                tutor = TutorAgent(model_name=model_choice, level=level, subject=subject)
                # Convert history to LangChain messages
                formatted_history = []
                for m in st.session_state.chat_history[:-1]: # Exclude the current prompt
                    if m["role"] == "user":
                        formatted_history.append(HumanMessage(content=m["content"]))
                    else:
                        formatted_history.append(AIMessage(content=m["content"]))
                response = tutor.get_response(prompt, chat_history=formatted_history)
            
            st.markdown(response)
            st.session_state.chat_history.append({"role": "assistant", "content": response})

# --- Tab 2: Quiz Center ---
with tabs[1]:
    st.header("Quick Quiz")
    q_col1, q_col2 = st.columns(2)
    with q_col1:
        quiz_topic = st.text_input("Quiz Topic", value=subject)
        quiz_type = st.radio("Quiz Type", ["MCQ", "Short Answer"])
    with q_col2:
        num_q = st.slider("Number of Questions", 1, 10, 5)
        diff_q = st.select_slider("Difficulty", ["Easy", "Medium", "Hard"])

    if st.button("Generate Quiz"):
        quiz_agent = QuizAgent(model_name=model_choice)
        with st.spinner("Generating your quiz..."):
            st.session_state.current_quiz = quiz_agent.generate_quiz(subject, quiz_topic, num_q, diff_q, quiz_type)
            st.session_state.quiz_score = 0
            st.session_state.quiz_submitted = False

    if 'current_quiz' in st.session_state:
        with st.form("quiz_form"):
            user_answers = []
            for i, q in enumerate(st.session_state.current_quiz):
                st.subheader(f"Q{i+1}: {q['question']}")
                if quiz_type == "MCQ":
                    ans = st.radio(f"Select option for Q{i+1}", q['options'], key=f"q_{i}")
                    user_answers.append(ans)
                else:
                    ans = st.text_input(f"Your answer for Q{i+1}", key=f"q_{i}")
                    user_answers.append(ans)
            
            if st.form_submit_button("Submit Quiz"):
                score = 0
                for i, q in enumerate(st.session_state.current_quiz):
                    if user_answers[i] == q['answer']:
                        score += 1
                        st.success(f"Q{i+1} Correct!")
                    else:
                        st.error(f"Q{i+1} Incorrect. Correct answer: {q['answer']}")
                        st.info(f"Explanation: {q['explanation']}")
                
                final_score = (score / len(st.session_state.current_quiz)) * 100
                st.balloons()
                st.metric("Final Score", f"{final_score}%")
                log_progress(st.session_state.student_id, subject, quiz_topic, final_score, len(st.session_state.current_quiz))

# --- Tab 3: Study Planner ---
with tabs[2]:
    st.header("AI Study Planner")
    p_col1, p_col2 = st.columns(2)
    with p_col1:
        goal = st.text_input("Main Goal", placeholder="e.g. Master Calculus for Midterms")
        exam_date = st.date_input("Exam Date")
    with p_col2:
        daily_h = st.number_input("Daily Hours", 1, 12, 4)
        weak_s = st.text_area("Weak Topics", placeholder="e.g. Integration, Derivation")

    if st.button("Generate My Plan"):
        planner = PlannerAgent(model_name=model_choice)
        with st.spinner("Creating your path to success..."):
            plan = planner.generate_plan(goal, exam_date, daily_h, weak_s)
            st.markdown(f"<div class='card'>{plan}</div>", unsafe_allow_html=True)

# --- Tab 4: Revision Notes ---
with tabs[3]:
    st.header("Smart Revision Notes")
    rev_topic = st.text_input("Topic for Revision", value=subject)
    if st.button("Generate Revision Sheet"):
        rev_agent = RevisionAgent(model_name=model_choice)
        with st.spinner("Summarizing concepts..."):
            notes = rev_agent.generate_notes(rev_topic, subject)
            st.markdown(notes)
            st.download_button("Download as Text", notes, file_name=f"{rev_topic}_revision.txt")

# --- Tab 5: Progress Dashboard ---
with tabs[4]:
    st.header(f"Dashboard: {student_name}")
    
    streak = get_streak(st.session_state.student_id)
    d_col1, d_col2, d_col3 = st.columns(3)
    with d_col1:
        st.markdown(f"<div class='metric-card'><h3>🔥 Streak</h3><h1>{streak} Days</h1></div>", unsafe_allow_html=True)
    with d_col2:
        # Mock Motivation
        mot_agent = MotivationAgent(model_name=model_choice)
        quote = mot_agent.get_quote()
        st.info(quote)
    
    st.divider()
    progress_df = get_student_progress(st.session_state.student_id)
    if not progress_df.empty:
        analytics = AnalyticsAgent(progress_df)
        st.plotly_chart(analytics.get_score_trends(), use_container_width=True)
        st.plotly_chart(analytics.get_subject_performance(), use_container_width=True)
        
        st.subheader("Weak Areas Identified")
        weak_df = analytics.get_weak_areas()
        if isinstance(weak_df, pd.DataFrame):
            st.table(weak_df)
        else:
            st.write(weak_df)
    else:
        st.warning("No progress data available yet. Take a quiz to see analytics!")

# --- Tab 6: Doubt Solver ---
with tabs[5]:
    st.header("Instant Doubt Solver")
    doubt_input = st.text_area("What's confusing you?", placeholder="e.g. Explain quantum entanglement for a 10 year old.")
    if st.button("Solve My Doubt"):
        solver = DoubtSolverAgent(model_name=model_choice)
        with st.spinner("Analyzing..."):
            solution = solver.solve(doubt_input, level=level)
            st.markdown(f"<div class='card'>{solution}</div>", unsafe_allow_html=True)

# --- Tab 7: Exam Mode ---
with tabs[6]:
    st.header("Timed Exam Mode")
    st.write("Simulate a real exam environment. Timer starts as soon as you generate.")
    if st.button("Start Exam"):
        st.session_state.exam_start_time = time.time()
        st.session_state.exam_duration = 30 * 60 # 30 minutes
        st.rerun()
    
    if 'exam_start_time' in st.session_state:
        elapsed = time.time() - st.session_state.exam_start_time
        remaining = max(0, st.session_state.exam_duration - elapsed)
        st.progress(remaining / st.session_state.exam_duration)
        st.write(f"Time Remaining: {int(remaining // 60)}m {int(remaining % 60)}s")
        
        if remaining <= 0:
            st.error("Time's up!")
        else:
            st.write("Exam in progress... (Implementation follows Quiz Logic)")

# Footer
st.divider()
st.caption("Built by Antigravity AI - Your Production Ready EdTech Partner")
