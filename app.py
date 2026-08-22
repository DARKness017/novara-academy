import streamlit as st
import pandas as pd
import numpy as np
import time
import bcrypt
import matplotlib.pyplot as plt
from supabase import create_client
import random
from datetime import date, timedelta, datetime
import streamlit.components.v1 as components
import re
from zoneinfo import ZoneInfo

# --- 1. Page Config & Theming ---
st.set_page_config(page_title="Novara Academy - Adaptive Engine", page_icon="🎓", layout="centered")

# --- Custom CSS Styling ---
st.markdown("""
    <style>
    /* --- 0. IMPORT PREMIUM FONT & ICONS --- */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
    }

    /* --- 1. AMBIENT SAAS CANVAS (Removes the flat white void) --- */
    .stApp {
        background-color: #F8FAFC !important;
        background-image: 
            radial-gradient(at 0% 0%, rgba(11, 27, 61, 0.03) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(192, 155, 90, 0.05) 0px, transparent 50%) !important;
        background-attachment: fixed !important;
    }

    /* --- 2. REMOVE STREAMLIT CHROME --- */
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
        padding-bottom: 2rem !important;
        max-width: 900px !important;
    }

    /* --- 3. METRIC CARDS & DATA WRAPPERS --- */
    div[data-testid="stMetric"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        box-shadow: 0 4px 12px rgba(11, 27, 61, 0.04) !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 20px rgba(11, 27, 61, 0.08) !important;
        border-color: #C09B5A !important;
    }

    /* --- 4. NOVARA ACADEMY ANIMATED BUTTONS --- */
    .stButton > button, [data-testid="stFormSubmitButton"] > button {
        background-color: #0B1B3D !important;
        color: white !important;
        border-radius: 10px !important;
        border: 1px solid rgba(192, 155, 90, 0.6) !important;
        font-weight: 600;
        letter-spacing: 0.2px;
        padding: 10px 20px !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        box-shadow: 0 4px 10px rgba(11, 27, 61, 0.12) !important;
    }
    .stButton > button:hover, [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #C09B5A !important;
        color: #0B1B3D !important;
        border: 1px solid #0B1B3D !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 18px rgba(192, 155, 90, 0.35) !important;
    }
    .stButton > button:active, [data-testid="stFormSubmitButton"] > button:active {
        transform: translateY(1px) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    .stButton > button[kind="primary"], [data-testid="stFormSubmitButton"] > button[kind="primary"] {
        background: linear-gradient(135deg, #C09B5A 0%, #B08B4A 100%) !important;
        color: #0B1B3D !important;
        border-radius: 10px !important;
        border: 1px solid #0B1B3D !important;
        font-weight: 700;
    }
    .stButton > button[kind="primary"]:hover, [data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
        background: #0B1B3D !important;
        color: #FFFFFF !important;
        border: 1px solid #C09B5A !important; 
        box-shadow: 0 8px 18px rgba(11, 27, 61, 0.25) !important;
    }

    /* --- 5. CUSTOM GOLD PROGRESS BAR --- */
    [data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, #0B1B3D 0%, #C09B5A 100%) !important;
        border-radius: 8px !important;
    }
    [data-testid="stProgress"] > div > div {
        background-color: #E2E8F0 !important;
        border-radius: 8px !important;
    }

    /* --- 6. NATIVE MARKDOWN TABLE STYLING --- */
    .stMarkdown table {
        background-color: #0B1B3D !important;
        border: 2px solid #C09B5A !important;
        border-top: none !important;
        border-bottom-left-radius: 14px !important;
        border-bottom-right-radius: 14px !important;
        color: white !important;
        width: 100% !important;
        margin-top: -10px !important;
        box-shadow: 0 10px 25px rgba(11, 27, 61, 0.2) !important;
        border-collapse: separate !important;
        border-spacing: 0 !important;
    }
    .stMarkdown th { display: none !important; }
    .stMarkdown td {
        border-bottom: 1px solid rgba(192, 155, 90, 0.4) !important;
        border-top: none !important;
        border-right: none !important;
        border-left: none !important;
        padding: 16px !important;
        vertical-align: top !important;
        font-size: 14px !important;
    }
    .stMarkdown tr:last-child td { border-bottom: none !important; }
    /* Fixes the corner bleeding bug */
    .stMarkdown tr:last-child td:first-child { border-bottom-left-radius: 12px !important; }
    .stMarkdown tr:last-child td:last-child { border-bottom-right-radius: 12px !important; }
    .stMarkdown td:first-child {
        color: #C09B5A !important;
        font-weight: bold !important;
        width: 28% !important;
    }

    /* --- 7. SAAS SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #0B1B3D !important;
        border-right: 1.5px solid #C09B5A !important;
        box-shadow: 4px 0 20px rgba(0,0,0,0.15) !important;
    }
    [data-testid="stSidebar"] hr {
        border-bottom: 1px solid rgba(192, 155, 90, 0.3) !important;
    }

    /* --- 8. EXPANDER / ACCORDION CARDS --- */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E8F0 !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
        margin-bottom: 12px !important;
    }

    /* --- 9. PREMIUM QUIZ OPTION CARDS --- */
    div[role="radiogroup"] {
        gap: 14px !important; 
    }
    div[role="radiogroup"] > label {
        background-color: #FFFFFF !important;
        border: 1.5px solid #E2E8F0 !important; 
        border-radius: 12px !important;
        padding: 16px 22px !important; 
        box-shadow: 0 4px 8px rgba(11, 27, 61, 0.03) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
        width: 100% !important;
        display: flex !important;
        align-items: center !important;
    }
    div[role="radiogroup"] > label:hover {
        border: 1.5px solid #C09B5A !important; 
        background-color: #FAF8F5 !important; 
        transform: translateY(-3px) !important; 
        box-shadow: 0 10px 20px rgba(192, 155, 90, 0.18) !important; 
    }

    /* --- 10. HIDE STREAMLIT HEADER ANCHOR LINKS --- */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a {
        display: none !important;
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

# --- GLOBAL CONSTANTS (Performance Optimization) ---
# Moving this outside the function stops it from rebuilding 360 lines of text on every click!
CHEAT_SHEETS = {
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
""",
    6: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 6: Integration & Accumulation — Quick Reference</h3>
</div>

| | |
|---|---|
| **6.1**<br>Accumulation of Change | **Total Change from a Rate:** $\int_a^b f'(x)\,dx=f(b)-f(a)$<br><br>**Signed Area Rules:** region above $x$-axis $\implies$ positive accumulation; region below $\implies$ negative accumulation; net accumulation $=$ signed area between curve and $x$-axis |
| **6.2**<br>Riemann Sums | Subinterval width: $\Delta x=\frac{b-a}{n}$<br><br>**Left (LRS):** $L_n=\sum_{k=0}^{n-1}f(x_k)\Delta x,\ x_k=a+k\Delta x$ — incr. $f$: underestimate; decr. $f$: overestimate<br><br>**Right (RRS):** $R_n=\sum_{k=1}^{n}f(x_k)\Delta x$ — incr. $f$: overestimate; decr. $f$: underestimate<br><br>**Midpoint (MRS):** $M_n=\sum_{k=1}^{n}f\left(\frac{x_{k-1}+x_k}{2}\right)\Delta x$<br><br>**Trapezoidal:** $T_n=\frac{\Delta x}{2}\big[y_0+2y_1+\dots+2y_{n-1}+y_n\big]$ |
| **6.3**<br>Riemann Sums & Definite Integral Notation | **General Riemann Sum:** $\sum_{k=1}^{n}f(x_k^*)\Delta x,\ x_k^*\in[x_{k-1},x_k]$<br><br>**Sigma Identities:** $\sum_{k=1}^{n}1=n$,&nbsp;&nbsp; $\sum_{k=1}^{n}k=\frac{n(n+1)}{2}$,&nbsp;&nbsp; $\sum_{k=1}^{n}k^2=\frac{n(n+1)(2n+1)}{6}$<br><br>**Definite Integral as a Limit:** $\int_a^b f(x)\,dx=\lim_{n\to\infty}\sum_{k=1}^{n}f(x_k^*)\Delta x$ |
| **Properties of Definite Integrals** | $\int_a^a f\,dx=0$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\int_a^b f\,dx=-\int_b^a f\,dx$<br><br>$\int_a^b cf\,dx=c\int_a^b f\,dx$<br><br>$\int_a^b[f\pm g]\,dx=\int_a^b f\,dx\pm\int_a^b g\,dx$<br><br>$\int_a^b f\,dx=\int_a^c f\,dx+\int_c^b f\,dx$ |
| **6.4**<br>FTC & Accumulation Functions | **FTC Part 1:** $F(x)=\int_a^x f(t)\,dt \implies F'(x)=f(x)$<br><br>**Chain Rule extension:** $\frac{d}{dx}\int_a^{g(x)} f(t)\,dt=f(g(x))\cdot g'(x)$<br><br>**FTC Part 2:** $\int_a^b f(x)\,dx=F(b)-F(a)=\big[F(x)\big]_a^b$ |
| **6.5**<br>Behavior of Accumulation Functions | Let $F(x)=\int_a^x f(t)\,dt$:<br><br>• $F'(x)=f(x)$ — slope of $F$ equals value of $f$<br>• $F$ increasing $\iff f(x)>0$ ;&nbsp;&nbsp; $F$ decreasing $\iff f(x)<0$<br>• Local max/min of $F$ where $f$ changes sign<br>• $F$ concave up $\iff f$ increasing ;&nbsp;&nbsp; concave down $\iff f$ decreasing<br>• Inflection point of $F$ where $f$ has local max/min |
| **6.6**<br>Properties of Definite Integrals | **Comparison:** if $f(x)\geq g(x)$ on $[a,b]$, then $\int_a^b f\,dx\geq\int_a^b g\,dx$<br><br>**Bound:** if $m\leq f(x)\leq M$ on $[a,b]$: $m(b-a)\leq\int_a^b f(x)\,dx\leq M(b-a)$<br><br>**Average Value:** $f_{\text{avg}}=\frac{1}{b-a}\int_a^b f(x)\,dx$<br><br>**MVT for Integrals:** $\exists\,c\in(a,b)$ such that $f(c)=\frac{1}{b-a}\int_a^b f(x)\,dx$ |
| **6.7**<br>FTC & Definite Integrals (Net Change) | **Net Change Theorem:** $\int_a^b F'(x)\,dx=F(b)-F(a)$<br><br>**Displacement:** $\int_a^b v(t)\,dt$ &nbsp;&nbsp;\|&nbsp;&nbsp; **Distance:** $\int_a^b \lvert v(t) \rvert\,dt$ |
| **6.8**<br>Basic Antiderivatives | **Power Rule:** $\int x^n\,dx=\frac{x^{n+1}}{n+1}+C,\ n\neq-1$<br><br>$\int cf(x)\,dx=c\int f(x)\,dx$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\int[f\pm g]\,dx=\int f\,dx\pm\int g\,dx$<br><br>**Common Integrals:**<br>• $\int e^x\,dx = e^x+C$<br>• $\int \frac{1}{x}\,dx = \ln\lvert x \rvert+C$<br>• $\int \sin x\,dx = -\cos x+C$<br>• $\int \cos x\,dx = \sin x+C$<br>• $\int \sec^2 x\,dx = \tan x+C$<br>• $\int \sec x\tan x\,dx = \sec x+C$<br>• $\int \frac{1}{\sqrt{1-x^2}}\,dx = \arcsin x+C$<br>• $\int \frac{1}{1+x^2}\,dx = \arctan x+C$ |
| **6.9**<br>Substitution ($u$-sub) | **Procedure:**<br>**1.** choose $u=g(x)$, compute $du=g'(x)\,dx$<br>**2.** rewrite integral entirely in $u$<br>**3.** integrate $\int f(u)\,du$; substitute back<br><br>**Definite integral (change limits):** $\int_a^b f(g(x))g'(x)\,dx=\int_{g(a)}^{g(b)} f(u)\,du$ |
| **6.10**<br>Long Division & Completing the Square | **Long Division:** used when degree of numerator $\geq$ degree of denominator: $\int\frac{P(x)}{q(x)}\,dx \implies \int\left[\text{quotient}+\frac{\text{remainder}}{q(x)}\right]dx$<br><br>**Completing the Square:** for $\frac{1}{ax^2+bx+c}$, rewrite denominator as $(x-h)^2+k^2$, then use $\int\frac{1}{u^2+a^2}\,du=\frac{1}{a}\arctan\left(\frac{u}{a}\right)+C$ |
| **6.11 (BC)**<br>Integration by Parts | $\int u\,dv=uv-\int v\,du$<br><br>**LIATE** priority for choosing $u$: **L**ogarithmic, **I**nverse trig, **A**lgebraic, **T**rigonometric, **E**xponential |
| **6.12 (BC)**<br>Linear Partial Fractions | For $\frac{P(x)}{(ax+b)(cx+d)}$, decompose: $\frac{P(x)}{(ax+b)(cx+d)}=\frac{A}{ax+b}+\frac{B}{cx+d}$<br><br>then integrate each term using $\int\frac{1}{ax+b}\,dx=\frac{1}{a}\ln\lvert ax+b \rvert+C$ |
| **6.13 (BC)**<br>Improper Integrals | **Infinite bounds:** $\int_a^{\infty} f(x)\,dx=\lim_{t\to\infty}\int_a^t f(x)\,dx$<br><br>**Converges:** limit exists, finite &nbsp;&nbsp;\|&nbsp;&nbsp; **Diverges:** limit is $\pm\infty$ or DNE<br><br>**Discontinuous integrand** at $c\in[a,b]$: $\int_a^b f\,dx=\lim_{t\to c^{-}}\int_a^t f\,dx+\lim_{t\to c^{+}}\int_t^b f\,dx$ |
| **6.14**<br>Selecting Techniques | • $\int x^n\,dx \implies$ Power Rule<br>• $\int f(g(x))g'(x)\,dx \implies u$-Substitution<br>• $\int u\,dv$ form $\implies$ Integration by Parts<br>• Rational, deg. num $\geq$ deg. den. $\implies$ Long Division<br>• $\frac{1}{ax^2+bx+c}$, no roots $\implies$ Complete the Square<br>• $\frac{P(x)}{(ax+b)(cx+d)} \implies$ Partial Fractions<br>• Infinite bound/discontinuity $\implies$ Improper Integral |
""",
    7: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 7: Differential Equations — Quick Reference</h3>
</div>

| | |
|---|---|
| **7.1**<br>Modeling with Differential Equations | **Differential Equation (DE):** an equation relating a function to one or more of its derivatives: $\frac{dy}{dx}=f(x,y)$<br><br>**Common Model Forms:**<br>• Rate proportional to quantity: $\frac{dy}{dt}=ky$<br>• Rate proportional to difference: $\frac{dy}{dt}=k(y-a)$<br>• General rate of change: $\frac{dy}{dx}=f(x)$ or $g(y)$<br><br>**Reading DEs from Context:** "$y$ grows at a rate proportional to itself" $\implies \frac{dy}{dt}=ky$ ;&nbsp;&nbsp; "$y$ decreases at a rate proportional to the square of $y$" $\implies \frac{dy}{dt}=-ky^2$ |
| **7.2**<br>Verifying Solutions | **Verification Procedure:**<br>• **1.** Differentiate the proposed solution $y=f(x)$ to find $\frac{dy}{dx}$<br>• **2.** Substitute $y$ and $\frac{dy}{dx}$ into the DE<br>• **3.** Confirm both sides are equal $\implies$ solution is verified<br><br>**Checking Initial Conditions:** if given $y(x_0)=y_0$, substitute $x=x_0$ into $y$ and confirm $y=y_0$<br><br>**Example:** given $\frac{dy}{dx}=2y$ and $y=Ce^{2x}$: $\frac{dy}{dx}=2Ce^{2x}=2y$ $\checkmark$ |
| **7.3**<br>Sketching Slope Fields | A slope field (direction field) is a grid of short segments where each segment at $(x,y)$ has slope equal to $\frac{dy}{dx}$ evaluated at that point<br><br>**Steps to Sketch:**<br>• **1.** Evaluate $\frac{dy}{dx}$ at each grid point $(x,y)$<br>• **2.** Draw a short segment with that slope at each point<br>• **3.** Identify horizontal segments where $\frac{dy}{dx}=0$<br>• **4.** Identify vertical segments (undefined slope) where applicable<br><br>**Key Observations:** if DE depends only on $x$: slopes constant along vertical lines; if DE depends only on $y$: slopes constant along horizontal lines; isoclines: curves where $\frac{dy}{dx}=c$ (constant) |
| **7.4**<br>Reasoning Using Slope Fields | **Reading Solution Curves:** solution curves flow tangent to slope-field segments; different initial conditions produce different solution curves<br><br>Equilibrium solutions are horizontal lines where $\frac{dy}{dx}=0$ everywhere<br><br>**Stable vs. Unstable Equilibria:** **Stable:** nearby solutions converge toward equilibrium; **Unstable:** nearby solutions diverge away from equilibrium<br><br>**Matching DEs to Slope Fields:** look for sign of slopes in quadrants, behavior as $y\to 0$, whether slopes depend on $x$, $y$, or both |
| **7.5 (BC)**<br>Euler's Method | **Purpose:** numerically approximates a solution to $\frac{dy}{dx}=F(x,y)$ given an initial condition $(x_0,y_0)$<br><br>**Iteration Formula:** $x_{n+1}=x_n+\Delta x$,&nbsp;&nbsp; $y_{n+1}=y_n+F(x_n,y_n)\cdot\Delta x$<br><br>**Iteration Step-by-Step:**<br>• Start at $(x_0, y_0)$<br>• Compute slope: $F(x_0, y_0)$<br>• Find change in $y$: $\Delta y = F(x_0, y_0) \cdot \Delta x$<br>• Next point: $(x_1, y_1) = (x_0 + \Delta x, y_0 + \Delta y)$<br>• Repeat process<br><br>**Notes:** smaller $\Delta x \implies$ more accurate approximation; concave up curve $\implies$ Euler underestimates; concave down curve $\implies$ Euler overestimates |
| **7.6**<br>Separation of Variables | **When to Use:** the DE can be written as $\frac{dy}{dx}=g(x)\cdot h(y)$, i.e., variables are separable<br><br>**Procedure:**<br>• **1.** Separate: $\frac{dy}{h(y)}=g(x)\,dx$<br>• **2.** Integrate both sides: $\int\frac{1}{h(y)}\,dy=\int g(x)\,dx$<br>• **3.** Solve for $y$ (if possible); include $+C$<br>• **4.** Result is the general solution<br><br>**Key Detail:** always check for constant solutions where $h(y)=0$ — these may be lost in division |
| **7.7**<br>Particular Solutions | **From General to Particular:**<br>• **1.** Solve the DE by separation of variables to get general solution with $C$<br>• **2.** Substitute the initial condition $(x_0,y_0)$ into the general solution<br>• **3.** Solve for $C$<br>• **4.** Write the particular solution with the found value of $C$<br><br>**Form:** General: $y=f(x)+C \implies$ Particular: $y=f(x)+C_0$<br><br>**Important:** the particular solution satisfies *both* the DE and the initial condition |
| **7.8**<br>Exponential Models | **Exponential Growth/Decay DE:** $\frac{dy}{dt}=ky$ &nbsp;&nbsp;\|&nbsp;&nbsp; **Solution:** $y(t)=y_0e^{kt}$<br><br>where $y_0=y(0)$ is the initial value and $k$ is the growth/decay constant<br>$k>0$: **exponential growth** &nbsp;&nbsp;\|&nbsp;&nbsp; $k<0$: **exponential decay**<br><br>**Doubling Time/Half-Life:** $t_{\text{double}}=\frac{\ln 2}{k}$ &nbsp;&nbsp;\|&nbsp;&nbsp; $t_{1/2}=\frac{\ln 2}{\lvert k \rvert}$<br><br>**Newton's Law of Cooling:** $\frac{dT}{dt}=k(T-T_a)$,&nbsp;&nbsp; solution: $T(t)=T_a+(T_0-T_a)e^{kt}$<br>where $T_a=$ ambient temp., $T_0=$ initial temp. |
| **7.9 (BC)**<br>Logistic Models | **Logistic DE:** $\frac{dP}{dt}=kP\left(1-\frac{P}{L}\right)$, where $L=$ carrying capacity, $k=$ growth constant<br><br>**Logistic Solution:** $P(t)=\frac{L}{1+Ae^{-kt}}$,&nbsp;&nbsp; $A=\frac{L-P_0}{P_0}$<br><br>**Key Properties:** $P\to L$ as $t\to\infty$ (upper bound); $P\to 0$ as $t\to-\infty$ (lower bound); fastest growth (inflection point) at $P=\frac{L}{2}$; $\frac{dP}{dt}$ is maximized when $P=\frac{L}{2}$; $\frac{d^2P}{dt^2}=0$ at inflection point $P=\frac{L}{2}$<br><br>**Second Derivative/Concavity:** $\frac{d^2P}{dt^2}=k^2P\left(1-\frac{P}{L}\right)\left(1-\frac{2P}{L}\right)$<br><br>Concave up when $P<\frac{L}{2}$ ;&nbsp;&nbsp; Concave down when $P>\frac{L}{2}$ |
""",
    8: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 8: Applications of Integration — Quick Reference</h3>
</div>

| | |
|---|---|
| **8.1**<br>Average Value & MVT for Integrals | **Average Value:** $f_{\text{avg}}=\frac{1}{b-a}\int_a^b f(x)\,dx$<br><br>**Mean Value Theorem for Integrals:** $\exists\,c\in(a,b)$ such that $f(c)=\frac{1}{b-a}\int_a^b f(x)\,dx$ (i.e., $f$ actually attains its average value at some point $c$) |
| **8.2**<br>Position, Velocity, Acceleration | **Relationships:** $v(t)=\int a(t)\,dt+C$ &nbsp;&nbsp;\|&nbsp;&nbsp; $s(t)=\int v(t)\,dt+C$<br><br>**Displacement:** $\int_a^b v(t)\,dt$ &nbsp;&nbsp;\|&nbsp;&nbsp; **Distance Traveled:** $\int_a^b \lvert v(t) \rvert\,dt$<br><br>**Position from Displacement:** $s(t)=s(t_0)+\int_{t_0}^{t} v(\tau)\,d\tau$<br><br>**Speed** $=\lvert v(t) \rvert$. Object speeds up when $v$ and $a$ have the *same* sign; slows down when *opposite* signs |
| **8.3**<br>Accumulation Functions | **Net Change from Rate:** $\text{Net Change}=\int_a^b R(t)\,dt$, where $R(t)$ is a rate function (gallons/min, people/hr, etc.)<br><br>**Total Amount at Time $t$:** $Q(t)=Q(t_0)+\int_{t_0}^{t} R(\tau)\,d\tau$<br><br>**Interpreting the Integral:** units of integral $=$ units of $R(t)\times$ units of $t$; positive rate $\implies$ quantity increasing; negative rate $\implies$ quantity decreasing; net vs. total: net includes sign, total uses $\lvert R(t) \rvert$ |
| **8.4**<br>Area Between Curves (w.r.t. $x$) | **Formula:** $A=\int_a^b \big[f(x)-g(x)\big]\,dx$, where $f(x)\geq g(x)$ on $[a,b]$ (**top minus bottom**)<br><br>**Finding Intersection Points:** set $f(x)=g(x)$ and solve for $x$ to determine limits $a$ and $b$<br><br>**Tips:** always sketch to identify which curve is on top; result is always $\geq 0$ |
| **8.5**<br>Area Between Curves (w.r.t. $y$) | **Formula:** $A=\int_c^d \big[R(y)-L(y)\big]\,dy$, where $R(y)$ is the right curve and $L(y)$ is the left curve, integrated from $y=c$ to $y=d$<br><br>**When to Use:** curves more naturally expressed as $x=f(y)$, or when integrating w.r.t. $x$ would require splitting the region |
| **8.6**<br>Area Between Curves — More Than Two Intersections | **Strategy:**<br>• **1.** Find all intersection points of $f$ and $g$<br>• **2.** On each subinterval, determine which function is on top<br>• **3.** Integrate separately on each subinterval and sum:<br>$A=\int_a^c [f-g]\,dx+\int_c^e [g-f]\,dx+\dots$<br><br>**Alternative (Absolute Value):** $A=\int_a^b \lvert f(x)-g(x) \rvert\,dx$ |
| **8.7**<br>Volumes: Cross Sections — Squares & Rectangles | **General Cross-Section Formula:** $V=\int_a^b A(x)\,dx$, where $A(x)$ is the area of a cross-sectional slice perpendicular to the $x$-axis<br><br>**Square Cross Sections** (side $=f(x)-g(x)$): $A(x)=[f(x)-g(x)]^2 \implies V=\int_a^b [f(x)-g(x)]^2\,dx$<br><br>**Rectangle Cross Sections** (height $h$ given): $A(x)=[f(x)-g(x)]\cdot h \implies V=\int_a^b [f(x)-g(x)]\cdot h\,dx$ |
| **8.8**<br>Volumes: Cross Sections — Triangles & Semicircles | **Equilateral Triangle** (side $s=f(x)-g(x)$): $A(x)=\frac{\sqrt{3}}{4}s^2 \implies V=\int_a^b \frac{\sqrt{3}}{4}[f(x)-g(x)]^2\,dx$<br><br>**Right Isosceles Triangle:** leg $=s$, hyp. on base: $A=\frac{1}{2}s^2$ &nbsp;&nbsp;\|&nbsp;&nbsp; leg on base: $A=\frac{1}{4}s^2$<br><br>**Semicircle** (diameter $=f(x)-g(x)$, radius $r=\frac{s}{2}$): $A(x)=\frac{\pi}{2}r^2=\frac{\pi}{8}[f(x)-g(x)]^2 \implies V=\int_a^b \frac{\pi}{8}[f(x)-g(x)]^2\,dx$ |
| **8.9**<br>Disc Method: $x$- or $y$-Axis | **Around $x$-axis:** $V=\pi\int_a^b [f(x)]^2\,dx$<br><br>**Around $y$-axis:** $V=\pi\int_c^d [g(y)]^2\,dy$<br><br>**Key Idea:** each disc has radius $=f(x)$ (distance from axis to curve) and thickness $dx$ (or $dy$); area of disc $=\pi r^2$ |
| **8.10**<br>Disc Method: Other Axes | **Around Horizontal Line $y=k$:** radius $=\lvert f(x)-k \rvert$: $V=\pi\int_a^b [f(x)-k]^2\,dx$<br><br>**Around Vertical Line $x=k$:** radius $=\lvert g(y)-k \rvert$: $V=\pi\int_c^d [g(y)-k]^2\,dy$<br><br>**Sign of Radius:** the radius is always a positive distance; squaring removes sign issues, but correctly identifying top/bottom or left/right relative to the axis of revolution is essential |
| **8.11**<br>Washer Method: $x$- or $y$-Axis | **Around $x$-axis:** outer radius $R(x)=f(x)$, inner radius $r(x)=g(x)$, $f\geq g\geq 0$: $V=\pi\int_a^b \big([R(x)]^2-[r(x)]^2\big)\,dx$<br><br>**Around $y$-axis:** $V=\pi\int_c^d \big([R(y)]^2-[r(y)]^2\big)\,dy$<br><br>**Key Idea:** washer $=$ large disc $-$ small disc. Use when the solid has a hole (two curves, neither touching the axis) |
| **8.12**<br>Washer Method: Other Axes | **Around $y=k$ (horizontal):** $R(x)=$ farther curve from $y=k$, $r(x)=$ closer curve: $V=\pi\int_a^b \big(R(x)^2-r(x)^2\big)\,dx$<br><br>**Around $x=k$ (vertical):** $V=\pi\int_c^d \big(R(y)^2-r(y)^2\big)\,dy$<br><br>**Radius Rules:** axis below region: $R=f(x)-k,\ r=g(x)-k$; axis above region: $R=k-g(x),\ r=k-f(x)$; always $R>r>0$ |
| **8.13 (BC)**<br>Arc Length & Distance Traveled | **Arc Length, $y=f(x)$:** $L=\int_a^b \sqrt{1+[f'(x)]^2}\,dx$<br><br>**Arc Length, $x=g(y)$:** $L=\int_c^d \sqrt{1+[g'(y)]^2}\,dy$<br><br>**Distance Traveled (Parametric),** for $x(t),y(t)$ on $[t_1,t_2]$: $L=\int_{t_1}^{t_2} \sqrt{\left(\frac{dx}{dt}\right)^2+\left(\frac{dy}{dt}\right)^2}\,dt$<br><br>**Speed (Parametric):** $\text{Speed}=\sqrt{\left(\frac{dx}{dt}\right)^2+\left(\frac{dy}{dt}\right)^2}$ |
""",
    9: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 9: Parametric, Polar & Vectors — Quick Reference</h3>
</div>

| | |
|---|---|
| **9.1 (BC)**<br>Parametric Equations | **Parametric Form:** a curve defined by $x=x(t)$, $y=y(t)$, $t\in[a,b]$<br><br>**First Derivative:** $\frac{dy}{dx}=\frac{dy/dt}{dx/dt}=\frac{y'(t)}{x'(t)},\ x'(t)\neq 0$<br><br>**Tangent Lines:** horizontal tangent: $y'(t)=0$ and $x'(t)\neq 0$; vertical tangent: $x'(t)=0$ and $y'(t)\neq 0$<br><br>**Converting to Rectangular Form:** eliminate the parameter $t$ by solving one equation for $t$ and substituting into the other (when possible) |
| **9.2 (BC)**<br>Second Derivatives of Parametric Equations | **Second Derivative Formula:** $\frac{d^2y}{dx^2}=\frac{\frac{d}{dt}\left(\frac{dy}{dx}\right)}{dx/dt}$<br><br>**Step-by-Step:**<br>• **1.** Compute $\frac{dy}{dx}=\frac{y'(t)}{x'(t)}$<br>• **2.** Differentiate $\frac{dy}{dx}$ with respect to $t$: call it $\left(\frac{dy}{dx}\right)'$<br>• **3.** Divide by $x'(t)$: $\frac{d^2y}{dx^2}=\frac{\left(\frac{dy}{dx}\right)'}{x'(t)}$<br><br>**Concavity:** $\frac{d^2y}{dx^2}>0 \implies$ concave up &nbsp;&nbsp;\|&nbsp;&nbsp; $\frac{d^2y}{dx^2}<0 \implies$ concave down |
| **9.3 (BC)**<br>Arc Length of Parametric Curves | **Arc Length Formula:** $L=\int_{t_1}^{t_2} \sqrt{\left(\frac{dx}{dt}\right)^2+\left(\frac{dy}{dt}\right)^2}\,dt$<br><br>**Speed:** $\text{Speed}=\sqrt{\left(\frac{dx}{dt}\right)^2+\left(\frac{dy}{dt}\right)^2}$<br><br>**Distance Traveled vs. Displacement:** distance traveled $=$ arc length (always $\geq 0$)<br>Displacement in $x$: $\int_{t_1}^{t_2} x'(t)\,dt$ &nbsp;&nbsp;\|&nbsp;&nbsp; Displacement in $y$: $\int_{t_1}^{t_2} y'(t)\,dt$ |
| **9.4 (BC)**<br>Vector-Valued Functions | **Vector-Valued Function:** $\vec{r}(t)=\langle x(t),y(t)\rangle$<br><br>**Derivative (Velocity Vector):** $\vec{r}'(t)=\langle x'(t),y'(t)\rangle=\vec{v}(t)$<br><br>**Second Derivative (Acceleration Vector):** $\vec{r}''(t)=\langle x''(t),y''(t)\rangle=\vec{a}(t)$<br><br>**Key Quantities:**<br>• Speed: $\lvert\vec{v}(t)\rvert=\sqrt{[x'(t)]^2+[y'(t)]^2}$<br>• Direction of motion: angle $=\arctan\left(\frac{y'(t)}{x'(t)}\right)$<br>• $\vec{v}(t)=\vec{0}$ at rest; object stops momentarily |
| **9.5 (BC)**<br>Integrating Vector-Valued Functions | **Antiderivative:** $\int \vec{r}(t)\,dt=\left\langle \int x(t)\,dt,\ \int y(t)\,dt\right\rangle+\vec{C}$<br><br>**Definite Integral:** $\int_{t_1}^{t_2} \vec{r}(t)\,dt=\left\langle \int_{t_1}^{t_2} x(t)\,dt,\ \int_{t_1}^{t_2} y(t)\,dt\right\rangle$<br><br>**Finding Position from Velocity:** $\vec{r}(t)=\vec{r}(t_0)+\int_{t_0}^{t} \vec{v}(\tau)\,d\tau$<br>Use initial condition $\vec{r}(t_0)=\langle x_0,y_0\rangle$ to solve for constant $\vec{C}$ |
| **9.6 (BC)**<br>Motion Problems: Parametric & Vector | **Core Quantities:**<br>• **Position:** $\vec{r}(t)=\langle x(t),y(t)\rangle$<br>• **Velocity:** $\vec{v}(t)=\langle x'(t),y'(t)\rangle$<br>• **Acceleration:** $\vec{a}(t)=\langle x''(t),y''(t)\rangle$<br>• **Speed:** $\lvert\vec{v}(t)\rvert=\sqrt{(x')^2+(y')^2}$<br><br>**Total Distance Traveled:** $d=\int_{t_1}^{t_2} \lvert\vec{v}(t)\rvert\,dt=\int_{t_1}^{t_2} \sqrt{[x'(t)]^2+[y'(t)]^2}\,dt$<br><br>**Motion Analysis:** moving right: $x'(t)>0$; left: $x'(t)<0$<br>moving up: $y'(t)>0$; down: $y'(t)<0$<br>At rest: $x'(t)=0$ and $y'(t)=0$ |
| **9.7 (BC)**<br>Polar Coordinates & Differentiation | **Polar $\leftrightarrow$ Rectangular:** $x=r\cos\theta$, $y=r\sin\theta$ &nbsp;&nbsp;\|&nbsp;&nbsp; $r^2=x^2+y^2$, $\tan\theta=\frac{y}{x}$<br><br>**Common Polar Curves:** Circle: $r=a$; Rose: $r=a\cos(n\theta)$ or $a\sin(n\theta)$; Cardioid: $r=a(1\pm\cos\theta)$ or $a(1\pm\sin\theta)$; Limaçon: $r=a\pm b\cos\theta$; Lemniscate: $r^2=a^2\cos(2\theta)$; Spiral: $r=a\theta$<br><br>**Derivative in Polar Form:** $\frac{dy}{dx}=\frac{\frac{dr}{d\theta}\sin\theta+r\cos\theta}{\frac{dr}{d\theta}\cos\theta-r\sin\theta}$<br><br>**Horiz. & Vert. Tangents:** horizontal: numerator $=0$, denominator $\neq 0$; vertical: denominator $=0$, numerator $\neq 0$ |
| **9.8 (BC)**<br>Area of a Polar Region | **Area Formula (Single Curve):** $A=\frac{1}{2}\int_\alpha^\beta [r(\theta)]^2\,d\theta$<br><br>**Notes on Limits:** $\alpha$ and $\beta$ are the $\theta$-values that bound the region; for rose curves, find one petal's start/end angles; full circle: $\alpha=0,\beta=2\pi$ (or $0$ to $\pi$ for sin/cos curves that repeat)<br><br>**Area Using Symmetry:** $A=n\cdot\frac{1}{2}\int_{\alpha_0}^{\beta_0} r^2\,d\theta$ |
| **9.9 (BC)**<br>Area Between Two Polar Curves | **Formula:** $A=\frac{1}{2}\int_\alpha^\beta \Big([r_{\text{outer}}(\theta)]^2-[r_{\text{inner}}(\theta)]^2\Big)\,d\theta$<br><br>**Steps:**<br>• **1.** Find intersection points by setting $r_1(\theta)=r_2(\theta)$; also check the pole $r=0$<br>• **2.** Identify which curve is the outer (larger $r$) on the interval<br>• **3.** Integrate outer$^2$ minus inner$^2$, multiplied by $\frac{1}{2}$<br><br>**Important Caution:** polar curves can intersect at the pole even when $r_1(\theta)\neq r_2(\theta)$ for the same $\theta$ — always check $r=0$ separately and sketch the curves |
""",
    10: r"""
<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 10: Infinite Sequences & Series — Quick Reference</h3>
</div>

| | |
|---|---|
| **10.1 (BC)**<br>Convergent & Divergent Infinite Series | **Infinite Series Definition:** $\sum_{n=1}^{\infty} a_n=\lim_{N\to\infty} S_N,\ S_N=\sum_{n=1}^{N} a_n$<br><br>**Convergence vs. Divergence:** if $\lim_{N\to\infty}S_N=L$ (finite) $\implies$ series converges to $L$; if limit is $\pm\infty$ or DNE $\implies$ series diverges<br><br>**Telescoping Series:** terms cancel in pairs. Write out partial sums, identify cancellation, then take the limit: $\sum_{n=1}^{\infty}(a_n-a_{n+1})=a_1-\lim_{n\to\infty}a_{n+1}$ |
| **10.2 (BC)**<br>Geometric Series | **Form:** $\sum_{n=0}^{\infty} ar^n=a+ar+ar^2+\dots$<br><br>**Convergence:** $\lvert r \rvert<1$: converges to $S=\frac{a}{1-r}$ &nbsp;&nbsp;\|&nbsp;&nbsp; $\lvert r \rvert\geq 1$: diverges<br><br>**Notes:** $a=$ first term, $r=$ common ratio. If series starts at $n=1$: first term is $ar$ |
| **10.3 (BC)**<br>$n$th Term Test for Divergence | **Statement:** if $\lim_{n\to\infty} a_n\neq 0$ (or DNE), then $\sum a_n$ diverges<br><br>**Critical Warning:** if $\lim_{n\to\infty} a_n=0$, the test is inconclusive — the series may converge or diverge. This test can only confirm divergence, never convergence |
| **10.4 (BC)**<br>Integral Test for Convergence | **Conditions:** $f$ must be continuous, positive, and decreasing on $[1,\infty)$, with $a_n=f(n)$<br><br>**Statement:** $\sum_{n=1}^{\infty} a_n$ and $\int_1^{\infty} f(x)\,dx$ both converge or both diverge<br><br>**Note:** the value of the integral does *not* equal the sum of the series — the test only determines behavior |
| **10.5 (BC)**<br>Harmonic Series & $p$-Series | **$p$-Series:** $\sum_{n=1}^{\infty} \frac{1}{n^p}$ — $p>1$: converges &nbsp;&nbsp;\|&nbsp;&nbsp; $p\leq 1$: diverges<br><br>**Harmonic Series:** $\sum_{n=1}^{\infty}\frac{1}{n}$ ($p=1$) $\implies$ diverges |
| **10.6 (BC)**<br>Comparison Tests for Convergence | **Direct Comparison Test (DCT):** for $0\leq a_n\leq b_n$: $\sum b_n$ converges $\implies\sum a_n$ converges; $\sum a_n$ diverges $\implies\sum b_n$ diverges<br><br>**Limit Comparison Test (LCT):** let $L=\lim_{n\to\infty}\frac{a_n}{b_n}$ with $b_n>0$:<br>• $0<L<\infty$: $\sum a_n$ and $\sum b_n$ same behavior<br>• $L=0$: $\sum b_n$ conv. $\implies\sum a_n$ conv.<br>• $L=\infty$: $\sum b_n$ div. $\implies\sum a_n$ div. |
| **10.7 (BC)**<br>Alternating Series Test | **Form:** $\sum_{n=1}^{\infty}(-1)^{n+1}b_n=b_1-b_2+b_3-\dots,\ b_n>0$<br><br>**Conditions for Convergence (AST):**<br>• **1.** $b_n$ is decreasing: $b_{n+1}\leq b_n$ for all $n$<br>• **2.** $\lim_{n\to\infty} b_n=0$<br>Both conditions must hold $\implies$ series converges |
| **10.8 (BC)**<br>Ratio Test for Convergence | **Statement:** let $L=\lim_{n\to\infty}\lvert\frac{a_{n+1}}{a_n}\rvert$:<br>• $L<1$: series converges absolutely<br>• $L>1$ (or $L=\infty$): series diverges<br>• $L=1$: inconclusive — use another test<br><br>**Best Used For:** series with factorials ($n!$), exponentials ($r^n$), or products — wherever the ratio simplifies cleanly |
| **10.9 (BC)**<br>Absolute or Conditional Convergence | **Definitions:** $\sum a_n$ **absolutely converges** if $\sum\lvert a_n \rvert$ converges; $\sum a_n$ **conditionally converges** if $\sum a_n$ converges but $\sum\lvert a_n \rvert$ diverges<br><br>**Key Fact:** absolute convergence $\implies$ convergence (not vice versa)<br><br>**Decision Flow:**<br>• **1.** Test $\sum\lvert a_n \rvert$: if it converges $\implies$ absolutely convergent<br>• **2.** If $\sum\lvert a_n \rvert$ diverges but $\sum a_n$ converges $\implies$ conditionally convergent<br>• **3.** If both diverge $\implies$ divergent |
| **10.10 (BC)**<br>Alternating Series Error Bound | **Error Bound:** for a convergent alternating series, the error in using $S_N$ to approximate $S$ satisfies $\lvert S-S_N \rvert\leq b_{N+1}$ (error is at most the absolute value of the first omitted term)<br><br>**Conditions:** the series must satisfy the AST conditions (decreasing, limit $\to 0$)<br><br>**Overestimate vs. Underestimate:** if first omitted term is positive $\implies S_N$ underestimates $S$; if negative $\implies S_N$ overestimates $S$ |
| **10.11 (BC)**<br>Taylor Polynomial Approximations | **$n$th-Degree Taylor Polynomial centered at $x=a$:**<br>$P_n(x)=\sum_{k=0}^{n} \frac{f^{(k)}(a)}{k!}(x-a)^k$<br>$=f(a)+f'(a)(x-a)+\frac{f''(a)}{2!}(x-a)^2+\dots$<br><br>**Maclaurin Polynomial** (centered at $a=0$): $P_n(x)=\sum_{k=0}^{n} \frac{f^{(k)}(0)}{k!}x^k$<br><br>**Common Maclaurin Polynomials:**<br>• $e^x \approx 1+x+\frac{x^2}{2!}+\frac{x^3}{3!}+\dots$<br>• $\sin x \approx x-\frac{x^3}{3!}+\frac{x^5}{5!}-\dots$<br>• $\cos x \approx 1-\frac{x^2}{2!}+\frac{x^4}{4!}-\dots$<br>• $\ln(1+x) \approx x-\frac{x^2}{2}+\frac{x^3}{3}-\dots$<br>• $\frac{1}{1-x} \approx 1+x+x^2+x^3+\dots$ |
| **10.12 (BC)**<br>Lagrange Error Bound | **Statement:** if $\lvert f^{(n+1)}(t) \rvert\leq M$ for all $t$ between $a$ and $x$, then:<br>$\lvert f(x)-P_n(x) \rvert\leq \frac{M}{(n+1)!}\lvert x-a \rvert^{n+1}$<br><br>**Steps:**<br>• **1.** Find $f^{(n+1)}(x)$ (one degree higher than $P_n$)<br>• **2.** Bound it: find $M=\max\lvert f^{(n+1)}(t) \rvert$ on the interval<br>• **3.** Plug into the error formula<br><br>**Note:** the Lagrange bound gives a **worst-case** (maximum possible) error, not the exact error |
| **10.13 (BC)**<br>Radius & Interval of Convergence | **Power Series Form:** $\sum_{n=0}^{\infty} c_n(x-a)^n$<br><br>**Finding Radius $R$:** apply the Ratio Test to get $L$ in terms of $x$; set $L<1$ and solve for $\lvert x-a \rvert<R$<br><br>**Interval of Convergence:**<br>• **1.** Start with $(a-R, a+R)$<br>• **2.** Check each endpoint separately by substituting into the series and applying an appropriate test<br>• **3.** State whether endpoints are included ([, ]) or excluded ((, ))<br><br>**Special Cases:** $R=\infty$: converges for all $x\in(-\infty,\infty)$ &nbsp;&nbsp;\|&nbsp;&nbsp; $R=0$: converges only at $x=a$<br><br>**Differentiation:** $\frac{d}{dx}\sum_{n=0}^{\infty}c_nx^n=\sum_{n=1}^{\infty}nc_nx^{n-1}$<br>**Integration:** $\int\sum_{n=0}^{\infty}c_nx^n\,dx=\sum_{n=0}^{\infty}\frac{c_n}{n+1}x^{n+1}+C$<br>Both operations preserve the same radius of convergence; check endpoints separately |
| **10.14 (BC)**<br>Taylor & Maclaurin Series | **Taylor Series** (centered at $x=a$): $f(x)=\sum_{n=0}^{\infty} \frac{f^{(n)}(a)}{n!}(x-a)^n$<br><br>**Key Maclaurin Series:**<br>• $e^x = \sum_{n=0}^{\infty}\frac{x^n}{n!}$, all $x$<br>• $\sin x = \sum_{n=0}^{\infty}\frac{(-1)^n x^{2n+1}}{(2n+1)!}$, all $x$<br>• $\cos x = \sum_{n=0}^{\infty}\frac{(-1)^n x^{2n}}{(2n)!}$, all $x$<br>• $\frac{1}{1-x} = \sum_{n=0}^{\infty} x^n$, $\lvert x \rvert<1$<br>• $\ln(1+x) = \sum_{n=1}^{\infty}\frac{(-1)^{n+1}x^n}{n}$, $-1<x\leq 1$ |
| **10.15 (BC)**<br>Representing Functions as Power Series | **Substitution:** replace $x$ in a known series with an expression in $x$: $\frac{1}{1-x}=\sum x^n \implies \frac{1}{1+x^2}=\sum(-1)^n x^{2n}$<br><br>**Techniques:**<br>• Form $\frac{1}{1\pm u} \implies$ Geometric series sub<br>• Derivative of known $\implies$ Differentiate term-by-term<br>• Antiderivative of known $\implies$ Integrate term-by-term |
"""
}

@st.cache_data(ttl=3600)
def get_question_map():
    """Cache the mapping of question_id to unit_number to save database calls."""
    q_res = supabase.table("questions").select("question_id, unit_number").execute()
    return {q['question_id']: q['unit_number'] for q in q_res.data} if q_res.data else {}

# --- 3. Session State Management ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
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
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = []
if 'failed_attempts' not in st.session_state:
    st.session_state.failed_attempts = 0
if 'lockout_until' not in st.session_state:
    st.session_state.lockout_until = 0
if 'reviewing_q_id' not in st.session_state:
    st.session_state.reviewing_q_id = None
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'
if 'current_answers' not in st.session_state:
    st.session_state.current_answers = {}
if 'hide_guide' not in st.session_state:
    st.session_state.hide_guide = False
if 'quiz_mode' not in st.session_state:
    st.session_state.quiz_mode = "Exam Mode"

# --- 4. Core Application Logic ---
def start_quiz(unit=None, selected_subtopic="All Subtopics"):
    if unit:
        # Build the dynamic query
        query = supabase.table("questions").select("*").eq("unit_number", unit)
        
        # If the student selected a specific subtopic, apply the filter!
        if selected_subtopic != "All Subtopics":
            query = query.eq("subtopic", selected_subtopic)
            
        response = query.execute()
        questions = response.data
        
        if questions:
            random.shuffle(questions)
            
    else:
        all_questions_response = supabase.table("questions").select("*").execute()
        all_questions = all_questions_response.data
        
        attempts_response = supabase.table("attempts").select("is_correct, question_id").eq("user_id", st.session_state.user_id).execute()
        attempts = attempts_response.data
        
        q_map = get_question_map()
        
        weak_units = []
        if attempts:
            unit_stats = {}
            for a in attempts:
                q_id = a.get('question_id')
                if q_id in q_map:
                    u = q_map[q_id]
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
    st.session_state.user_answers = []
    st.session_state.current_answers = {}
    st.session_state.quiz_started = True
    st.session_state.q_start_time = time.time()
    st.session_state.current_screen = "quiz"
    st.rerun()

def start_saved_quiz():
    """Generates a custom quiz using ONLY the questions the student has starred/saved in their vault."""
    saved_res = supabase.table("saved_questions").select("question_id").eq("user_id", st.session_state.user_id).execute()
    
    if not saved_res.data:
        st.toast("⭐ You haven't saved any questions yet! Complete a quiz and star hard questions to review them here.", icon="⚠️")
        return
        
    saved_q_ids = [item['question_id'] for item in saved_res.data]
    q_res = supabase.table("questions").select("*").in_("question_id", saved_q_ids).execute()
    questions = q_res.data if q_res.data else []
    
    if not questions:
        return
        
    random.shuffle(questions)
    
    st.session_state.quiz_questions = questions[:10] 
    st.session_state.current_q_index = 0
    st.session_state.quiz_score = 0
    st.session_state.user_answers = []
    st.session_state.quiz_started = True
    st.session_state.q_start_time = time.time()
    st.session_state.current_screen = "quiz"
    st.rerun()

def submit_entire_quiz():
    end_time = time.time()
    total_time = int(end_time - st.session_state.q_start_time)
    # Average the time taken across all questions for the analytics engine
    avg_time = max(1, total_time // len(st.session_state.quiz_questions))
    
    st.session_state.quiz_score = 0
    st.session_state.user_answers = []
    attempts_batch = []

    for idx, q in enumerate(st.session_state.quiz_questions):
        # Retrieve their saved answer, or default to "A" if they skipped it
        selected_option = st.session_state.current_answers.get(idx, "A")
        is_correct = 1 if selected_option == q['correct_option'] else 0
        
        if is_correct:
            st.session_state.quiz_score += 1

        st.session_state.user_answers.append({
            'question_id': q['question_id'],
            'question': q['question_text'],
            'selected': selected_option,
            'selected_text': q[f"option_{selected_option.lower()}"],
            'correct': q['correct_option'],
            'correct_text': q[f"option_{q['correct_option'].lower()}"],
            'is_correct': is_correct
        })

        attempts_batch.append({
            "user_id": st.session_state.user_id,
            "question_id": q['question_id'],
            "selected_option": selected_option,
            "is_correct": is_correct,
            "time_taken_seconds": avg_time
        })

    # Bulk insert all attempts into Supabase for maximum speed
    if attempts_batch:
        supabase.table("attempts").insert(attempts_batch).execute()
    
    # Push the user to the Quiz Review screen
    st.session_state.current_q_index = len(st.session_state.quiz_questions)
    st.rerun()

def save_to_vault(q_id):
    """Saves a question to the student's personal vault in Supabase."""
    try:
        supabase.table("saved_questions").insert({
            "user_id": st.session_state.user_id,
            "question_id": q_id
        }).execute()
        st.toast("✅ Question saved to your Vault!", icon="⭐")
    except Exception as e:
        err_msg = str(e)
        if "duplicate" in err_msg or "23505" in err_msg:
            st.toast("This question is already in your Vault!", icon="⭐")
        else:
            st.toast(f"Error saving question: {err_msg}", icon="❌")

def remove_from_vault(q_id):
    """Deletes a mastered question from the student's personal vault."""
    try:
        supabase.table("saved_questions").delete().eq("user_id", st.session_state.user_id).eq("question_id", q_id).execute()
        st.toast("Question removed from your Vault!", icon="✅")
    except Exception:
        st.toast("Error removing question.", icon="❌")

# --- 5. UI Screens ---
def vault_screen():
    st.markdown("<h1 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-star' style='color: #C09B5A;'></i> My Saved Questions Vault</h1>", unsafe_allow_html=True)
    st.write("---")

    # 1. Fetch saved question IDs for this user
    saved_res = supabase.table("saved_questions").select("question_id").eq("user_id", st.session_state.user_id).execute()
    
    if not saved_res.data:
        st.info("Your vault is empty! Take a quiz and click 'Save to Vault' on questions you want to review later.")
        return

    saved_q_ids = [item['question_id'] for item in saved_res.data]
    
    # 2. Fetch the actual questions from the question bank
    q_res = supabase.table("questions").select("*").in_("question_id", saved_q_ids).execute()
    questions = q_res.data if q_res.data else []

    if not questions:
        st.info("Your vault is empty!")
        return

    # ==========================================
    # VIEW 1: SPECIFIC QUESTION REVIEW MODE
    # ==========================================
    if st.session_state.get('reviewing_q_id'):
        # Find the specific question the user clicked
        q = next((q for q in questions if q['question_id'] == st.session_state.reviewing_q_id), None)
        
        if q:
            if st.button("← Back to Vault Grid"):
                st.session_state.reviewing_q_id = None
                st.rerun()
            
            st.write("---")
            st.markdown(f"### Unit {q['unit_number']} - {q['difficulty']}")
            
            # Show image first, just like the real quiz!
            if q.get('image_url'):
                st.image(q['image_url'], use_container_width=True)
                
            st.markdown(f"**{q['question_text']}**")
            st.write("")
            st.write(f"**A)** {q['option_a']}")
            st.write(f"**B)** {q['option_b']}")
            st.write(f"**C)** {q['option_c']}")
            st.write(f"**D)** {q['option_d']}")
            st.write("---")
            correct_letter = q['correct_option']
            correct_text = q[f"option_{correct_letter.lower()}"]
            st.markdown(f"<span style='display: block; background-color: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; padding: 14px; border-radius: 8px; color: #22c55e; margin-bottom: 15px;'><b>✅ Correct Answer:</b> {correct_letter}) {correct_text}</span>", unsafe_allow_html=True)
            
            if st.button("Remove from Vault", type="primary"):
                supabase.table("saved_questions").delete().eq("user_id", st.session_state.user_id).eq("question_id", q['question_id']).execute()
                st.session_state.reviewing_q_id = None
                st.toast("Question removed from Vault!", icon="✅")
                time.sleep(0.5)
                st.rerun()
        else:
            st.session_state.reviewing_q_id = None
            st.rerun()
        return

    # ==========================================
    # VIEW 2: KHAN ACADEMY STYLE GRID
    # ==========================================
    st.markdown(f"**Total Saved Questions:** {len(questions)}")
    if st.button("Generate 10-Question Quiz from Vault", type="primary", use_container_width=True):
        start_saved_quiz()
    st.write("---")

    unit_titles = {
        1: "Limits", 2: "Diff Basics", 3: "Composite", 4: "Context Apps", 5: "Analytical Apps",
        6: "Integration", 7: "Diff Eq", 8: "Integration Apps", 9: "Parametric/Polar", 10: "Series"
    }

    # Group questions by unit
    q_by_unit = {i: [] for i in range(1, 11)}
    for q in questions:
        q_by_unit[q['unit_number']].append(q)

    # Draw the Grid row by row
    for u in range(1, 11):
        col1, col2 = st.columns([1.5, 4])
        
        with col1:
            st.markdown(f"<div style='padding-top: 10px;'><b>Unit {u}</b><br><span style='font-size: 12px; color: gray;'>{unit_titles[u]}</span></div>", unsafe_allow_html=True)
            
        with col2:
            unit_qs = q_by_unit[u]
            if not unit_qs:
                st.markdown("<div style='padding-top: 10px; color: #A0A0A0; font-size: 14px;'>This unit does not include saved questions.</div>", unsafe_allow_html=True)
            else:
                # Chunk buttons into rows of 6 so it looks like a clean grid
                chunk_size = 6
                for i in range(0, len(unit_qs), chunk_size):
                    chunk = unit_qs[i:i+chunk_size]
                    # Create exactly 6 columns so the buttons stay small/square
                    b_cols = st.columns(chunk_size) 
                    for j, q in enumerate(chunk):
                        with b_cols[j]:
                            if st.button(f"{i+j+1}", key=f"vq_{q['question_id']}", use_container_width=True):
                                st.session_state.reviewing_q_id = q['question_id']
                                st.rerun()
        st.write("---")

def login_screen():
    st.write("") # Top padding
    st.write("")
    
    # --- Split Screen Layout: 1.2 parts Info (Left) | 0.2 Spacing | 1 part Login (Right) ---
    col_info, col_space, col_login = st.columns([1.2, 0.2, 1])
    
    with col_info:
        st.markdown("""
        <div style="padding-top: 30px; padding-right: 20px;">
            <h1 style="color: #0B1B3D; font-size: 42px; font-weight: 800; line-height: 1.1; margin-bottom: 15px;">
                Master AP Calculus.<br>
                <span style="color: #C09B5A;">Smarter, Not Harder.</span>
            </h1>
            <p style="color: #64748B; font-size: 16px; margin-bottom: 35px; line-height: 1.6;">
                Welcome to Novara Academy's Adaptive Engine. We track your performance in real-time to pinpoint weaknesses, optimize your study time, and help you secure a 5 on the AP Exam.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; align-items: flex-start; margin-bottom: 25px;">
            <div style="background-color: rgba(192, 155, 90, 0.15); border-radius: 8px; padding: 10px; margin-right: 15px;">
                <i class="fa-solid fa-bullseye" style="color: #C09B5A; font-size: 20px;"></i>
            </div>
            <div>
                <b style="color: #0B1B3D; font-size: 16px;">Adaptive Quizzing</b>
                <p style="color: #64748B; font-size: 14px; margin: 2px 0 0 0;">Dynamic algorithms automatically target your weakest units.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; align-items: flex-start; margin-bottom: 25px;">
            <div style="background-color: rgba(192, 155, 90, 0.15); border-radius: 8px; padding: 10px; margin-right: 15px;">
                <i class="fa-solid fa-crosshairs" style="color: #C09B5A; font-size: 20px;"></i>
            </div>
            <div>
                <b style="color: #0B1B3D; font-size: 16px;">Advanced Analytics</b>
                <p style="color: #64748B; font-size: 14px; margin: 2px 0 0 0;">Track your mastery with precision radar charts and speed metrics.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="display: flex; align-items: flex-start;">
            <div style="background-color: rgba(192, 155, 90, 0.15); border-radius: 8px; padding: 10px; margin-right: 15px;">
                <i class="fa-solid fa-bookmark" style="color: #C09B5A; font-size: 20px;"></i>
            </div>
            <div>
                <b style="color: #0B1B3D; font-size: 16px;">Personal Study Vault</b>
                <p style="color: #64748B; font-size: 14px; margin: 2px 0 0 0;">Save challenging questions and review them on demand.</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_login:
        st.markdown("<div style='text-align: center; margin-bottom: 10px;'><i class='fa-solid fa-graduation-cap' style='color: #C09B5A; font-size: 32px;'></i><h2 style='color: #0B1B3D; margin-top: 10px;'>Novara Academy</h2></div>", unsafe_allow_html=True)
        
        # --- SIGN IN VIEW ---
        if st.session_state.auth_mode == 'login':
            st.markdown("<p style='text-align: center; color: #64748B; margin-top: -10px; margin-bottom: 30px; font-size: 15px;'>Welcome back! Please enter your details.</p>", unsafe_allow_html=True)
            
            login_email = st.text_input("Email Address", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            st.write("")
            if st.button("Sign In", type="primary", use_container_width=True):
                # Reset attempts if the penalty time has officially expired
                if st.session_state.failed_attempts >= 5 and time.time() > st.session_state.lockout_until:
                    st.session_state.failed_attempts = 0
                
                if time.time() < st.session_state.lockout_until:
                    remaining_seconds = int(st.session_state.lockout_until - time.time())
                    st.markdown(f"<div style='background-color: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 14px; border-radius: 8px; color: #ef4444; margin-bottom: 15px;'><i class='fa-solid fa-lock'></i> <b>Account temporarily locked.</b> Try again in {remaining_seconds} seconds.</div>", unsafe_allow_html=True)
                elif login_email and login_password:
                    try:
                        user_record = supabase.table("users").select("*").eq("email", login_email).execute()
                        if user_record.data:
                            user = user_record.data[0]
                            if bcrypt.checkpw(login_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                                st.session_state.failed_attempts = 0
                                st.session_state.lockout_until = 0
                                st.session_state.logged_in = True
                                st.session_state.user_id = user['user_id']
                                st.session_state.username = user['username']
                                st.session_state.is_admin = user.get('is_admin', False)
                                st.session_state.current_screen = "dashboard"
                                st.success(f"Welcome back, {user['username']}!")
                                time.sleep(1)
                                st.rerun()
                            else:
                                st.session_state.failed_attempts += 1
                                if st.session_state.failed_attempts >= 5:
                                    st.session_state.lockout_until = time.time() + 300 
                                    st.markdown("<div style='background-color: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 14px; border-radius: 8px; color: #ef4444; margin-bottom: 15px;'><i class='fa-solid fa-lock'></i> <b>Too many failed attempts.</b> You are locked out for 5 minutes.</div>", unsafe_allow_html=True)
                                else:
                                    attempts_left = 5 - st.session_state.failed_attempts
                                    st.error(f"Invalid email or password. ({attempts_left} attempts remaining)")
                        else:
                            st.session_state.failed_attempts += 1
                            if st.session_state.failed_attempts >= 5:
                                st.session_state.lockout_until = time.time() + 300
                                st.markdown("<div style='background-color: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 14px; border-radius: 8px; color: #ef4444; margin-bottom: 15px;'><i class='fa-solid fa-lock'></i> <b>Too many failed attempts.</b> You are locked out for 5 minutes.</div>", unsafe_allow_html=True)
                            else:
                                attempts_left = 5 - st.session_state.failed_attempts
                                st.error(f"Invalid email or password. ({attempts_left} attempts remaining)")
                    except Exception as e:
                        st.error(f"Error during login: {e}")
                else:
                    st.warning("Please fill in both fields.")
            
            # The Toggle Link
            st.write("---")
            st.markdown("<div style='text-align: center; color: #64748B; font-size: 13px; margin-bottom: 10px;'>Don't have an account?</div>", unsafe_allow_html=True)
            if st.button("Sign Up", use_container_width=True):
                st.session_state.auth_mode = 'register'
                st.rerun()

        # --- SIGN UP VIEW ---
        else:
            st.markdown("<p style='text-align: center; color: #64748B; margin-top: -10px; margin-bottom: 30px; font-size: 15px;'>Create an account to start mastering AP Calc.</p>", unsafe_allow_html=True)
            
            reg_username = st.text_input("Full Name", key="reg_username")
            reg_email = st.text_input("Email Address", key="reg_email")
            reg_password = st.text_input("Password", type="password", key="reg_password")
            
            st.write("")
            if st.button("Sign Up", type="primary", use_container_width=True):
                if reg_username and reg_email and reg_password:
                    email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                    if not re.match(email_pattern, reg_email):
                        st.warning("Please enter a valid email address format (e.g., student@example.com).")
                    elif len(reg_password) < 8:
                        st.warning("Password must be at least 8 characters long.")
                    else:
                        try:
                            email_check = supabase.table("users").select("*").eq("email", reg_email).execute()
                            username_check = supabase.table("users").select("*").eq("username", reg_username).execute()
                            
                            if email_check.data:
                                st.error("Registration failed: An account with this email already exists.")
                            elif username_check.data:
                                st.error("Registration failed: That username is already taken. Please choose another one.")
                            else:
                                salt = bcrypt.gensalt()
                                hashed_pw = bcrypt.hashpw(reg_password.encode('utf-8'), salt).decode('utf-8')
                                
                                supabase.table("users").insert({
                                    "username": reg_username,
                                    "email": reg_email,
                                    "password_hash": hashed_pw 
                                }).execute()
                                st.success("Account created successfully! Switching to Log In...")
                                time.sleep(1.5)
                                st.session_state.auth_mode = 'login'
                                st.rerun()
                        except Exception as e:
                            st.error(f"Registration failed: {e}")
                else:
                    st.warning("Please fill in all fields.")

            # The Toggle Link
            st.write("---")
            st.markdown("<div style='text-align: center; color: #64748B; font-size: 13px; margin-bottom: 10px;'>Already have an account?</div>", unsafe_allow_html=True)
            if st.button("Sign In", use_container_width=True):
                st.session_state.auth_mode = 'login'
                st.rerun()

    # --- MINIMALIST SOCIAL MEDIA & LEGAL FOOTER ---
    st.write("---")
    st.markdown("""
    <style>
    .social-icon {
        width: 32px;
        height: 32px;
        margin: 0 20px;
        transition: transform 0.2s ease-in-out, opacity 0.2s;
        opacity: 0.65;
    }
    .social-icon:hover {
        transform: scale(1.15);
        opacity: 1;
    }
    .social-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .legal-footer {
        text-align: center;
        color: #A0A0A0;
        font-size: 12px;
        font-family: sans-serif;
        padding-bottom: 30px;
        line-height: 1.5;
    }
    </style>
    
    <div class="social-container">
        <a href='https://t.me/Novara_Academy' target='_blank'>
            <img class="social-icon" src='https://cdn.simpleicons.org/telegram/0B1B3D' alt='Telegram'/>
        </a>
        <a href='https://www.instagram.com/thenovaraacademy' target='_blank'>
            <img class="social-icon" src='https://cdn.simpleicons.org/instagram/0B1B3D' alt='Instagram'/>
        </a>
        <a href='https://youtube.com/@thenovara_academy' target='_blank'>
            <img class="social-icon" src='https://cdn.simpleicons.org/youtube/0B1B3D' alt='YouTube'/>
        </a>
    </div>
    
    <div class="legal-footer">
        &copy; 2026 Novara Academy. All rights reserved.<br>
        Designed & Engineered in Uzbekistan.<br>
        <span style="font-size: 10px; opacity: 0.7;">For educational purposes only. Not affiliated with the College Board.</span>
    </div>
    """, unsafe_allow_html=True)

def dashboard_screen():
    st.markdown(f"<h1 style='text-align: center; color: #0B1B3D;'>Welcome, {st.session_state.username}!</h1>", unsafe_allow_html=True)
    
    # --- 0. 🗺️ ONBOARDING QUICK GUIDE ---
    if not st.session_state.get('hide_guide', False):
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0B1B3D 0%, #152A55 100%); padding: 25px; border-radius: 16px; border: 1px solid #C09B5A; box-shadow: 0 10px 20px rgba(0,0,0,0.15); margin-bottom: 15px; margin-top: 10px;">
            <h3 style="color: #C09B5A; margin-top: 0; text-align: center; margin-bottom: 20px;"><i class="fa-solid fa-map-location-dot"></i> Welcome to Novara Academy</h3>
            <div style="display: flex; flex-wrap: wrap; gap: 20px;">
                <div style="flex: 1 1 45%; min-width: 200px;">
                    <h4 style="color: #FFFFFF; margin-top: 0; font-size: 16px;"><i class="fa-solid fa-brain" style="color: #C09B5A;"></i> Adaptive Engine</h4>
                    <p style="font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 0;">Click <b>Start Full Adaptive Quiz</b>. The algorithm tracks your unit accuracy and automatically targets your weakest topics to force improvement.</p>
                </div>
                <div style="flex: 1 1 45%; min-width: 200px;">
                    <h4 style="color: #FFFFFF; margin-top: 0; font-size: 16px;"><i class="fa-solid fa-stopwatch" style="color: #C09B5A;"></i> Practice vs. Exam Mode</h4>
                    <p style="font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 0;"><b>Practice Mode</b> gives you instant feedback and a relaxed timer to learn concepts. <b>Exam Mode</b> runs a strict 15-minute clock with zero hints until the end.</p>
                </div>
                <div style="flex: 1 1 45%; min-width: 200px;">
                    <h4 style="color: #FFFFFF; margin-top: 0; font-size: 16px;"><i class="fa-solid fa-fire" style="color: #C09B5A;"></i> XP & Streaks</h4>
                    <p style="font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 0;">Consistency is key. You earn <b>1 XP</b> for every <i>correct</i> answer. Practice daily to build your blazing streak and climb the Leaderboard!</p>
                </div>
                <div style="flex: 1 1 45%; min-width: 200px;">
                    <h4 style="color: #FFFFFF; margin-top: 0; font-size: 16px;"><i class="fa-solid fa-bookmark" style="color: #C09B5A;"></i> The Vault</h4>
                    <p style="font-size: 13px; color: #94A3B8; line-height: 1.5; margin-bottom: 0;">Don't lose hard questions. Click <b>Save to Vault</b> during a quiz review to build a personal bank, then generate custom practice quizzes.</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Got it! Dismiss Guide", type="primary", use_container_width=True):
            st.session_state.hide_guide = True
            st.rerun()
        st.write("---")

    # --- 1. ⏱️ AP EXAM COUNTDOWN & STREAK TRACKER ---
    tz = ZoneInfo("Asia/Tashkent")
    exam_datetime = datetime(2027, 5, 10, 8, 0, 0, tzinfo=tz) 
    now = datetime.now(tz)
    total_seconds = int((exam_datetime - now).total_seconds())
    
    # Force the streak to calculate based on Tashkent midnight, not server UTC
    today = datetime.now(tz).date()
    streak = 0
    unit_accuracies = {}
    
    try:
        # 🚨 FIX 1: Restored q_map and changed "created_at" back to "timestamp"
        q_map = get_question_map()
        response = supabase.table("attempts").select("timestamp, is_correct, question_id").eq("user_id", st.session_state.user_id).execute()
        
        if response.data:
            active_dates = set()
            unit_stats = {}
            
            for row in response.data:
                # Daily Streak Calculation
                if row.get("timestamp"):
                    active_dates.add(str(row["timestamp"])[:10])
                
                # Unit Accuracy for Trophy Case
                q_id = row.get("question_id")
                if q_id in q_map:
                    u = q_map[q_id]
                    if u not in unit_stats:
                        unit_stats[u] = {"correct": 0, "total": 0}
                    unit_stats[u]["total"] += 1
                    unit_stats[u]["correct"] += row["is_correct"]
            
            # Streak Logic
            current_date = today
            while current_date.strftime("%Y-%m-%d") in active_dates:
                streak += 1
                current_date -= timedelta(days=1)
            if streak == 0:
                current_date = today - timedelta(days=1)
                while current_date.strftime("%Y-%m-%d") in active_dates:
                    streak += 1
                    current_date -= timedelta(days=1)
                    
            # Compute percentage per unit
            for u, stats in unit_stats.items():
                if stats["total"] > 0:
                    unit_accuracies[u] = (stats["correct"] / stats["total"]) * 100
    except Exception:
        pass

    # --- 2. Dynamic Gamification Gamestate Logic ---
    if streak == 0:
        card_bg = "linear-gradient(135deg, #1E293B 0%, #0F172A 100%)" # Slate Gray
        icon_color = "#64748B"
        text_color = "#94A3B8"
        streak_msg = "Start your streak!"
    elif 1 <= streak <= 7:
        card_bg = "linear-gradient(135deg, #FBBF24 0%, #D97706 100%)" # Vibrant Yellow
        icon_color = "#FFFFFF"
        text_color = "#FFFFFF"
        streak_msg = "Heating Up!"
    elif 8 <= streak <= 30:
        card_bg = "linear-gradient(135deg, #F97316 0%, #C2410C 100%)" # Bright Orange
        icon_color = "#FFFFFF"
        text_color = "#FFFFFF"
        streak_msg = "On Fire!"
    else:
        card_bg = "linear-gradient(135deg, #EF4444 0%, #991B1B 100%)" # Blazing Red
        icon_color = "#FFFFFF"
        text_color = "#FFFFFF"
        streak_msg = "Unstoppable!"

    # --- 3. Live JavaScript Countdown Widget & Duolingo Layout ---
    components.html(
    f"""
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <div style="display: flex; justify-content: space-between; font-family: 'Inter', sans-serif; margin-bottom: 5px; margin-top: 15px;">
        <!-- Countdown Card -->
        <div style="background: linear-gradient(135deg, #0B1B3D 0%, #152A55 100%); border: 1px solid #C09B5A; border-radius: 16px; padding: 22px; width: 48%; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.15); box-sizing: border-box;">
            <h4 style="color: #E2E8F0; margin-top: 0; margin-bottom: 8px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;"><i class="fa-solid fa-hourglass-half" style="color: #C09B5A; margin-right: 5px;"></i> AP Calc Exam</h4>
            <h1 id="countdown" style="color: #C09B5A; margin: 0; font-size: 26px; font-weight: 800;"></h1>
            <p style="color: #A0A0A0; margin: 8px 0 0 0; font-size: 12px;">Time Left (May 10)</p>
        </div>
        
        <!-- Duolingo-Style Gamified Streak Card -->
        <div style="background: {card_bg}; border-radius: 16px; padding: 22px; width: 48%; text-align: center; box-shadow: 0 10px 20px rgba(0,0,0,0.15); box-sizing: border-box; display: flex; flex-direction: column; justify-content: center; align-items: center; transition: all 0.3s ease;">
            <div style="display: flex; justify-content: center; align-items: center; gap: 10px; margin-bottom: 4px;">
                <i class="fa-solid fa-fire" style="color: {icon_color}; font-size: 42px;"></i>
                <h1 style="color: {text_color}; margin: 0; font-size: 46px; font-weight: 800; line-height: 1;">{streak}</h1>
            </div>
            <p style="color: {text_color}; margin: 0; font-size: 15px; font-weight: 600; opacity: 0.95;">{streak_msg}</p>
        </div>
    </div>
    
    <script>
        let total_seconds = {total_seconds};
        const countdown_div = document.getElementById("countdown");

        function updateTimer() {{
            if (total_seconds <= 0) {{
                countdown_div.innerHTML = "<i class='fa-solid fa-champagne-glasses' style='color:#C09B5A;'></i> Exam Day!";
                clearInterval(timer);
                return;
            }}
            
            let d = Math.floor(total_seconds / (3600*24));
            let h = Math.floor((total_seconds % (3600*24)) / 3600);
            let m = Math.floor((total_seconds % 3600) / 60);
            let s = Math.floor(total_seconds % 60);
            
            let formatted_time = d + "d " + 
                                (h < 10 ? "0" : "") + h + "h " + 
                                (m < 10 ? "0" : "") + m + "m " + 
                                (s < 10 ? "0" : "") + s + "s";
                                
            countdown_div.innerText = formatted_time;
            total_seconds--;
        }}
        
        const timer = setInterval(updateTimer, 1000);
        updateTimer(); 
    </script>
    """,
    height=180
    )
    
    # --- 2. 🏆 TROPHY CASE (MASTERY BADGES) ---
    st.markdown("<h3 style='text-align: center; color: #0B1B3D; margin-bottom: 15px;'><i class='fa-solid fa-award' style='color: #C09B5A;'></i> Unit Mastery Trophy Case</h3>", unsafe_allow_html=True)
    
    unit_titles = {
        1: "Limits", 2: "Diff Basics", 3: "Composite", 4: "Context Apps", 5: "Analytical Apps",
        6: "Integration", 7: "Diff Eq", 8: "Integration Apps", 9: "Parametric/Polar", 10: "Series"
    }
    
    for row_start in [1, 6]:
        cols = st.columns(5)
        for idx, u_num in enumerate(range(row_start, row_start + 5)):
            acc = unit_accuracies.get(u_num, 0)
            is_mastered = acc >= 80.0
            
            bg_color = "#C09B5A" if is_mastered else "#0B1B3D"
            text_color = "#0B1B3D" if is_mastered else "#A0A0A0"
            border_style = "2px solid #C09B5A" if is_mastered else "1px solid #334155"
            
            icon = "<i class='fa-solid fa-trophy'></i>" if is_mastered else "<i class='fa-solid fa-lock'></i>"
            icon_color = "#0B1B3D" if is_mastered else "#A0A0A0"
            
            with cols[idx]:
                st.markdown(f"""
                <div style="background-color: {bg_color}; border: {border_style}; border-radius: 10px; padding: 10px 5px; text-align: center; margin-bottom: 12px;">
                    <span style="font-size: 18px; color: {icon_color};">{icon}</span><br>
                    <b style="color: {text_color}; font-size: 11px;">U{u_num}: {unit_titles[u_num]}</b><br>
                    <span style="color: {text_color}; font-size: 10px;">{acc:.0f}% Acc</span>
                </div>
                """, unsafe_allow_html=True)

    st.write("---")
    
    # --- 3. AP CALCULUS UNITS GRID ---
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

    # --- 4. 🌍 GLOBAL LEADERBOARD (Monthly & All-Time) ---
    st.write("---")
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-globe' style='color: #C09B5A;'></i> Global Leaderboard</h3>", unsafe_allow_html=True)
    
    # Fetch Leaderboard Data
    lb_users_res = supabase.table("users").select("user_id, username").execute()
    lb_users_dict = {u['user_id']: u['username'] for u in lb_users_res.data} if lb_users_res.data else {}
    
    lb_attempts_res = supabase.table("attempts").select("user_id, is_correct, timestamp").execute()
    
    if lb_attempts_res.data:
        df_lb = pd.DataFrame(lb_attempts_res.data)
        if not df_lb.empty and 'timestamp' in df_lb.columns:
            # Clean and filter the data
            df_lb['timestamp'] = pd.to_datetime(df_lb['timestamp'], errors='coerce')
            df_lb = df_lb[df_lb['is_correct'] == 1] # Only count correct answers (XP)
            
            # Force the monthly leaderboard to reset based on Tashkent time
            curr_month = datetime.now(tz).month
            curr_year = datetime.now(tz).year
            
            # --- Monthly Data ---
            df_monthly = df_lb[(df_lb['timestamp'].dt.month == curr_month) & (df_lb['timestamp'].dt.year == curr_year)]
            monthly_xp = df_monthly.groupby('user_id').size().reset_index(name='XP')
            monthly_xp['Student'] = monthly_xp['user_id'].map(lb_users_dict)
            monthly_xp = monthly_xp.sort_values(by='XP', ascending=False).head(10)[['Student', 'XP']]
            monthly_xp.index = range(1, len(monthly_xp) + 1)
            
            # --- All-Time Data ---
            alltime_xp = df_lb.groupby('user_id').size().reset_index(name='XP')
            alltime_xp['Student'] = alltime_xp['user_id'].map(lb_users_dict)
            alltime_xp = alltime_xp.sort_values(by='XP', ascending=False).head(10)[['Student', 'XP']]
            alltime_xp.index = range(1, len(alltime_xp) + 1)
            
            # Display Tabs
            tab_month, tab_alltime = st.tabs(["This Month", "All-Time"])
            with tab_month:
                st.markdown("<h4 style='color: #0B1B3D; margin-top: 5px;'><i class='fa-solid fa-calendar-days' style='color: #C09B5A;'></i> This Month's Scholars</h4>", unsafe_allow_html=True)
                if not monthly_xp.empty: st.dataframe(monthly_xp, use_container_width=True)
                else: st.markdown("<div style='background-color: rgba(192, 155, 90, 0.1); border: 1px solid #C09B5A; padding: 12px; border-radius: 8px; color: #C09B5A;'><i class='fa-solid fa-circle-info'></i> No points earned yet this month! Be the first on the board.</div>", unsafe_allow_html=True)
            with tab_alltime:
                st.markdown("<h4 style='color: #0B1B3D; margin-top: 5px;'><i class='fa-solid fa-trophy' style='color: #C09B5A;'></i> All-Time Hall of Fame</h4>", unsafe_allow_html=True)
                if not alltime_xp.empty: st.dataframe(alltime_xp, use_container_width=True)
                else: st.markdown("<div style='background-color: rgba(192, 155, 90, 0.1); border: 1px solid #C09B5A; padding: 12px; border-radius: 8px; color: #C09B5A;'><i class='fa-solid fa-circle-info'></i> No points earned yet.</div>", unsafe_allow_html=True)

    # --- MINIMALIST SOCIAL MEDIA & LEGAL FOOTER ---
    st.write("---")
    st.markdown("""
    <style>
    .social-icon {
        width: 32px;
        height: 32px;
        margin: 0 20px;
        transition: transform 0.2s ease-in-out, opacity 0.2s;
        opacity: 0.65;
    }
    .social-icon:hover {
        transform: scale(1.15);
        opacity: 1;
    }
    .social-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .legal-footer {
        text-align: center;
        color: #A0A0A0;
        font-size: 12px;
        font-family: sans-serif;
        padding-bottom: 30px;
        line-height: 1.5;
    }
    .legal-footer a {
        color: #C09B5A;
        text-decoration: none;
    }
    .legal-footer a:hover {
        text-decoration: underline;
    }
    </style>
    
    <div class="social-container">
        <a href='https://t.me/Novara_Academy' target='_blank'>
            <img class="social-icon" src='https://cdn.simpleicons.org/telegram/0B1B3D' alt='Telegram'/>
        </a>
        <a href='https://www.instagram.com/thenovaraacademy' target='_blank'>
            <img class="social-icon" src='https://cdn.simpleicons.org/instagram/0B1B3D' alt='Instagram'/>
        </a>
        <a href='https://youtube.com/@thenovara_academy' target='_blank'>
            <img class="social-icon" src='https://cdn.simpleicons.org/youtube/0B1B3D' alt='YouTube'/>
        </a>
    </div>
    
    <div class="legal-footer">
        &copy; 2026 Novara Academy. All rights reserved.<br>
        Designed & Engineered in Uzbekistan.<br>
        <span style="font-size: 10px; opacity: 0.7;">For educational purposes only. Not affiliated with the College Board.</span>
    </div>
    """, unsafe_allow_html=True)

def unit_detail_screen():
    unit_num = st.session_state.selected_unit
    unit_name = st.session_state.selected_unit_name
        
    st.markdown(f"<h1 style='text-align: center; color: #0B1B3D;'>{unit_name}</h1>", unsafe_allow_html=True)
    st.write("---")
    
    # --- 🆕 DYNAMIC SUBTOPIC SELECTOR ---
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-layer-group' style='color: #C09B5A;'></i> Select Subtopic</h3>", unsafe_allow_html=True)
    
    # Fetch all unique subtopics for this specific unit from the database
    res = supabase.table("questions").select("subtopic").eq("unit_number", unit_num).execute()
    
    subtopic_options = ["All Subtopics"]
    if res.data:
        # Extract unique valid subtopics (ignoring empty/None values)
        unique_subs = list(set([q['subtopic'] for q in res.data if q.get('subtopic')]))
        
        # Custom sorting logic to fix the "1.10 comes before 1.2" bug
        def subtopic_sort_key(s):
            match = re.match(r"^(\d+)\.(\d+)", s)
            if match:
                return (int(match.group(1)), int(match.group(2)), s)
            return (999, 999, s) # Puts things like "General Practice" safely at the bottom
            
        fetched_subs = sorted(unique_subs, key=subtopic_sort_key)
        subtopic_options.extend(fetched_subs)
    
    # Render the sleek dropdown
    selected_subtopic = st.selectbox("Focus on a specific skill:", subtopic_options, label_visibility="collapsed")
    st.write("---")
    
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-sliders' style='color: #C09B5A;'></i> Select Difficulty Level</h3>", unsafe_allow_html=True)    
    diff_col1, diff_col2, diff_col3, diff_col4 = st.columns(4)
    with diff_col1:
        if st.button("All", use_container_width=True): st.session_state.difficulty = "All"
    with diff_col2:
        if st.button("Easy", use_container_width=True): st.session_state.difficulty = "Easy"
    with diff_col3:
        if st.button("Medium", use_container_width=True): st.session_state.difficulty = "Medium"
    with diff_col4:
        if st.button("Hard", use_container_width=True): st.session_state.difficulty = "Hard"

    st.write("---")
    
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-stopwatch' style='color: #C09B5A;'></i> Select Testing Mode</h3>", unsafe_allow_html=True)    
    mode_col1, mode_col2 = st.columns(2)
    with mode_col1:
        if st.button("Exam Mode (Strict Timer, No Hints)", use_container_width=True): st.session_state.quiz_mode = "Exam Mode"
    with mode_col2:
        if st.button("Practice Mode (Untimed, Instant Feedback)", use_container_width=True): st.session_state.quiz_mode = "Practice Mode"
        
    st.info(f"**Current Settings:** **{st.session_state.difficulty}** Difficulty | **{st.session_state.quiz_mode}**")

    st.write("")
    
    # Change the button text dynamically based on what they selected
    btn_text = f"Start {st.session_state.quiz_mode}: {selected_subtopic}" if selected_subtopic != "All Subtopics" else f"Start Full Unit Quiz ({st.session_state.quiz_mode})"
    
    if st.button(btn_text, type="primary", use_container_width=True):
        start_quiz(unit=unit_num, selected_subtopic=selected_subtopic)
        
    st.write("---")
    
    with st.expander("View Unit Formulas & Cheat Sheets (Click to Expand)"):
        st.markdown(CHEAT_SHEETS.get(unit_num, "*Add your custom formulas for this unit here!*"), unsafe_allow_html=True)

def quiz_screen():
    # --- POST-QUIZ REVIEW SCREEN ---
    if st.session_state.current_q_index >= len(st.session_state.quiz_questions):
        st.markdown("<h2 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-flag-checkered' style='color: #C09B5A;'></i> Quiz Complete!</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #C09B5A;'>Your Score: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</h3>", unsafe_allow_html=True)
        st.write("---")
        
        st.markdown("<h3 style='color: #0B1B3D;'><i class='fa-solid fa-magnifying-glass' style='color: #C09B5A;'></i> Question Review</h3>", unsafe_allow_html=True)
        
        # --- 1. QUICKLY FETCH THE STUDENT'S VAULT FIRST ---
        vault_response = supabase.table("saved_questions").select("question_id").eq("user_id", st.session_state.user_id).execute()
        saved_q_ids = [item['question_id'] for item in vault_response.data] if vault_response.data else []
        
        for i, ans in enumerate(st.session_state.user_answers):
            st.markdown(f"**Q{i+1}:** {ans['question']}")
            
            if ans['is_correct']:
                st.markdown(f"<span style='display: block; background-color: rgba(34, 197, 94, 0.1); border: 1px solid #22c55e; padding: 14px; border-radius: 8px; color: #22c55e; margin-bottom: 12px;'><b>✅ Correct:</b> {ans['selected']}) {ans['selected_text']}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"<span style='display: block; background-color: rgba(239, 68, 68, 0.1); border: 1px solid #ef4444; padding: 14px; border-radius: 8px; color: #ef4444; margin-bottom: 12px;'><b>❌ Incorrect:</b> You chose {ans['selected']}) {ans['selected_text']}<br><br><i class='fa-solid fa-lightbulb' style='color: #eab308;'></i> <b style='color: #eab308;'>Right Answer:</b> <span style='color: #eab308;'>{ans['correct']}) {ans['correct_text']}</span></span>", unsafe_allow_html=True)
            
            # --- 2. DYNAMICALLY SHOW ONLY ONE BUTTON ---
            if ans['question_id'] in saved_q_ids:
                # If it's already in the vault, ONLY show the Remove button
                st.button("Remove from Vault", key=f"remove_btn_{i}_{ans['question_id']}", on_click=remove_from_vault, args=(ans['question_id'],))
            else:
                # If it's not in the vault, ONLY show the Save button
                st.button("Save to Vault", key=f"save_btn_{i}_{ans['question_id']}", on_click=save_to_vault, args=(ans['question_id'],))
            
            st.write("---")
            
        st.write("---")
        if st.button("Return to Dashboard", type="primary", use_container_width=True):
            st.session_state.quiz_started = False
            st.session_state.user_answers = [] 
            st.session_state.current_screen = "dashboard"
            st.rerun()
        return

    # --- ACTIVE QUIZ SCREEN ---
    q = st.session_state.quiz_questions[st.session_state.current_q_index]
    st.progress((st.session_state.current_q_index) / len(st.session_state.quiz_questions))
    st.markdown(f"**Question {st.session_state.current_q_index + 1} of {len(st.session_state.quiz_questions)}** (Unit {q['unit_number']} - {q['difficulty']})")
    
    elapsed = int(time.time() - st.session_state.q_start_time)
    components.html(
        f"""
        <div style="font-family: 'Inter', sans-serif; text-align: right; color: #0B1B3D; font-size: 18px; font-weight: bold; margin: 0; padding-right: 10px;">
            <i class="fa-solid fa-stopwatch" style="color: #0B1B3D;"></i> Time Elapsed: <span id="clock"></span>
        </div>
        <script>
            let time_elapsed = {elapsed};
            const clock_div = document.getElementById("clock");
            
            setInterval(() => {{
                let minutes = Math.floor(time_elapsed / 60);
                let seconds = time_elapsed % 60;
                
                let formatted_time = (minutes < 10 ? "0" : "") + minutes + ":" + (seconds < 10 ? "0" : "") + seconds;
                clock_div.innerText = formatted_time;
                
                if (time_elapsed > 90) {{
                    clock_div.style.color = "#FF4B4B";
                }}
                time_elapsed++;
            }}, 1000);
        </script>
        """,
        height=40
    )
    
    # --- 📈 NEW: GRAPH / IMAGE RENDERER ---
    if q.get('image_url'):
        st.image(q['image_url'], use_container_width=True)
        
    st.markdown(f"### {q['question_text']}")
    
    options = {
        "A": q['option_a'],
        "B": q['option_b'],
        "C": q['option_c'],
        "D": q['option_d']
    }
    
    # Remember previously selected answers if the student goes backwards
    saved_ans = st.session_state.current_answers.get(st.session_state.current_q_index, "A")
    radio_index = ["A", "B", "C", "D"].index(saved_ans)
    
    # Dynamically generate the form key so it updates properly on navigation
    with st.form(key=f"quiz_form_{st.session_state.current_q_index}"):
        
        # label_visibility="collapsed" entirely removes the "Select your answer:" text!
        choice_label = st.radio(
            "Answer", 
            ["A", "B", "C", "D"], 
            index=radio_index,
            format_func=lambda x: f"**{x})** {options[x]}", # ADDED MARKDOWN BOLDING HERE
            label_visibility="collapsed"
        )
        
        st.write("") # Extra padding
        
        # We shrink the spacer and widen the buttons
        c1, c_space, c2, c3 = st.columns([2, 3, 2, 2])
        
        with c1:
            quit_btn = st.form_submit_button("Quit Quiz", use_container_width=True)
            
        with c2:
            # Disable the Back button if we are on the very first question
            back_disabled = (st.session_state.current_q_index == 0)
            back_btn = st.form_submit_button("Back", disabled=back_disabled, use_container_width=True)
            
        with c3:
            # If we are on the last question, change "Next" to "Submit"
            is_last = (st.session_state.current_q_index == len(st.session_state.quiz_questions) - 1)
            next_text = "Submit" if is_last else "Next"
            next_btn = st.form_submit_button(next_text, type="primary", use_container_width=True)

        # --- Routing Logic ---
        if quit_btn:
            st.session_state.quiz_started = False
            st.session_state.current_screen = "dashboard"
            st.rerun()
            
        elif back_btn:
            # Save current answer, move index back 1
            st.session_state.current_answers[st.session_state.current_q_index] = choice_label
            st.session_state.current_q_index -= 1
            st.rerun()
            
        elif next_btn:
            # Save current answer
            st.session_state.current_answers[st.session_state.current_q_index] = choice_label
            if is_last:
                submit_entire_quiz()
            else:
                # Move index forward 1
                st.session_state.current_q_index += 1
                st.rerun()

def analytics_screen():
    st.markdown("<h1 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-chart-line' style='color: #C09B5A;'></i> Performance Analytics</h1>", unsafe_allow_html=True)
    
    response = supabase.table("attempts").select("is_correct, time_taken_seconds, question_id").eq("user_id", st.session_state.user_id).execute()
    data = response.data
    
    q_map = get_question_map()

    if data:
        processed = []
        slow_units = set() 
        
        for item in data:
            q_id = item.get('question_id')
            if q_id in q_map:
                unit_num = q_map[q_id]
                processed.append({"unit_num": unit_num, "correct": item['is_correct']})
                
                if item['is_correct'] == 1 and item['time_taken_seconds'] > 90:
                    slow_units.add(unit_num)
        
        if processed:
            df = pd.DataFrame(processed)
            summary_raw = df.groupby('unit_num')['correct'].mean() * 100
            
            # ==========================================
            # 🕸️ SKILL RADAR CHART (SPIDER WEB)
            # ==========================================
            st.markdown("<h3 style='color: #0B1B3D;'>Your Mastery Radar</h3>", unsafe_allow_html=True)
            
            # 1. Map all 10 units (fill with 0 if unattempted)
            all_units = [f"U{i}" for i in range(1, 11)]
            accuracies = []
            for i in range(1, 11):
                if i in summary_raw.index:
                    accuracies.append(summary_raw[i])
                else:
                    accuracies.append(0)
            
            # 2. Calculate angles for the radar
            angles = np.linspace(0, 2 * np.pi, len(all_units), endpoint=False).tolist()
            
            # 3. Close the loop to draw a full shape
            accuracies += [accuracies[0]]
            angles += [angles[0]]
            
            # 4. Plot the beautiful chart
            fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
            fig.patch.set_facecolor('#0B1B3D') # Navy background
            ax.set_facecolor('#0B1B3D')
            
            # Adjust grid and axes
            plt.xticks(angles[:-1], all_units, color='white', size=12)
            ax.set_rlabel_position(0)
            plt.yticks([20, 40, 60, 80], ["20%", "40%", "60%", "80%"], color="#A0A0A0", size=8)
            plt.ylim(0, 100)
            
            # Fill the radar
            ax.plot(angles, accuracies, color='#C09B5A', linewidth=2.5, linestyle='solid')
            ax.fill(angles, accuracies, color='#C09B5A', alpha=0.4)
            
            # Styling
            ax.grid(color='#334155', linestyle='--', linewidth=0.8)
            ax.spines['polar'].set_color('#C09B5A')
            
            st.pyplot(fig)
            st.write("---")
            
            # Feedback logic
            if slow_units:
                sorted_slow = sorted(list(slow_units))
                st.markdown(f"<div style='background-color: rgba(234, 179, 8, 0.1); border: 1px solid #eab308; padding: 14px; border-radius: 8px; color: #eab308; margin-top: 15px;'><i class='fa-solid fa-stopwatch'></i> <b>Speed Improvement Needed:</b> You have correct answers that took longer than 90 seconds in <b>Units: {', '.join(map(str, sorted_slow))}</b>. The AP exam requires faster pacing here!</div>", unsafe_allow_html=True)
        else:
            st.info("No unit data found for your attempts.")
    else:
        st.info("You haven't taken any quizzes yet! Start a quiz to see your analytics.")
        
    if st.button("← Back to Dashboard", type="primary"):
        st.session_state.current_screen = "dashboard"
        st.rerun()

def admin_dashboard_screen():
    st.markdown("<h1 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-crown' style='color: #C09B5A;'></i> Platform Administration</h1>", unsafe_allow_html=True)
    st.write("---")

    users_res = supabase.table("users").select("user_id, username").execute()
    users = {u['user_id']: u['username'] for u in users_res.data}

    attempts_res = supabase.table("attempts").select("user_id, is_correct, question_id").execute()
    
    q_map = get_question_map()
    
    student_stats = []
    for uid, uname in users.items():
        u_attempts = [a for a in attempts_res.data if a['user_id'] == uid]
        total_xp = sum(1 for a in u_attempts if a['is_correct'])
        total_q = len(u_attempts)
        accuracy = (total_xp / total_q * 100) if total_q > 0 else 0
        
        unit_acc = {}
        for a in u_attempts:
            q_id = a.get('question_id')
            if q_id in q_map:
                unit = q_map[q_id]
                if unit not in unit_acc:
                    unit_acc[unit] = {'correct': 0, 'total': 0}
                unit_acc[unit]['total'] += 1
                unit_acc[unit]['correct'] += a['is_correct']
        
        weakest_unit = "None"
        lowest_acc = 101 # Safely catches 100% accuracy students now
        for u, stats in unit_acc.items():
            acc = (stats['correct'] / stats['total']) * 100
            if acc <= lowest_acc:
                lowest_acc = acc
                weakest_unit = f"Unit {u}"
        
        student_stats.append({
            "Username": uname,
            "Total XP": total_xp,
            "Questions Answered": total_q,
            "Accuracy": f"{accuracy:.1f}%",
            "Weakest Unit": weakest_unit if total_q > 0 else "N/A"
        })
    
    st.markdown("<h3 style='text-align: center; color: #0B1B3D;'><i class='fa-solid fa-globe' style='color: #C09B5A;'></i> Global Platform Metrics</h3>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Students", len(users))
    c2.metric("Total Questions Answered", len(attempts_res.data))
    global_acc = (sum(1 for a in attempts_res.data if a['is_correct']) / len(attempts_res.data) * 100) if attempts_res.data else 0
    c3.metric("Global Average Accuracy", f"{global_acc:.1f}%")
    
    st.write("---")
    st.markdown("<h3 style='color: #0B1B3D;'><i class='fa-solid fa-users' style='color: #C09B5A;'></i> Student Roster & Leaderboard</h3>", unsafe_allow_html=True)
    
    df = pd.DataFrame(student_stats)
    if not df.empty:
        df = df.sort_values(by="Total XP", ascending=False).reset_index(drop=True)
        df.index += 1 
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No student data available yet.")

# --- 6. Screen Router & SaaS Sidebar ---
if not st.session_state.logged_in:
    login_screen()
else:
    with st.sidebar:
        st.markdown("<h2 style='text-align: center; color: white;'><i class='fa-solid fa-user-graduate' style='color: #C09B5A;'></i> Novara Profile</h2>", unsafe_allow_html=True)
        
        response = supabase.table("attempts").select("is_correct").eq("user_id", st.session_state.user_id).execute()
        total_score = sum([1 for item in response.data if item['is_correct'] == 1]) if response.data else 0
        
        st.markdown(f"<div style='text-align: center; color: #C09B5A; font-size: 18px; margin-bottom: 20px;'><b><i class='fa-solid fa-user'></i> {st.session_state.username}</b><br><i class='fa-solid fa-star'></i> Total XP: {total_score}</div>", unsafe_allow_html=True)
        
        if st.button("Home", use_container_width=True, type="primary"):
            st.session_state.current_screen = "dashboard"
            st.rerun()
            
        if st.button("Start Full Adaptive Quiz", use_container_width=True, type="primary"):
            start_quiz()
            
        if st.button("Saved Questions", use_container_width=True, type="primary"):
            st.session_state.current_screen = "vault"
            st.rerun()
            
        if st.button("View Analytics", use_container_width=True, type="primary"):
            st.session_state.current_screen = "analytics"
            st.rerun()
            
        if st.session_state.get("is_admin", False):
            st.write("---")
            if st.button("Admin Dashboard", use_container_width=True, type="primary"):
                st.session_state.current_screen = "admin_dashboard"
                st.rerun()
            
        st.write("---")
        if st.button("Log Out", use_container_width=True, type="primary"):
            st.session_state.clear()
            st.rerun()

    if st.session_state.current_screen == "dashboard":
        dashboard_screen()
    elif st.session_state.current_screen == "unit_detail":
        unit_detail_screen()
    elif st.session_state.current_screen == "quiz":
        quiz_screen()
    elif st.session_state.current_screen == "analytics":
        analytics_screen()
    elif st.session_state.current_screen == "admin_dashboard":
        admin_dashboard_screen()
    elif st.session_state.current_screen == "vault":
        vault_screen()