import streamlit as st
import pandas as pd
import time
import matplotlib.pyplot as plt
from supabase import create_client, Client
import random

# --- 1. Page Config & Theming ---
st.set_page_config(page_title="Novara Academy - Adaptive Engine", page_icon="🎓", layout="centered")

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    /* --- 1. AGGRESSIVELY REMOVE ALL STREAMLIT BRANDING --- */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Nuke the floating GitHub/Deploy toolbars and Streamlit badges */
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    [data-testid="viewerBadge"] {display: none !important;}
    
    /* Push the app content up so there isn't a massive blank space at the top */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }

    /* --- 2. NOVARA ACADEMY BUTTON STYLING --- */
    /* Default buttons (Unit buttons) = Deep Navy */
    .stButton > button {
        background-color: #0B1B3D !important;
        color: white !important;
        border-radius: 8px !important;
        border: 1px solid #C09B5A !important;
        font-weight: 500;
    }
    .stButton > button:hover {
        background-color: #C09B5A !important;
        color: #0B1B3D !important;
        border: 1px solid #0B1B3D !important;
    }
    
    /* Primary buttons (Log Out, Start Quiz, Analytics, etc.) = Champagne Gold */
    .stButton > button[kind="primary"] {
        background-color: #C09B5A !important;
        color: #0B1B3D !important;
        border-radius: 8px !important;
        border: 1px solid #0B1B3D !important;
        font-weight: 600;
    }
    .stButton > button[kind="primary"]:hover {
        background-color: #0B1B3D !important;
        color: white !important;
        border: 1px solid #0B1B3D !important;
    }
    </style>
""", unsafe_allow_html=True)

# --- 2. Cloud Database Connection (Supabase) ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- 3. Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'current_screen' not in st.session_state:
    st.session_state.current_screen = "login"
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'quiz_questions' not in st.session_state:
    st.session_state.quiz_questions = []
if 'q_start_time' not in st.session_state:
    st.session_state.q_start_time = 0
if 'quiz_score' not in st.session_state:
    st.session_state.quiz_score = 0

# --- 4. Core Application Logic (Now with Adaptive Engine!) ---
def start_quiz(unit=None):
    if unit:
        response = supabase.table("questions").select("*").eq("unit_number", unit).execute()
        questions = response.data
        if questions:
            random.shuffle(questions)
    else:
        all_questions_response = supabase.table("questions").select("*").execute()
        all_questions = all_questions_response.data
        
        attempts_response = supabase.table("attempts").select("is_correct, questions(unit_number)").eq("user_id", st.session_state.user_id).execute()
        attempts = attempts_response.data
        
        weak_units = []
        if attempts:
            unit_stats = {}
            for a in attempts:
                if a.get('questions'):
                    u = a['questions']['unit_number']
                    if u not in unit_stats:
                        unit_stats[u] = {'correct': 0, 'total': 0}
                    unit_stats[u]['total'] += 1
                    unit_stats[u]['correct'] += a['is_correct']
            
            for u, stats in unit_stats.items():
                if (stats['correct'] / stats['total']) < 0.60:
                    weak_units.append(u)
        
        if weak_units:
            st.toast(f"🧠 Adaptive Engine Triggered: Prioritizing Units {weak_units}", icon="🎯")
            weak_q = [q for q in all_questions if q['unit_number'] in weak_units]
            strong_q = [q for q in all_questions if q['unit_number'] not in weak_units]
            random.shuffle(weak_q)
            random.shuffle(strong_q)
            questions = weak_q + strong_q
        else:
            questions = all_questions
            if questions:
                random.shuffle(questions)
            
        if questions:
            questions = questions[:10]

    if not questions:
        st.warning("No questions found for this selection yet! Please try another unit.")
        return
        
    st.session_state.quiz_questions = questions
    st.session_state.current_q_index = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_started = True
    st.session_state.q_start_time = time.time()
    st.session_state.current_screen = "quiz"
    st.rerun()

def submit_answer(selected_option):
    end_time = time.time()
    time_taken = int(end_time - st.session_state.q_start_time)
    
    current_q = st.session_state.quiz_questions[st.session_state.current_q_index]
    is_correct = 1 if selected_option == current_q['correct_option'] else 0
    
    if is_correct:
        st.session_state.quiz_score += 1

    supabase.table("attempts").insert({
        "user_id": st.session_state.user_id,
        "question_id": current_q['question_id'],
        "selected_option": selected_option,
        "is_correct": is_correct,
        "time_taken_seconds": time_taken
    }).execute()
    
    st.session_state.current_q_index += 1
    st.session_state.q_start_time = time.time()
    st.rerun()

# --- 5. UI Screens (NOW WITH ENTERPRISE AUTH) ---
def login_screen():
    st.markdown("<h1 style='text-align: center; color: #0B1B3D;'>🎓 Novara Academy</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'>Secure Adaptive Quiz Engine</h3>", unsafe_allow_html=True)
    st.write("---")

    # 👇 THIS IS THE NEW 3-TAB SYSTEM!
    tab1, tab2, tab3 = st.tabs(["Log In", "Create Account", "Forgot Password"])
    
    with tab1:
        login_email = st.text_input("Email Address", key="login_email")
        login_password = st.text_input("Password", type="password", key="login_password")
        if st.button("Log In", type="primary"):
            if login_email and login_password:
                try:
                    auth_response = supabase.auth.sign_in_with_password({"email": login_email, "password": login_password})
                    user_record = supabase.table("users").select("*").eq("email", login_email).execute()
                    if user_record.data:
                        user = user_record.data[0]
                        st.session_state.logged_in = True
                        st.session_state.user_id = user['user_id']
                        st.session_state.username = user['username']
                        st.session_state.current_screen = "dashboard"
                        st.success(f"Welcome back, {user['username']}!")
                        time.sleep(1)
                        st.rerun()
                except Exception as e:
                    st.error("Invalid email or password. Please try again.")
            else:
                st.warning("Please fill in both fields.")

    with tab2:
        reg_username = st.text_input("Full Name / Username", key="reg_username")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        if st.button("Create Account", type="primary"):
            if reg_username and reg_email and reg_password:
                try:
                    auth_response = supabase.auth.sign_up({"email": reg_email, "password": reg_password})
                    check = supabase.table("users").select("*").eq("email", reg_email).execute()
                    if not check.data:
                        supabase.table("users").insert({
                            "username": reg_username,
                            "email": reg_email,
                            "password_hash": "SECURED_BY_SUPABASE_AUTH" 
                        }).execute()
                    st.success("✅ Account created successfully! You can now Log In.")
                except Exception as e:
                    st.error(f"Registration failed: An account with this email may already exist.")
            else:
                st.warning("Please fill in all fields.")
                
    with tab3:
        st.markdown("### 🔒 Reset Your Password")
        st.write("Enter your email address and we will send you a secure reset link.")
        reset_email = st.text_input("Account Email", key="reset_email")
        if st.button("Send Reset Link", type="primary"):
            if reset_email:
                try:
                    supabase.auth.reset_password_for_email(reset_email)
                    st.success("✅ Secure reset link sent! Please check your email inbox.")
                except Exception as e:
                    st.error("Could not send reset link. Ensure the email is correct.")
            else:
                st.warning("Please enter your email address.")

def dashboard_screen():
    st.markdown(f"<h1 style='text-align: center; color: #0B1B3D;'>Welcome, {st.session_state.username}!</h1>", unsafe_allow_html=True)
    st.write("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("↩️ Log Out", use_container_width=True, type="primary"):
            supabase.auth.sign_out() 
            st.session_state.clear()
            st.rerun()
        st.write("")
        if st.button("🚀 Start Full Adaptive Quiz", type="primary", use_container_width=True):
            start_quiz()
        if st.button("📊 View All-Time Analytics", use_container_width=True, type="primary"):
            st.session_state.current_screen = "analytics"
            st.rerun()
            
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'>AP Calculus Units</h3>", unsafe_allow_html=True)
    
    units = [
        "Unit 1: Limits & Continuity", "Unit 2: Differentiation (Basics)",
        "Unit 3: Diff (Composite/Implicit)", "Unit 4: Contextual Apps of Diff",
        "Unit 5: Analytical Apps of Diff", "Unit 6: Integration & Accumulation",
        "Unit 7: Differential Equations", "Unit 8: Applications of Integration",
        "Unit 9: Parametric/Polar/Vectors", "Unit 10: Infinite Sequences & Series"
    ]
    
    for i in range(0, 10, 2):
        c1, c2 = st.columns(2)
        with c1:
            if st.button(units[i], use_container_width=True):
                start_quiz(i + 1)
        with c2:
            if st.button(units[i+1], use_container_width=True):
                start_quiz(i + 2)

def quiz_screen():
    if st.session_state.current_q_index >= len(st.session_state.quiz_questions):
        st.success(f"Quiz Complete! Score: {st.session_state.quiz_score}/{len(st.session_state.quiz_questions)}")
        if st.button("Return to Dashboard", type="primary"):
            st.session_state.quiz_started = False
            st.session_state.current_screen = "dashboard"
            st.rerun()
        return

    q = st.session_state.quiz_questions[st.session_state.current_q_index]
    st.progress((st.session_state.current_q_index) / len(st.session_state.quiz_questions))
    st.markdown(f"**Question {st.session_state.current_q_index + 1} of {len(st.session_state.quiz_questions)}** (Unit {q['unit_number']} - {q['difficulty']})")
    
    st.markdown(f"### {q['question_text']}")
    
    options = {
        "A": q['option_a'],
        "B": q['option_b'],
        "C": q['option_c'],
        "D": q['option_d']
    }
    
    with st.form(key="quiz_form"):
        choice_label = st.radio("Select your answer:", ["A", "B", "C", "D"], format_func=lambda x: f"{x}) {options[x]}")
        submit = st.form_submit_button("Submit Answer", type="primary")
        if submit:
            submit_answer(choice_label)

def analytics_screen():
    st.markdown("<h1 style='text-align: center; color: #0B1B3D;'>📊 Performance Analytics</h1>", unsafe_allow_html=True)
    
    response = supabase.table("attempts").select("is_correct, time_taken_seconds, questions(unit_number)").eq("user_id", st.session_state.user_id).execute()
    data = response.data
    
    if data:
        processed = []
        slow_units = set() 
        
        for item in data:
            if item.get('questions'):
                unit_num = item['questions']['unit_number']
                processed.append({"unit": f"Unit {unit_num}", "correct": item['is_correct']})
                
                if item['is_correct'] == 1 and item['time_taken_seconds'] > 90:
                    slow_units.add(unit_num)
        
        if processed:
            df = pd.DataFrame(processed)
            summary = df.groupby('unit')['correct'].mean() * 100
            
            fig, ax = plt.subplots(figsize=(8, 4))
            summary.plot(kind='bar', ax=ax, color='#0B1B3D', edgecolor='#C09B5A', width=0.7)
            
            ax.set_ylabel('Accuracy (%)')
            ax.set_ylim(0, 100)
            ax.axhline(60, color='#C09B5A', linestyle='--', label='60% Threshold')
            ax.legend()
            
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            plt.xticks(rotation=0)
            
            st.pyplot(fig)
            
            if slow_units:
                sorted_slow = sorted(list(slow_units))
                st.warning(f"⏱️ **Speed Improvement Needed:** You have correct answers that took longer than 90 seconds in **Units: {', '.join(map(str, sorted_slow))}**. The AP exam requires faster pacing here!")
        else:
            st.info("No unit data found for your attempts.")
    else:
        st.info("You haven't taken any quizzes yet! Start a quiz to see your analytics.")
        
    if st.button("← Back to Dashboard", type="primary"):
        st.session_state.current_screen = "dashboard"
        st.rerun()

# --- 6. Screen Router ---
if not st.session_state.logged_in:
    login_screen()
else:
    if st.session_state.current_screen == "dashboard":
        dashboard_screen()
    elif st.session_state.current_screen == "quiz":
        quiz_screen()
    elif st.session_state.current_screen == "analytics":
        analytics_screen()