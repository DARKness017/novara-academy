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
    
    .stDeployButton {display: none !important;}
    [data-testid="stToolbar"] {display: none !important;}
    [data-testid="stDecoration"] {display: none !important;}
    [data-testid="stStatusWidget"] {display: none !important;}
    [data-testid="viewerBadge"] {display: none !important;}
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 0rem !important;
    }

    /* --- 2. NOVARA ACADEMY BUTTON STYLING --- */
    /* Only the 10 Unit buttons = Deep Navy */
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
    
    /* Primary buttons (Log Out, Start Quiz, Analytics, Difficulty selectors) = Champagne Gold */
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
if 'difficulty' not in st.session_state:
    st.session_state.difficulty = "All" 
if 'selected_unit' not in st.session_state:
    st.session_state.selected_unit = None
if 'selected_unit_name' not in st.session_state:
    st.session_state.selected_unit_name = ""

# --- 4. Core Application Logic (With Adaptive Engine & Difficulty Filtering) ---
def start_quiz(unit=None):
    if unit:
        response = supabase.table("questions").select("*").eq("unit_number", unit).execute()
        questions = response.data
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

    # Filter by selected difficulty if they didn't choose "All"
    if st.session_state.difficulty != "All":
        questions = [q for q in questions if q.get('difficulty') == st.session_state.difficulty]
        
    if questions:
        questions = questions[:10]

    if not questions:
        st.warning(f"No {st.session_state.difficulty} questions found for this selection yet! Please change the difficulty or try another unit.")
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

# --- 5. UI Screens ---
def login_screen():
    st.markdown("<h1 style='text-align: center; color: #0B1B3D;'>🎓 Novara Academy</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'>Secure Adaptive Quiz Engine</h3>", unsafe_allow_html=True)
    st.write("---")

    tab1, tab2 = st.tabs(["Log In", "Create Account"])
    
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
            start_quiz() # No unit means full adaptive engine
        if st.button("📊 View All-Time Analytics", use_container_width=True, type="primary"):
            st.session_state.current_screen = "analytics"
            st.rerun()
            
    st.write("---")
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'>AP Calculus Units</h3>", unsafe_allow_html=True)
    
    units = [
        "Unit 1: Limits & Continuity", 
        "Unit 2: Differentiation (Basics)",
        "Unit 3: Diff (Composite/Implicit)", 
        "Unit 4: Contextual Apps of Diff",
        "Unit 5: Analytical Apps of Diff", 
        "Unit 6: Integration & Accumulation",
        "Unit 7: Differential Equations", 
        "Unit 8: Applications of Integration",
        "Unit 9: Parametric/Polar/Vectors", 
        "Unit 10: Infinite Sequences & Series"
    ]
    
    # Render units in pairs. Clicking any unit opens its dedicated Unit Detail Page.
    for i in range(0, 10, 2):
        c1, c2 = st.columns(2)
        
        with c1:
            if st.button(units[i], use_container_width=True):
                st.session_state.selected_unit = i + 1
                st.session_state.selected_unit_name = units[i]
                st.session_state.current_screen = "unit_detail"
                st.rerun()
                
        with c2:
            if st.button(units[i+1], use_container_width=True):
                st.session_state.selected_unit = i + 2
                st.session_state.selected_unit_name = units[i+1]
                st.session_state.current_screen = "unit_detail"
                st.rerun()

def unit_detail_screen():
    unit_num = st.session_state.selected_unit
    unit_name = st.session_state.selected_unit_name
    
    if st.button("← Back to Dashboard", type="primary"):
        st.session_state.current_screen = "dashboard"
        st.rerun()
        
    st.markdown(f"<h1 style='text-align: center; color: #0B1B3D;'>{unit_name}</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # 1. Difficulty Level Selector for this Unit
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'>Select Difficulty Level</h3>", unsafe_allow_html=True)
    diff_col1, diff_col2, diff_col3, diff_col4 = st.columns(4)
    with diff_col1:
        if st.button("🌐 All", use_container_width=True): st.session_state.difficulty = "All"
    with diff_col2:
        if st.button("🟢 Easy", use_container_width=True): st.session_state.difficulty = "Easy"
    with diff_col3:
        if st.button("🟡 Medium", use_container_width=True): st.session_state.difficulty = "Medium"
    with diff_col4:
        if st.button("🔴 Hard", use_container_width=True): st.session_state.difficulty = "Hard"
        
    st.info(f"**Current Setting:** Quizzes for this unit will pull **{st.session_state.difficulty}** questions.")

    st.write("")
    if st.button(f"🚀 Start Quiz for {unit_name}", type="primary", use_container_width=True):
        start_quiz(unit=unit_num)
        
    st.write("---")
    
    # 2. Formula Cheat Sheet for this Unit
    st.markdown(f"<h3 style='text-align: center; color: #0B1B3D;'>📝 {unit_name} - Formula Cheat Sheet</h3>", unsafe_allow_html=True)
    
    cheat_sheets = {
        1: """
        <div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-radius: 12px; padding: 22px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); font-family: sans-serif; margin-bottom: 20px;">
            <h3 style="color: #C09B5A; text-align: center; margin-top: 0; font-family: sans-serif;">Unit 1: Limits & Continuity — Quick Reference</h3>
            <hr style="border-color: #C09B5A; margin-bottom: 15px;">
            <table style="width: 100%; color: white; border-collapse: collapse; font-size: 14px;">
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; width: 28%; vertical-align: top;">1.1–1.4<br>Intro to Limits</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>AROC (secant slope):</b> $\\text{AROC}=\\frac{f(b)-f(a)}{b-a}$<br><br>
                        <b>IROC (tangent slope):</b> $\\text{IROC}=\\lim_{h\\to0}\\frac{f(x+h)-f(x)}{h}$<br><br>
                        $\\lim_{x\\to c}f(x)=L$ means $f(x)\\to L$ as $x\\to c$ from both sides<br><br>
                        Left-hand: $\\lim_{x\\to c^{-}}f(x)$ &nbsp;|&nbsp; Right-hand: $\\lim_{x\\to c^{+}}f(x)$<br><br>
                        <b>Existence:</b> $\\lim_{x\\to c}f(x)=L \\iff \\lim_{x\\to c^{-}}f(x)=\\lim_{x\\to c^{+}}f(x)=L$
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.5–1.7<br>Algebraic Properties</td>
                    <td style="padding: 10px; vertical-align: top;">
                        Assume $\\lim_{x\\to c}f(x)=L,\\ \\lim_{x\\to c}g(x)=M$:<br>
                        • <b>Sum/Diff:</b> $\\lim[f(x)\\pm g(x)]=L\\pm M$<br>
                        • <b>Product:</b> $\\lim[f(x)g(x)]=LM$<br>
                        • <b>Quotient:</b> $\\lim\\frac{f(x)}{g(x)}=\\frac{L}{M}\\ (M\\neq0)$<br>
                        • <b>Constant:</b> $\\lim[kf(x)]=kL$<br>
                        • <b>Power/Root:</b> $\\lim[f(x)]^n=L^n$, &nbsp; $\\lim\\sqrt[n]{f(x)}=\\sqrt[n]{L}$<br><br>
                        <b>1. Factor:</b> cancel common factors (e.g., $\\frac{x^2-4}{x-2}=\\frac{(x-2)(x+2)}{x-2}$)<br>
                        <b>2. Rationalize:</b> multiply by conjugate $(\\sqrt{a}-b)(\\sqrt{a}+b)=a-b^2$<br>
                        <b>3. Complex Fractions:</b> multiply by LCD to simplify
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.8<br>Squeeze Theorem</td>
                    <td style="padding: 10px; vertical-align: top;">
                        If $g(x)\\le f(x)\\le h(x)$ for all $x$ near $c$ (except possibly at $c$), and $\\lim_{x\\to c}g(x)=\\lim_{x\\to c}h(x)=L$, then $\\lim_{x\\to c}f(x)=L$
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.10–1.13<br>Continuity & Discontinuities</td>
                    <td style="padding: 10px; vertical-align: top;">
                        $f(x)$ is continuous at $x=c$ iff:<br>
                        <b>1.</b> $f(c)$ is defined &nbsp; <b>2.</b> $\\lim_{x\\to c}f(x)$ exists &nbsp; <b>3.</b> $\\lim_{x\\to c}f(x)=f(c)$<br><br>
                        <table style="width: 100%; border: 1px solid #C09B5A; margin: 8px 0; font-size: 13px; border-collapse: collapse;">
                            <tr style="background-color: #122a5c; color: #C09B5A;">
                                <th style="padding: 6px; text-align: left; border: 1px solid #C09B5A;">Type</th>
                                <th style="padding: 6px; text-align: left; border: 1px solid #C09B5A;">Condition</th>
                                <th style="padding: 6px; text-align: left; border: 1px solid #C09B5A;">Graphic</th>
                            </tr>
                            <tr>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">Removable</td>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">$\\lim_{x\\to c}f(x)$ exists, $\\neq f(c)$</td>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">Hole</td>
                            </tr>
                            <tr>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">Jump</td>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">$\\lim_{x\\to c^{-}}f(x)\\neq\\lim_{x\\to c^{+}}f(x)$</td>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">Step break</td>
                            </tr>
                            <tr>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">Infinite</td>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">$\\lim_{x\\to c^{\\pm}}f(x)=\\pm\\infty$</td>
                                <td style="padding: 6px; border: 1px solid #C09B5A;">Vert. asymptote</td>
                            </tr>
                        </table>
                        Continuous on $(a,b)$: continuous at every point.<br>
                        Continuous on $[a,b]$: continuous on $(a,b)$ and $\\lim_{x\\to a^{+}}f(x)=f(a)$, $\\lim_{x\\to b^{-}}f(x)=f(b)$
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.14–1.15<br>Limits at Infinity & Asymptotes</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>Vertical:</b> $x=c$ is asymptote if $\\lim_{x\\to c^{+}}f(x)=\\pm\\infty$ or $\\lim_{x\\to c^{-}}f(x)=\\pm\\infty$<br>
                        <b>Horizontal:</b> $y=L$ is asymptote if $\\lim_{x\\to\\infty}f(x)=L$ or $\\lim_{x\\to-\\infty}f(x)=L$<br><br>
                        Degree of numerator $n$, denominator $m$:<br>
                        • $n<m$ (Bottom Heavy): $\\lim_{x\\to\\pm\\infty}f(x)=0$<br>
                        • $n=m$ (Balanced): $\\lim_{x\\to\\pm\\infty}f(x)=\\frac{a}{b}$<br>
                        • $n>m$ (Top Heavy): $\\lim_{x\\to\\pm\\infty}f(x)=\\pm\\infty$
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.16<br>Intermediate Value Thm (IVT)</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>Conditions:</b> <b>1.</b> $f(x)$ continuous on closed $[a,b]$ &nbsp; <b>2.</b> $u$ strictly between $f(a)$ and $f(b)$, $f(a)\\neq f(b)$<br>
                        <b>Conclusion:</b> there exists at least one $c\\in(a,b)$ such that $f(c)=u$
                    </td>
                </tr>
            </table>
        </div>

        <div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-radius: 12px; padding: 22px; color: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); font-family: sans-serif;">
            <h3 style="color: #C09B5A; text-align: center; margin-top: 0; font-family: sans-serif;">Unit 1: Limits & Continuity — Core Definitions</h3>
            <hr style="border-color: #C09B5A; margin-bottom: 15px;">
            <table style="width: 100%; color: white; border-collapse: collapse; font-size: 14px;">
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; width: 28%; vertical-align: top;">1.1–1.4<br>Core Limit Concepts</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>Def. Limit of a Function:</b> let $f(x)$ be defined on an open interval around $c$ (except possibly at $c$). We say $\\lim_{x\\to c}f(x)=L$ if we can make $f(x)$ arbitrarily close to $L$ by taking $x$ sufficiently close to $c$, from both sides, but not equal to $c$.<br><br>
                        <b>Def. One-Sided Limits:</b><br>
                        Left-hand: $x\\to c$ strictly from values $<c$: $\\lim_{x\\to c^{-}}f(x)$<br>
                        Right-hand: $x\\to c$ strictly from values $>c$: $\\lim_{x\\to c^{+}}f(x)$<br><br>
                        <b>Existence Condition:</b> $\\lim_{x\\to c}f(x)$ exists iff both one-sided limits exist and are equal to the same finite value $L$: $\\lim_{x\\to c^{-}}f(x)=\\lim_{x\\to c^{+}}f(x)=L$
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">Discontinuity Types</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>Jump:</b> left- and right-hand limits both exist as finite numbers, but are unequal: $\\lim_{x\\to c^{-}}f(x)\\neq\\lim_{x\\to c^{+}}f(x)$<br><br>
                        <b>Infinite:</b> one or both one-sided limits approach $\\pm\\infty$ as $x\\to c$
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.14–1.15<br>Asymptotic Behavior</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>Vertical Asymptote:</b> the line $x=c$ is a vertical asymptote of $f(x)$ if the output grows without bound as $x\\to c$: $\\lim_{x\\to c^{+}}f(x)=\\pm\\infty$ or $\\lim_{x\\to c^{-}}f(x)=\\pm\\infty$<br><br>
                        <b>Horizontal Asymptote:</b> the line $y=L$ is a horizontal asymptote if $f$ stabilizes toward $L$ as $x\\to\\pm\\infty$: $\\lim_{x\\to\\infty}f(x)=L$ or $\\lim_{x\\to-\\infty}f(x)=L$
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.5–1.7<br>Indeterminate Forms</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>Def. Indeterminate Form:</b> an algebraic expression obtained by evaluating a limit that does not provide enough information to determine the limit's actual value. The most common structural form is $\\left[\\frac{0}{0}\\right]$. It signals the limit <i>may or may not</i> exist and requires further manipulation (factoring, conjugate rationalization, simplifying complex fractions).
                    </td>
                </tr>
                <tr style="border-bottom: 1px solid #C09B5A;">
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.16<br>Existence Theorems</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>Thm. Intermediate Value Theorem (IVT):</b> if $f$ is continuous on the closed interval $[a,b]$, and $y_0$ is any value strictly between $f(a)$ and $f(b)$, then there must exist at least one value $c\\in(a,b)$ such that $f(c)=y_0$
                    </td>
                </tr>
                <tr>
                    <td style="padding: 10px; font-weight: bold; color: #C09B5A; vertical-align: top;">1.10–1.13<br>Continuity & Discontinuity</td>
                    <td style="padding: 10px; vertical-align: top;">
                        <b>Def. Continuity at a Point:</b> $f$ is continuous at $x=c$ if it satisfies all three: <b>1.</b> $f(c)$ is defined &nbsp; <b>2.</b> $\\lim_{x\\to c}f(x)$ exists &nbsp; <b>3.</b> $\\lim_{x\\to c}f(x)=f(c)$<br><br>
                        <b>Def. Removable Discontinuity:</b> a discontinuity at $x=c$ where $\\lim_{x\\to c}f(x)$ exists, but either $f(c)$ is undefined or $\\lim_{x\\to c}f(x)\\neq f(c)$. Graphically, a single hole in the graph.
                    </td>
                </tr>
            </table>
        </div>
        """,
        2: "### Unit 2: Differentiation (Basics)\n- **Power Rule:** $\\frac{d}{dx}[x^n] = n x^{n-1}$\n- **Product Rule:** $\\frac{d}{dx}[uv] = u'v + uv'$\n- **Quotient Rule:** $\\frac{d}{dx}\\left[\\frac{u}{v}\\right] = \\frac{u'v - uv'}{v^2}$",
        3: "### Unit 3: Differentiation (Composite/Implicit)\n- **Chain Rule:** $\\frac{d}{dx}[f(g(x))] = f'(g(x)) \\cdot g'(x)$\n- **Implicit Differentiation:** Differentiate implicitly with respect to $x$ and solve for $\\frac{dy}{dx}$.",
        4: "### Unit 4: Contextual Applications of Differentiation\n- **Related Rates:** Rate of change with respect to time $t$.\n- **Linear Approximation:** $L(x) = f(a) + f'(a)(x-a)$",
        5: "### Unit 5: Analytical Applications of Differentiation\n- **Mean Value Theorem:** $f'(c) = \\frac{f(b)-f(a)}{b-a}$\n- **First & Second Derivative Tests:** For extrema and concavity.",
        6: "### Unit 6: Integration & Accumulation\n- **Power Rule for Integration:** $\\int x^n dx = \\frac{x^{n+1}}{n+1} + C$\n- **Fundamental Theorem of Calculus:** $\\int_a^b f(x)dx = F(b) - F(a)$",
        7: "### Unit 7: Differential Equations\n- **Separation of Variables:** Separate $x$ and $y$ variables on opposite sides.\n- **Exponential Growth/Decay:** $\\frac{dy}{dt} = ky \\implies y = Ce^{kt}$",
        8: "### Unit 8: Applications of Integration\n- **Area Between Curves:** $\\int_a^b [f(x) - g(x)] dx$\n- **Volume (Disk/Washer):** $V = \\pi \\int_a^b [R(x)]^2 dx$",
        9: "### Unit 9: Parametric, Polar & Vectors\n- **Parametric Derivative:** $\\frac{dy}{dx} = \\frac{dy/dt}{dx/dt}$\n- **Polar Area:** $A = \\frac{1}{2} \\int_a^b [r(\\theta)]^2 d\\theta$",
        10: "### Unit 10: Infinite Sequences & Series\n- **Geometric Series:** $\\sum ar^n = \\frac{a}{1-r}$ (|r| < 1)\n- **Nth Term Test:** If $\\lim a_n \\neq 0$, the series diverges."
    }
    
    st.markdown(cheat_sheets.get(unit_num, "*Add your custom formulas for this unit here!*"))

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
    elif st.session_state.current_screen == "unit_detail":
        unit_detail_screen()
    elif st.session_state.current_screen == "quiz":
        quiz_screen()
    elif st.session_state.current_screen == "analytics":
        analytics_screen()