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

    /* --- 3. NATIVE MARKDOWN TABLE STYLING (For Perfect Math Rendering) --- */
    .stMarkdown table {
        background-color: #0B1B3D !important;
        border: 2px solid #C09B5A !important;
        border-top: none !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        color: white !important;
        width: 100% !important;
        margin-top: -10px !important; /* Pulls it flush with the header div */
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    .stMarkdown th {
        display: none !important; /* Hides the default markdown headers */
    }
    .stMarkdown td {
        border-bottom: 1px solid #C09B5A !important;
        border-top: none !important;
        border-right: none !important;
        border-left: none !important;
        padding: 15px !important;
        vertical-align: top !important;
        font-size: 14px !important;
    }
    .stMarkdown tr:last-child td {
        border-bottom: none !important; /* Removes border from last row */
    }
    /* Style the left column specifically to be Gold and Bold */
    .stMarkdown td:first-child {
        color: #C09B5A !important;
        font-weight: bold !important;
        width: 28% !important;
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

# --- 4. Core Application Logic ---
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
            start_quiz()
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
    cheat_sheets = {
        1: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 1: Limits & Continuity — Quick Reference</h3>
</div>

| | |
|---|---|
| **1.1–1.4**<br>Intro to Limits | **AROC (secant slope):** $\text{AROC}=\frac{f(b)-f(a)}{b-a}$<br><br>**IROC (tangent slope):** $\text{IROC}=\lim_{h\to0}\frac{f(x+h)-f(x)}{h}$<br><br>$\lim_{x\to c}f(x)=L$ means $f(x)\to L$ as $x\to c$ from both sides<br><br>Left-hand: $\lim_{x\to c^{-}}f(x)$ &nbsp;&nbsp;\|&nbsp;&nbsp; Right-hand: $\lim_{x\to c^{+}}f(x)$<br><br>**Existence:** $\lim_{x\to c}f(x)=L \iff \lim_{x\to c^{-}}f(x)=\lim_{x\to c^{+}}f(x)=L$ |
| **1.5–1.7**<br>Algebraic Properties | Assume $\lim_{x\to c}f(x)=L,\ \lim_{x\to c}g(x)=M$:<br>• **Sum/Diff:** $\lim[f(x)\pm g(x)]=L\pm M$<br>• **Product:** $\lim[f(x)g(x)]=LM$<br>• **Quotient:** $\lim\frac{f(x)}{g(x)}=\frac{L}{M}\ (M\neq0)$<br>• **Constant:** $\lim[kf(x)]=kL$<br>• **Power/Root:** $\lim[f(x)]^n=L^n$, &nbsp; $\lim\sqrt[n]{f(x)}=\sqrt[n]{L}$<br><br>**1. Factor:** cancel common factors (e.g., $\frac{x^2-4}{x-2}=\frac{(x-2)(x+2)}{x-2}$)<br>**2. Rationalize:** multiply by conjugate $(\sqrt{a}-b)(\sqrt{a}+b)=a-b^2$<br>**3. Complex Fractions:** multiply by LCD to simplify |
| **1.8**<br>Squeeze Theorem | If $g(x)\le f(x)\le h(x)$ for all $x$ near $c$ (except possibly at $c$), and $\lim_{x\to c}g(x)=\lim_{x\to c}h(x)=L$, then $\lim_{x\to c}f(x)=L$ |
| **1.10–1.13**<br>Continuity & Discontinuities | $f(x)$ is continuous at $x=c$ iff:<br>**1.** $f(c)$ is defined &nbsp; **2.** $\lim_{x\to c}f(x)$ exists &nbsp; **3.** $\lim_{x\to c}f(x)=f(c)$<br><br>**Types:**<br>• **Removable:** $\lim_{x\to c}f(x)$ exists, $\neq f(c)$ (Hole)<br>• **Jump:** $\lim_{x\to c^{-}}f(x)\neq\lim_{x\to c^{+}}f(x)$ (Step break)<br>• **Infinite:** $\lim_{x\to c^{\pm}}f(x)=\pm\infty$ (Vert. asymptote)<br><br>Continuous on $(a,b)$: continuous at every point.<br>Continuous on $[a,b]$: continuous on $(a,b)$ and $\lim_{x\to a^{+}}f(x)=f(a)$, $\lim_{x\to b^{-}}f(x)=f(b)$ |
| **1.14–1.15**<br>Limits at Infinity & Asymptotes | **Vertical:** $x=c$ is asymptote if $\lim_{x\to c^{+}}f(x)=\pm\infty$ or $\lim_{x\to c^{-}}f(x)=\pm\infty$<br>**Horizontal:** $y=L$ is asymptote if $\lim_{x\to\infty}f(x)=L$ or $\lim_{x\to-\infty}f(x)=L$<br><br>Degree of numerator $n$, denominator $m$:<br>• $n<m$ (Bottom Heavy): $\lim_{x\to\pm\infty}f(x)=0$<br>• $n=m$ (Balanced): $\lim_{x\to\pm\infty}f(x)=\frac{a}{b}$<br>• $n>m$ (Top Heavy): $\lim_{x\to\pm\infty}f(x)=\pm\infty$ |
| **1.16**<br>Intermediate Value Thm (IVT) | **Conditions:** **1.** $f(x)$ continuous on closed $[a,b]$ &nbsp; **2.** $u$ strictly between $f(a)$ and $f(b)$, $f(a)\neq f(b)$<br>**Conclusion:** there exists at least one $c\in(a,b)$ such that $f(c)=u$ |

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 1: Limits & Continuity — Core Definitions</h3>
</div>

| | |
|---|---|
| **1.1–1.4**<br>Core Limit Concepts | **Def. Limit of a Function:** let $f(x)$ be defined on an open interval around $c$ (except possibly at $c$). We say $\lim_{x\to c}f(x)=L$ if we can make $f(x)$ arbitrarily close to $L$ by taking $x$ sufficiently close to $c$, from both sides, but not equal to $c$.<br><br>**Def. One-Sided Limits:**<br>Left-hand: $x\to c$ strictly from values $<c$: $\lim_{x\to c^{-}}f(x)$<br>Right-hand: $x\to c$ strictly from values $>c$: $\lim_{x\to c^{+}}f(x)$<br><br>**Existence Condition:** $\lim_{x\to c}f(x)$ exists iff both one-sided limits exist and are equal to the same finite value $L$: $\lim_{x\to c^{-}}f(x)=\lim_{x\to c^{+}}f(x)=L$ |
| **Discontinuity Types** | **Jump:** left- and right-hand limits both exist as finite numbers, but are unequal: $\lim_{x\to c^{-}}f(x)\neq\lim_{x\to c^{+}}f(x)$<br><br>**Infinite:** one or both one-sided limits approach $\pm\infty$ as $x\to c$ |
| **1.14–1.15**<br>Asymptotic Behavior | **Vertical Asymptote:** the line $x=c$ is a vertical asymptote of $f(x)$ if the output grows without bound as $x\to c$: $\lim_{x\to c^{+}}f(x)=\pm\infty$ or $\lim_{x\to c^{-}}f(x)=\pm\infty$<br><br>**Horizontal Asymptote:** the line $y=L$ is a horizontal asymptote if $f$ stabilizes toward $L$ as $x\to\pm\infty$: $\lim_{x\to\infty}f(x)=L$ or $\lim_{x\to-\infty}f(x)=L$ |
| **1.5–1.7**<br>Indeterminate Forms | **Def. Indeterminate Form:** an algebraic expression obtained by evaluating a limit that does not provide enough information to determine the limit's actual value. The most common structural form is $\left[\frac{0}{0}\right]$. It signals the limit *may or may not* exist and requires further manipulation (factoring, conjugate rationalization, simplifying complex fractions). |
| **1.16**<br>Existence Theorems | **Thm. Intermediate Value Theorem (IVT):** if $f$ is continuous on the closed interval $[a,b]$, and $y_0$ is any value strictly between $f(a)$ and $f(b)$, then there must exist at least one value $c\in(a,b)$ such that $f(c)=y_0$ |
| **1.10–1.13**<br>Continuity & Discontinuity | **Def. Continuity at a Point:** $f$ is continuous at $x=c$ if it satisfies all three: **1.** $f(c)$ is defined &nbsp; **2.** $\lim_{x\to c}f(x)$ exists &nbsp; **3.** $\lim_{x\to c}f(x)=f(c)$<br><br>**Def. Removable Discontinuity:** a discontinuity at $x=c$ where $\lim_{x\to c}f(x)$ exists, but either $f(c)$ is undefined or $\lim_{x\to c}f(x)\neq f(c)$. Graphically, a single hole in the graph. |
""",
        2: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 2: Derivatives — Quick Reference</h3>
</div>

| | |
|---|---|
| **2.1–2.3**<br>Rates of Change & Def. of the Derivative | **AROC** (secant slope over $[a,b]$): $\text{AROC}=\frac{f(b)-f(a)}{b-a}$<br><br>**IROC** (tangent slope at $x=c$): $\text{IROC}=\lim_{h\to0}\frac{f(c+h)-f(c)}{h}$<br><br>**Limit Def. (General):** $f'(x)=\lim_{h\to0}\frac{f(x+h)-f(x)}{h}$<br><br>**Alt. Def. at a Point:** $f'(c)=\lim_{x\to c}\frac{f(x)-f(c)}{x-c}$<br><br>**Tangent Line** to $f(x)$ at $(c,f(c))$: $y-f(c)=f'(c)(x-c)$<br><br>**Estimating from Table Data:** for $x_1<c<x_2$: $f'(c)\approx\frac{f(x_2)-f(x_1)}{x_2-x_1}$ |
| **2.4**<br>Differentiability & Continuity | $f(x)$ is differentiable at $x=c$ if $f'(c)$ exists.<br><br>**Existence:** $f'(c)$ exists iff $\lim_{h\to0^{-}}\frac{f(c+h)-f(c)}{h}=\lim_{h\to0^{+}}\frac{f(c+h)-f(c)}{h}$<br><br>**Differentiability $\implies$ Continuity:** if $f$ differentiable at $x=c$, then $f$ continuous at $x=c$ (converse not always true, e.g., $f(x)=\lvert x \rvert$) |
| **2.5–2.6**<br>Basic Rules & Geometric Lines | Assume $c$ constant, $f(x),g(x)$ differentiable:<br><br>**Constant:** $\frac{d}{dx}(c)=0$ &nbsp;&nbsp;\|&nbsp;&nbsp; **Power:** $\frac{d}{dx}(x^n)=nx^{n-1}$<br><br>**Const. Multiple:** $\frac{d}{dx}[c\cdot f(x)]=c\cdot f'(x)$<br><br>**Sum/Diff:** $\frac{d}{dx}[f(x)\pm g(x)]=f'(x)\pm g'(x)$<br><br>**Geometric Lines:**<br>• **Horiz. Tangent:** $f'(x)=0 \implies y=f(c)$<br>• **Vert. Tangent:** $f'(x)\to\pm\infty \implies x=c$<br>• **Normal Line:** slope $=-\frac{1}{f'(c)} \implies y-f(c)=-\frac{1}{f'(c)}(x-c)$ |
| **2.7, 2.10**<br>Transcendental & Trig Derivatives | $\frac{d}{dx}(\sin x)=\cos x$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\frac{d}{dx}(\cos x)=-\sin x$<br><br>$\frac{d}{dx}(\tan x)=\sec^2 x$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\frac{d}{dx}(\cot x)=-\csc^2 x$<br><br>$\frac{d}{dx}(\sec x)=\sec x\tan x$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\frac{d}{dx}(\csc x)=-\csc x\cot x$<br><br>$\frac{d}{dx}(e^x)=e^x$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\frac{d}{dx}(\ln x)=\frac{1}{x}\ (x>0)$ |
| **2.8–2.9**<br>Product & Quotient Rules | **Product Rule:** $\frac{d}{dx}[f(x)g(x)]=f'(x)g(x)+f(x)g'(x)$<br><br>**Quotient Rule:** $\frac{d}{dx}\left[\frac{f(x)}{g(x)}\right]=\frac{f'(x)g(x)-f(x)g'(x)}{[g(x)]^2}$ |

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 2: Derivatives — Core Definitions</h3>
</div>

| | |
|---|---|
| **2.1**<br>Average & Instantaneous Rate of Change | **Average Rate of Change (AROC):**<br>*Definition:* the change in the dependent variable divided by the change in the independent variable over a specified interval.<br>*Graphical Meaning:* the slope of the secant line passing through two distinct points on a curve.<br><br>**Instantaneous Rate of Change (IROC):**<br>*Definition:* the rate of change of a function at a single, exact moment in time.<br>*Graphical Meaning:* the slope of the tangent line to the curve at that specific point, evaluated by taking the limit of the average rate of change as the interval length approaches zero. |
| **2.2**<br>Defining the Derivative | **Derivative:**<br>*Definition:* a fundamental calculus function or value that measures the instantaneous rate of change of a dependent variable with respect to an independent variable.<br>*Graphical Meaning:* it represents the localized behavior and limiting trajectory of a function at any given point.<br><br>**Difference Quotient:**<br>*Definition:* the mathematical expression $\frac{f(x+h)-f(x)}{h}$ or $\frac{f(x)-f(c)}{x-c}$ that calculates the slope of a secant line.<br>*Graphical Meaning:* it serves as the foundational algebraic expression inside the limit definition of a derivative.<br><br>**Tangent Line:**<br>*Definition:* a straight line that locally touches a curve at a single point.<br>*Graphical Meaning:* sharing the exact same slope as the curve's instantaneous rate of change at that specific location. |
| **2.4**<br>Differentiability & Continuity | **Differentiability:**<br>*Definition:* the property of a function meaning its derivative exists at a given point or over an open interval.<br>*Graphical Meaning:* graphically, the curve must be locally linear, completely smooth (no sharp turns, corners, or cusps), and lack vertical tangents.<br><br>**Continuity:**<br>*Definition:* the structural property where a function has no breaks, holes, jumps, or vertical asymptotes over an interval.<br>*Graphical Meaning:* while differentiability guarantees continuity, a function can be continuous without being differentiable. |
| **2.6**<br>Geometric Lines | **Normal Line:**<br>*Definition:* a straight line that is perpendicular to the tangent line of a curve at the specific point of tangency.<br>*Graphical Meaning:* its slope is the negative reciprocal of the derivative at that point.<br><br>**Horizontal Tangent:**<br>*Definition:* a tangent line with a slope equal to zero ($f'(x)=0$).<br>*Graphical Meaning:* indicating a point on the function where the curve momentarily levels out, often corresponding to local extrema.<br><br>**Vertical Tangent:**<br>*Definition:* a line passing through a point where a continuous function becomes extremely steep.<br>*Graphical Meaning:* causing the limit of the derivative to approach $\infty$ or $-\infty$, making the function non-differentiable at that point. |
""",
        3: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 3: Differentiation Rules — Quick Reference</h3>
</div>

| | |
|---|---|
| **3.1**<br>The Chain Rule | For composite functions $y=f(g(x))$:<br><br>$\frac{d}{dx}\big[f(g(x))\big]=f'(g(x))\cdot g'(x)$<br><br>**Leibniz form:** if $y=f(u)$ and $u=g(x)$: $\frac{dy}{dx}=\frac{dy}{du}\cdot\frac{du}{dx}$<br><br>**General Power Rule:** $\frac{d}{dx}\big[(g(x))^n\big]=n(g(x))^{n-1}\cdot g'(x)$ |
| **3.2**<br>Implicit Differentiation | Differentiate both sides of an equation in $x$ and $y$ with respect to $x$, treating $y$ as a function of $x$: apply the Chain Rule to every $y$-term, attaching $\frac{dy}{dx}$<br><br>Example: $\frac{d}{dx}(y^2)=2y\frac{dy}{dx}$<br><br>Then collect all $\frac{dy}{dx}$ terms and solve algebraically for $\frac{dy}{dx}$ |
| **3.3**<br>Differentiating Inverse Functions | If $g=f^{-1}$ (i.e., $f(g(x))=x$), and $f$ is differentiable and invertible near the relevant points:<br><br>$g'(x)=\frac{1}{f'(g(x))}$<br><br>**At a specific point:** if $f(a)=b$, then $\big(f^{-1}\big)'(b)=\frac{1}{f'(a)}$ |
| **3.4**<br>Inverse Trig Derivatives | $\frac{d}{dx}\big[\sin^{-1}(x)\big]=\frac{1}{\sqrt{1-x^2}}$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\frac{d}{dx}\big[\cos^{-1}(x)\big]=\frac{-1}{\sqrt{1-x^2}}$<br><br>$\frac{d}{dx}\big[\tan^{-1}(x)\big]=\frac{1}{1+x^2}$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\frac{d}{dx}\big[\cot^{-1}(x)\big]=\frac{-1}{1+x^2}$<br><br>$\frac{d}{dx}\big[\sec^{-1}(x)\big]=\frac{1}{\lvert x \rvert\sqrt{x^2-1}}$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\frac{d}{dx}\big[\csc^{-1}(x)\big]=\frac{-1}{\lvert x \rvert\sqrt{x^2-1}}$<br><br>(Chain Rule applies: replace $x$ with $u(x)$ and multiply by $u'(x)$) |
| **3.5**<br>Selecting Procedures | Decision checklist for $\frac{d}{dx}$:<br>• **1.** Product of two functions? $\implies$ Product Rule<br>• **2.** Quotient of two functions? $\implies$ Quotient Rule<br>• **3.** Function inside a function? $\implies$ Chain Rule<br>• **4.** $y$ and $x$ mixed/not solved for $y$? $\implies$ Implicit Diff.<br>• **5.** Inverse function notation ($f^{-1}$, $\sin^{-1}$, etc.)? $\implies$ Inverse rules<br><br>Rules often combine — apply outer-to-inner, then simplify |
| **3.6**<br>Higher-Order Derivatives | $f'(x)$: 1st derivative &nbsp;&nbsp;\|&nbsp;&nbsp; $f''(x)=\frac{d}{dx}\big[f'(x)\big]$: 2nd derivative<br><br>$f'''(x)$: 3rd derivative &nbsp;&nbsp;\|&nbsp;&nbsp; $f^{(n)}(x)$: $n$th derivative<br><br>**Leibniz notation:** $\frac{d^2y}{dx^2},\ \frac{d^3y}{dx^3},\ \frac{d^ny}{dx^n}$<br><br>**Implicit 2nd derivative:** differentiate the expression for $\frac{dy}{dx}$ again, substituting the original expression for $\frac{dy}{dx}$ where it reappears |

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 3: Differentiation Rules — Core Definitions</h3>
</div>

| | |
|---|---|
| **3.1**<br>The Chain Rule | **Composite Function:**<br>*Definition:* a function formed when the output of one function, $g(x)$, is used as the input of another function, $f$, written $f(g(x))$.<br>*Graphical Meaning:* the rate of change of the composite is the product of the rates of change of each layer — the "outer" function's sensitivity scaled by the "inner" function's own rate of change. |
| **3.2**<br>Implicit Differentiation | **Implicit Relation:**<br>*Definition:* an equation relating $x$ and $y$ that is not (or cannot easily be) solved explicitly for $y$ in terms of $x$, e.g., $x^2+y^2=25$.<br>*Graphical Meaning:* the curve may not pass the vertical line test as a single function, yet $\frac{dy}{dx}$ still gives the slope of the tangent line at a given point on the curve. |
| **3.3**<br>Differentiating Inverse Functions | **Inverse Function:**<br>*Definition:* a function $g=f^{-1}$ that reverses the mapping of $f$, satisfying $f(g(x))=x$ and $g(f(x))=x$ on the appropriate domains.<br>*Graphical Meaning:* the graph of $f^{-1}$ is the reflection of the graph of $f$ across the line $y=x$; consequently, the slope of $f^{-1}$ at a point is the reciprocal of the slope of $f$ at the corresponding reflected point. |
| **3.4**<br>Inverse Trig Derivatives | **Inverse Trigonometric Function:**<br>*Definition:* the restricted-domain inverse of a trigonometric function (e.g., $\sin^{-1}(x)$ is the inverse of $\sin(x)$ restricted to $\left[-\frac{\pi}{2},\frac{\pi}{2}\right]$), returning the angle whose trig ratio is $x$.<br>*Graphical Meaning:* derived by applying implicit differentiation to the original trig equation and using a reference triangle to rewrite the result purely in terms of $x$. |
| **3.5**<br>Selecting Procedures | **Procedural Fluency:**<br>*Definition:* the skill of identifying a function's structure (product, quotient, composition, implicit relation, or inverse) before differentiating, in order to correctly select and combine the applicable derivative rule(s).<br>*Graphical Meaning:* regardless of the algebraic path taken, all correct procedures converge on the same tangent-line slope at a given point. |
| **3.6**<br>Higher-Order Derivatives | **Higher-Order Derivative:**<br>*Definition:* the result of differentiating a function more than once; the $n$th derivative $f^{(n)}(x)$ is obtained by differentiating $f$ a total of $n$ times.<br>*Graphical Meaning:* $f'$ describes the slope of $f$; $f''$ describes the concavity (rate of change of the slope) of $f$; each successive derivative describes the rate of change of the previous one. |
""",
        4: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 4: Contextual Applications — Quick Reference</h3>
</div>

| | |
|---|---|
| **4.1**<br>Interpreting the Derivative in Context | $f'(a)$ = instantaneous rate of change of $f$ with respect to its input, at $x=a$<br><br>**Units:** $f'(a)$ has units of $\frac{\text{units of }f}{\text{units of }x}$<br><br>Always interpret in a full sentence: "At [input value/context], [quantity] is [increasing/decreasing] at a rate of [value] [units]" |
| **4.2**<br>Motion: Position, Velocity, Acceleration | Position: $s(t)$ &nbsp;&nbsp;\|&nbsp;&nbsp; Velocity: $v(t)=s'(t)$ &nbsp;&nbsp;\|&nbsp;&nbsp; Accel.: $a(t)=v'(t)=s''(t)$<br><br>**Speed** $=\lvert v(t) \rvert$<br><br>**Speeding up:** $v(t)$ and $a(t)$ have the *same* sign<br>**Slowing down:** $v(t)$ and $a(t)$ have *opposite* signs<br><br>At rest / changing direction: $v(t)=0$ and $v$ changes sign |
| **4.3**<br>Rates of Change (Non-Motion) | Same derivative structure applied to other quantities: $\frac{dV}{dt}$ (volume), $\frac{dP}{dt}$ (population), $\frac{dC}{dx}$ (cost), etc.<br><br>Positive rate $\implies$ quantity increasing &nbsp;&nbsp;\|&nbsp;&nbsp; Negative rate $\implies$ quantity decreasing<br><br>Marginal quantity (e.g., marginal cost) $\approx$ derivative evaluated at that input |
| **4.4–4.5**<br>Related Rates | **Procedure:**<br>• **1.** Draw a diagram; label all variables<br>• **2.** Write an equation relating the variables (e.g., geometry formula)<br>• **3.** Differentiate both sides implicitly with respect to $t$<br>• **4.** Substitute known values *after* differentiating<br>• **5.** Solve for the desired rate; include units<br><br>Common relations: $A=\pi r^2$, $V=\frac{4}{3}\pi r^3$, $V=\pi r^2h$, $c^2=a^2+b^2$, $\tan\theta=\frac{y}{x}$ |
| **4.6**<br>Local Linearity & Linearization | **Tangent Line Approximation:** $L(x)=f(a)+f'(a)(x-a)$<br><br>Approximate: $f(x)\approx L(x)$ for $x$ near $a$<br><br>**Over/Underestimate:**<br>• $f$ concave up ($f''>0$): tangent line lies *below* $f \implies L(x)$ underestimates<br>• $f$ concave down ($f''<0$): tangent line lies *above* $f \implies L(x)$ overestimates |
| **4.7**<br>L'Hopital's Rule | If $\lim_{x\to c}\frac{f(x)}{g(x)}$ produces $\frac{0}{0}$ or $\frac{\pm\infty}{\pm\infty}$ (indeterminate), then:<br><br>$\lim_{x\to c}\frac{f(x)}{g(x)}=\lim_{x\to c}\frac{f'(x)}{g'(x)}$<br><br>(provided the right-hand limit exists or is $\pm\infty$)<br><br>Can reapply repeatedly if the new limit is still indeterminate; check the indeterminate form *before* every application |

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 4: Contextual Applications — Core Definitions</h3>
</div>

| | |
|---|---|
| **4.1**<br>Interpreting the Derivative in Context | **Derivative in Context:**<br>*Definition:* the value $f'(a)$ represents how quickly a real-world quantity modeled by $f$ is changing at the specific input $a$.<br>*Graphical Meaning:* the slope of the curve $y=f(x)$ at the point where $x=a$, showing whether and how fast the modeled quantity is rising or falling at that instant. |
| **4.2**<br>Straight-Line Motion | **Velocity:**<br>*Definition:* the instantaneous rate of change of position with respect to time; a signed quantity indicating direction of motion.<br>*Graphical Meaning:* the slope of the position graph $s(t)$ at a given time.<br><br>**Acceleration:**<br>*Definition:* the instantaneous rate of change of velocity with respect to time.<br>*Graphical Meaning:* the slope of the velocity graph $v(t)$; its sign relative to $v(t)$'s sign determines whether the object is speeding up or slowing down. |
| **4.3**<br>Rates of Change in Other Contexts | **Applied Rate of Change:**<br>*Definition:* the derivative of a non-motion quantity (volume, population, temperature, revenue, etc.) with respect to another variable, usually time.<br>*Graphical Meaning:* the slope of that quantity's graph at a given input, interpreted using the same units-based sentence structure as any other derivative. |
| **4.4–4.5**<br>Related Rates | **Related Rates:**<br>*Definition:* a problem type in which two or more quantities, each a function of time, are linked by an equation; differentiating that equation implicitly relates their rates of change.<br>*Graphical Meaning:* as one quantity's value changes along its own path over time, a geometric or physical constraint forces the linked quantity to change in a corresponding, calculable way. |
| **4.6**<br>Local Linearity & Linearization | **Local Linearity:**<br>*Definition:* the property that a differentiable function, when viewed at a sufficiently small scale near a point, appears indistinguishable from its tangent line.<br>*Graphical Meaning:* zooming in on a smooth curve at a point makes the curve look straight, matching the tangent line's slope.<br><br>**Linearization:**<br>*Definition:* the tangent-line function $L(x)$ used to approximate $f(x)$ for $x$ near the point of tangency.<br>*Graphical Meaning:* the tangent line itself, used as a stand-in for the curve close to $a$; accuracy decreases as $x$ moves farther from $a$. |
| **4.7**<br>L'Hopital's Rule | **Indeterminate Form:**<br>*Definition:* a limit expression such as $\frac{0}{0}$ or $\frac{\infty}{\infty}$ that does not by itself determine the limit's value.<br><br>**L'Hopital's Rule:**<br>*Definition:* a theorem stating that for indeterminate quotient limits, the limit of the ratio of two functions equals the limit of the ratio of their derivatives, provided that latter limit exists.<br>*Graphical Meaning:* near the point of indeterminacy, both functions' instantaneous rates of change govern the limiting behavior of their ratio more reliably than their raw (0 or $\infty$) values. |
""",
        5: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 5: Analytical Applications — Quick Reference</h3>
</div>

| | |
|---|---|
| **5.1**<br>Mean Value Theorem | If $f$ is continuous on $[a,b]$ and differentiable on $(a,b)$, there exists $c\in(a,b)$ such that:<br><br>$f'(c)=\frac{f(b)-f(a)}{b-a}$<br><br>(instantaneous rate $=$ average rate somewhere on the interval) |
| **5.2**<br>EVT, Extrema & Critical Points | **Critical Point:** $f'(c)=0$ *or* $f'(c)$ does not exist (and $c$ in domain of $f$)<br><br>**EVT:** if $f$ continuous on $[a,b]$, $f$ attains an absolute max *and* absolute min on $[a,b]$<br><br>Local extrema occur only at critical points; global extrema occur at critical points or endpoints |
| **5.3**<br>Increasing/Decreasing Intervals | $f'(x)>0$ on an interval $\implies f$ increasing<br>$f'(x)<0$ on an interval $\implies f$ decreasing<br><br>**Procedure:** find critical points, test sign of $f'$ in each resulting subinterval |
| **5.4**<br>First Derivative Test | At critical point $c$:<br>• $f'$ changes $+\to-$: local **max** at $c$<br>• $f'$ changes $-\to+$: local **min** at $c$<br>• $f'$ does not change sign: no extremum at $c$ |
| **5.5**<br>Candidates Test (Global Extrema) | On closed $[a,b]$:<br>• **1.** Find all critical points in $(a,b)$<br>• **2.** Evaluate $f$ at each critical point *and* at $x=a,\,x=b$<br>• **3.** Largest value $=$ absolute max; smallest $=$ absolute min |
| **5.6**<br>Concavity | $f''(x)>0$ on an interval $\implies$ concave up ($\cup$), $f'$ increasing<br>$f''(x)<0$ on an interval $\implies$ concave down ($\cap$), $f'$ decreasing<br><br>**Inflection Point:** $f''(p)=0$ or undefined *and* concavity changes sign at $p$ |
| **5.7**<br>Second Derivative Test | At critical point $c$ where $f'(c)=0$:<br>$f''(c)<0$: local **max** &nbsp;&nbsp;\|&nbsp;&nbsp; $f''(c)>0$: local **min**<br>$f''(c)=0$: test is **inconclusive** $\implies$ use First Derivative Test |
| **5.8–5.9**<br>Sketching & Connecting $f,f',f''$ | **Sign $\implies$ On $f$ $\implies$ On graph**<br>• $f'>0 \implies$ increasing $\implies$ rising<br>• $f'<0 \implies$ decreasing $\implies$ falling<br>• $f''>0 \implies$ concave up $\implies \cup$ shape<br>• $f''<0 \implies$ concave down $\implies \cap$ shape<br><br>**Particle motion link:** speeding up when $v,a$ same sign; slowing down when opposite signs (revisit of 4.2) |
| **5.10–5.11**<br>Optimization | **1.** Identify quantity to optimize; write objective function<br>**2.** Write constraint equation; solve for one variable, substitute in<br>**3.** Differentiate objective (now single-variable); set $=0$<br>**4.** Solve, classify (1st/2nd Deriv. Test or Candidates Test), state answer with units |
| **5.12**<br>Implicit Relations | Analyze extrema/concavity of implicitly defined curves:<br><br>• **Horizontal tangent:** $\frac{dy}{dx}=0$ (set numerator $=0$, denominator $\neq 0$)<br>• **Vertical tangent:** $\frac{dy}{dx}$ undefined (denominator $=0$, numerator $\neq 0$)<br><br>Find $\frac{d^2y}{dx^2}$ implicitly to test concavity, substituting known $\frac{dy}{dx}$ |

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 5: Analytical Applications — Core Definitions</h3>
</div>

| | |
|---|---|
| **5.1**<br>Mean Value Theorem | **Mean Value Theorem (MVT):**<br>*Definition:* guarantees that for a function continuous on $[a,b]$ and differentiable on $(a,b)$, at least one point exists where the instantaneous rate of change equals the average rate of change over the interval.<br>*Graphical Meaning:* there is a point where the tangent line is parallel to the secant line connecting $(a,f(a))$ and $(b,f(b))$. |
| **5.2**<br>EVT, Extrema & Critical Points | **Extreme Value Theorem (EVT):**<br>*Definition:* guarantees a continuous function on a closed interval $[a,b]$ attains both an absolute maximum and an absolute minimum value on that interval.<br><br>**Critical Point:**<br>*Definition:* a point $c$ in the domain of $f$ where $f'(c)=0$ or $f'(c)$ fails to exist.<br>*Graphical Meaning:* a location where the tangent line is horizontal, undefined (vertical tangent), or the curve has a sharp corner/cusp — the only candidates for local extrema. |
| **5.4**<br>First Derivative Test | **First Derivative Test:**<br>*Definition:* a method for classifying a critical point as a local max, local min, or neither, based on whether $f'$ changes sign around that point.<br>*Graphical Meaning:* the curve switches from rising to falling (a peak) or falling to rising (a valley) at the critical point. |
| **5.5**<br>Candidates Test | **Candidates Test:**<br>*Definition:* a procedure for finding absolute (global) extrema on a closed interval by comparing the function's value at every critical point with its value at both endpoints.<br>*Graphical Meaning:* the highest and lowest points on the entire graph over $[a,b]$ must occur either where the curve levels off/breaks or at the far edges of the interval. |
| **5.6–5.7**<br>Concavity & Second Derivative Test | **Concavity:**<br>*Definition:* describes whether a function's rate of change ($f'$) is itself increasing or decreasing.<br>*Graphical Meaning:* concave up curves bend upward like a cup; concave down curves bend downward like a frown.<br><br>**Second Derivative Test:**<br>*Definition:* an alternative method for classifying a critical point using the sign of $f''$ at that point rather than a sign chart of $f'$.<br>*Graphical Meaning:* local concavity (cup shape $\implies$ min; frown shape $\implies$ max) at a level point determines the type of extremum. |
| **5.8–5.9**<br>Sketching & Connecting $f,f',f''$ | **Graphical Connection:**<br>*Definition:* the relationship linking a function and its derivatives such that features of $f$ (extrema, inflection points) correspond to specific behaviors of $f'$ and $f''$ (zeros, sign changes).<br>*Graphical Meaning:* zeros of $f'$ align with peaks/valleys of $f$; zeros of $f''$ (with a sign change) align with inflection points of $f$ and extrema of $f'$. |
| **5.10–5.11**<br>Optimization | **Optimization Problem:**<br>*Definition:* a real-world scenario asking for the maximum or minimum possible value of some quantity, subject to a stated constraint.<br>*Graphical Meaning:* equivalent to finding the highest or lowest point on the graph of the objective function once it has been reduced to a single variable. |
| **5.12**<br>Implicit Relations | **Behavior of Implicit Relations:**<br>*Definition:* the study of extrema, concavity, and tangent behavior of curves defined by equations relating $x$ and $y$ that are not solved explicitly for $y$.<br>*Graphical Meaning:* horizontal/vertical tangents and concavity can still be identified and located on the curve, even though the curve is not a function of $x$ over its full domain. |
""",
        6: "### Unit 6: Integration & Accumulation\n- Power Rule for Integration: $\\int x^n dx = \\frac{x^{n+1}}{n+1} + C$\n- Fundamental Theorem of Calculus: $\\int_a^b f(x)dx = F(b) - F(a)$",
        7: "### Unit 7: Differential Equations\n- Separation of Variables: Separate $x$ and $y$ variables on opposite sides.\n- Exponential Growth/Decay: $\\frac{dy}{dt} = ky \\implies y = Ce^{kt}$",
        8: "### Unit 8: Applications of Integration\n- Area Between Curves: $\\int_a^b [f(x) - g(x)] dx$\n- Volume (Disk/Washer): $V = \\pi \\int_a^b [R(x)]^2 dx$",
        9: "### Unit 9: Parametric, Polar & Vectors\n- Parametric Derivative: $\\frac{dy}{dx} = \\frac{dy/dt}{dx/dt}$\n- Polar Area: $A = \\frac{1}{2} \\int_a^b [r(\\theta)]^2 d\\theta$",
        10: "### Unit 10: Infinite Sequences & Series\n- Geometric Series: $\\sum ar^n = \\frac{a}{1-r}$ (|r| < 1)\n- Nth Term Test: If $\\lim a_n \\neq 0$, the series diverges."
    }
    
    st.markdown(cheat_sheets.get(unit_num, "*Add your custom formulas for this unit here!*"), unsafe_allow_html=True)

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