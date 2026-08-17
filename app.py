import streamlit as st
import pandas as pd
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
        border: 1px solid #C09B5A !important; 
    }

    /* --- 3. NATIVE MARKDOWN TABLE STYLING --- */
    .stMarkdown table {
        background-color: #0B1B3D !important;
        border: 2px solid #C09B5A !important;
        border-top: none !important;
        border-bottom-left-radius: 12px !important;
        border-bottom-right-radius: 12px !important;
        color: white !important;
        width: 100% !important;
        margin-top: -10px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    .stMarkdown th { display: none !important; }
    .stMarkdown td {
        border-bottom: 1px solid #C09B5A !important;
        border-top: none !important;
        border-right: none !important;
        border-left: none !important;
        padding: 15px !important;
        vertical-align: top !important;
        font-size: 14px !important;
    }
    .stMarkdown tr:last-child td { border-bottom: none !important; }
    .stMarkdown td:first-child {
        color: #C09B5A !important;
        font-weight: bold !important;
        width: 28% !important;
    }

    /* --- 4. SAAS SIDEBAR STYLING --- */
    [data-testid="stSidebar"] {
        background-color: #0B1B3D !important;
        border-right: 2px solid #C09B5A !important;
    }
    [data-testid="stSidebar"] hr {
        border-bottom: 1px solid #C09B5A !important;
    }

    /* --- 5. PREMIUM QUIZ OPTION CARDS --- */
    div[role="radiogroup"] {
        gap: 15px !important; 
    }
    div[role="radiogroup"] > label {
        background-color: #FFFFFF !important;
        border: 2px solid #E2E8F0 !important; 
        border-radius: 12px !important;
        padding: 15px 20px !important; 
        box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
        transition: all 0.2s ease-in-out !important;
        cursor: pointer !important;
    }
    div[role="radiogroup"] > label:hover {
        border: 2px solid #C09B5A !important; 
        background-color: #F8FAFC !important; 
        transform: translateY(-3px) !important; 
        box-shadow: 0 8px 12px rgba(0,0,0,0.1) !important; 
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

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 6: Integration & Accumulation — Core Definitions</h3>
</div>

| | |
|---|---|
| **6.1**<br>Accumulation of Change | *Definition:* rate of change accumulated over an interval gives total change. When a rate is positive, the quantity grows; when negative, it decreases.<br>*Graphical Meaning:* the net result is the signed accumulation — positive regions add, negative regions subtract; the area under a rate curve is "collected change," the central idea of integration. |
| **6.2**<br>Riemann Sum Approximations | *Definition:* dividing an interval into $n$ equal subintervals of width $\Delta x$ and evaluating $f$ at a sample point in each gives a Riemann sum approximation of the area under the curve.<br>*Graphical Meaning:* Left/Right sums use endpoints; the Midpoint sum samples the center of each strip; the Trapezoidal sum averages left and right heights, modeling the curve with straight-line segments rather than rectangles. More subintervals always improves accuracy. |
| **6.3**<br>From Sums to the Definite Integral | *Definition:* the definite integral $\int_a^b f(x)\,dx$ is defined as the limit of Riemann sums as $n\to\infty$ (strip width $\to0$).<br>*Graphical Meaning:* it represents the signed area between $y=f(x)$ and the $x$-axis on $[a,b]$. Sigma ($\Sigma$) notation compactly expresses these sums; key integral properties — linearity, reversal of limits, splitting — follow directly from the limit definition. |
| **6.4**<br>Fundamental Theorem of Calculus | *Definition (Part 1):* differentiation and integration are inverse operations. If $F(x)=\int_a^x f(t)\,dt$, then $F'(x)=f(x)$ — the derivative of an accumulation function recovers the integrand; with the Chain Rule, an upper limit of $g(x)$ introduces a factor of $g'(x)$.<br>*Definition (Part 2):* a definite integral can be evaluated exactly using any antiderivative $F$ of $f$: simply compute $F(b)-F(a)$, connecting the area concept to algebraic antidifferentiation. |
| **6.5**<br>Behavior of Accumulation Functions | *Definition:* because $F'=f$, all information about the shape of $F$ comes from reading the graph of $f$.<br>*Graphical Meaning:* where $f>0$, $F$ rises; where $f<0$, $F$ falls; where $f$ crosses zero and changes sign, $F$ has a local extremum. Concavity of $F$ is governed by whether $f$ is increasing or decreasing; a local max or min of $f$ corresponds to an inflection point of $F$. |
| **6.6**<br>Applying Properties of Definite Integrals | *Definition:* the average value of a continuous function $f$ on $[a,b]$ is the integral divided by the length of the interval — the "height" a constant function would need to enclose the same area.<br>*Graphical Meaning:* the Mean Value Theorem for Integrals guarantees at least one point $c$ where $f$ actually equals this average; comparison and bound properties let us estimate integrals without computing them exactly. |
| **6.7**<br>FTC and Definite Integrals (Net Change) | *Definition:* the Net Change Theorem states that integrating a rate of change over $[a,b]$ gives the total (net) change in the quantity.<br>*Graphical Meaning:* for motion, integrating velocity gives displacement (net change in position, possibly zero if the object returns); integrating the absolute value of velocity gives total distance traveled, which is always non-negative. |
| **6.8**<br>Basic Antiderivatives & Indefinite Integrals | *Definition:* an indefinite integral $\int f(x)\,dx=F(x)+C$ represents a family of antiderivatives, differing only by the constant $C$.<br>*Graphical Meaning:* the Power Rule reverses differentiation of $x^n$; other fundamental antiderivatives correspond to the standard derivative rules for exponential, logarithmic, and trigonometric functions. The constant $C$ always appears because differentiation loses constant information. |
| **6.9**<br>$u$-Substitution | *Definition:* $u$-substitution is the integration counterpart of the Chain Rule; it applies when the integrand contains a composite function whose inner derivative also appears as a factor.<br>*Graphical Meaning:* the substitution $u=g(x)$ converts a complex integral into a simpler standard form; for definite integrals, limits must be converted to $u$-values so the integral remains in one variable throughout. |
| **6.10**<br>Long Division & Completing the Square | *Definition:* long division simplifies improper rational functions (numerator degree $\geq$ denominator degree) before integrating, converting them into a polynomial plus a proper fraction.<br>*Graphical Meaning:* completing the square restructures a quadratic expression into a shifted square form, enabling recognition of arctan and arcsin antiderivative patterns that would otherwise be hidden. |
| **6.11 (BC)**<br>Integration by Parts | *Definition:* the product-rule analog for integrals; it shifts the "difficulty" from one factor to the other: $\int u\,dv=uv-\int v\,du$.<br>*Graphical Meaning:* the goal is to choose $u$ and $dv$ so that $\int v\,du$ is easier; the LIATE mnemonic guides that choice. Sometimes the technique must be applied twice, or the original integral reappears on the right — in that case, solve algebraically for the integral. |
| **6.12 (BC)**<br>Linear Partial Fractions | *Definition:* a rational function whose denominator factors into distinct linear terms can be decomposed into a sum of simpler fractions, each with a single linear denominator.<br>*Graphical Meaning:* each piece integrates to a logarithm; this technique extends to repeated linear factors by including additional terms with increasing powers in the denominator. |
| **6.13 (BC)**<br>Improper Integrals | *Definition:* an integral is improper when either bound is infinite or the integrand has a vertical asymptote inside the interval; such integrals are defined as limits: replace the problematic bound with a variable, integrate normally, then take the limit.<br>*Graphical Meaning:* if the limit exists and is finite, the integral converges; otherwise it diverges. A divergent integral represents an "infinitely large" area. |
| **6.14**<br>Selecting Antidifferentiation Techniques | *Definition:* choosing the right integration method requires pattern recognition — looking at the structure of the integrand first.<br>*Graphical Meaning:* a composite with its inner derivative present signals $u$-sub; a product of unrelated functions suggests Integration by Parts; an improper rational calls for long division; a quadratic denominator with no factorable roots calls for completing the square; a factorable denominator calls for partial fractions. When in doubt, simplify algebraically before integrating. |
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

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 7: Differential Equations — Core Definitions</h3>
</div>

| | |
|---|---|
| **7.1**<br>Modeling with Differential Equations | *Definition:* a differential equation expresses a relationship between a function and its rate of change, making it the natural language for describing how quantities evolve over time or space.<br>*Graphical Meaning:* rather than giving the value of a quantity directly, a DE describes the rule by which it changes. Translating a real-world scenario into a DE is the first modeling step: identify what is changing, what drives that change, and whether the rate depends on time, the quantity itself, or some external factor. Common models include proportional growth, proportional decay, and temperature change toward an ambient value. |
| **7.2**<br>Verifying Solutions | *Definition:* verifying that a proposed function is a solution to a DE does not require solving the equation from scratch — it requires only substitution and differentiation.<br>*Graphical Meaning:* you differentiate the candidate function, substitute both it and its derivative into the DE, and check whether the equation holds as an identity. If it does, the function is a valid solution. When an initial condition is provided, an additional check confirms that the function passes through the specified point, confirming membership in the family of solutions without requiring re-derivation. |
| **7.3**<br>Sketching Slope Fields | *Definition:* a slope field is a visual portrait of a differential equation: at every point on the plane, a short line segment is drawn with slope equal to the value $\frac{dy}{dx}$ given by the DE at that point.<br>*Graphical Meaning:* slope fields make it possible to see the behavior of all solutions simultaneously without solving the equation algebraically. Points where the slope is zero produce horizontal segments, and regions where the slope is large produce steeply angled segments. Recognizing patterns — such as slopes depending only on $y$, only on $x$, or on both — helps you sketch and interpret slope fields efficiently. |
| **7.4**<br>Reasoning Using Slope Fields | *Definition:* solution curves drawn through a slope field must always be tangent to the field's segments, so the field itself constrains what solutions look like.<br>*Graphical Meaning:* different starting points (initial conditions) trace different curves through the same field, illustrating how a family of solutions fills the plane. Equilibrium solutions appear as horizontal lines where the slope is zero everywhere along that line; they divide the plane into regions of increasing or decreasing behavior. A stable equilibrium attracts nearby curves, while an unstable one repels them — a fact visible directly from the direction of surrounding segments. |
| **7.5 (BC)**<br>Euler's Method | *Definition:* Euler's Method is a numerical algorithm for approximating the solution to a differential equation when an exact algebraic solution is unavailable or unnecessary.<br>*Graphical Meaning:* starting at a known initial point, the method takes a small step in the direction indicated by the slope field, lands at a new point, recomputes the slope there, and repeats. Each step uses a linear (tangent-line) approximation, so accuracy depends critically on step size: smaller steps produce better approximations at the cost of more computation. The curvature of the true solution determines whether Euler's method over- or underestimates — concave-up curves are underestimated, concave-down curves are overestimated. |
| **7.6**<br>Separation of Variables | *Definition:* separation of variables is the most fundamental algebraic technique for solving differential equations in which the two variables can be algebraically isolated on opposite sides of the equation.<br>*Graphical Meaning:* once separated, each side is integrated independently, yielding a relationship between the variables that implicitly or explicitly defines the solution. The arbitrary constant $C$ that arises from integration encodes the entire family of solutions — one curve for each value of $C$. Care must be taken to check for constant (equilibrium) solutions that may be lost when dividing by an expression that could equal zero. |
| **7.7**<br>Particular Solutions Using Initial Conditions | *Definition:* a general solution to a differential equation contains an arbitrary constant and represents an entire family of curves. An initial condition — a specific known value of the dependent variable at a particular input — pins down one unique curve from that family, producing a particular solution.<br>*Graphical Meaning:* the procedure is to substitute the initial condition into the general solution, solve for the constant, and rewrite the solution with that specific value. The particular solution satisfies both the differential equation at every point and the initial condition at the specified point. |
| **7.8**<br>Exponential Models | *Definition:* when a quantity changes at a rate directly proportional to its current value, the governing differential equation is $\frac{dy}{dt}=ky$, and its solution is an exponential function.<br>*Graphical Meaning:* if $k$ is positive the quantity grows without bound; if $k$ is negative it decays toward zero. This model describes radioactive decay, population growth, continuous compound interest, and Newton's Law of Cooling (where the rate is proportional to the difference between current and ambient temperature). The constant $k$ and the initial value together uniquely determine the particular exponential function that models the situation. |
| **7.9 (BC)**<br>Logistic Models | *Definition:* the logistic model refines pure exponential growth by introducing a carrying capacity $L$ — an upper limit on how large the population or quantity can grow.<br>*Graphical Meaning:* the growth rate is fastest when the quantity is at half the carrying capacity and slows to zero as the quantity approaches $L$ from below. The solution is an S-shaped (sigmoidal) curve: initially nearly exponential, then decelerating, and finally leveling off asymptotically at $L$. The inflection point at $P=L/2$ marks the transition from increasing to decreasing growth rate, and the second derivative can confirm concavity above and below that threshold. |
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

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 8: Applications of Integration — Core Definitions</h3>
</div>

| | |
|---|---|
| **8.1**<br>Average Value of a Function | *Definition:* the average value of a continuous function on a closed interval is the integral of the function divided by the length of the interval — the single constant height that would produce the same net area as the curve.<br>*Graphical Meaning:* the Mean Value Theorem for Integrals guarantees that a continuous function must actually reach this average value at least once on the interior of the interval. This is the continuous analogue of averaging a finite list of numbers: summing and dividing by the count. Average value is widely used to describe mean temperature, mean velocity, or mean concentration over a time period. |
| **8.2**<br>Position, Velocity, Acceleration | *Definition:* velocity is the antiderivative of acceleration, and position is the antiderivative of velocity, so integrating a rate of change recovers the quantity it describes.<br>*Graphical Meaning:* integrating velocity over a time interval gives displacement — the net signed change in position, which can be zero even if the object moved. To find total distance traveled, the absolute value of velocity must be integrated, ensuring all motion is counted positively regardless of direction. An object speeds up when velocity and acceleration share the same sign and slows down when they have opposite signs. |
| **8.3**<br>Accumulation Functions | *Definition:* when a rate function describes how quickly a quantity is changing — water flowing, people entering, fuel burning — integrating that rate over a time interval gives the total net change in the quantity.<br>*Graphical Meaning:* adding this net change to the initial amount present at any later time gives the total amount at that time. The units of the integral are always the product of the rate's units and time's units, which keeps the interpretation grounded. Distinguishing net change (signed) from total accumulation (using absolute value) is crucial when the rate changes sign during the interval. |
| **8.4**<br>Area Between Curves (with respect to $x$) | *Definition:* when two curves bound a region on the plane, the area of that region is found by integrating the difference between the top curve and the bottom curve over the interval where they overlap horizontally.<br>*Graphical Meaning:* finding the intersection points of the two curves is the first step, as these determine the limits of integration. The integrand is always top minus bottom, which ensures a non-negative result. Sketching the region before integrating is strongly recommended to avoid sign errors. |
| **8.5**<br>Area Between Curves (with respect to $y$) | *Definition:* sometimes two curves are more naturally described as functions of $y$ rather than $x$, or the region is easier to analyze by integrating horizontally.<br>*Graphical Meaning:* in this case the area is computed as the integral of the rightmost curve minus the leftmost curve, with limits determined by the $y$-coordinates of the intersection points. This approach avoids the need to split the region when the top-bottom relationship changes — a common problem when integrating with respect to $x$. Choosing the right variable of integration can significantly simplify the calculation. |
| **8.6**<br>Area Between Curves: More Than Two Intersections | *Definition:* when two curves cross more than twice, the region between them is divided into sub-regions where the functions alternate which one is on top.<br>*Graphical Meaning:* each sub-region must be integrated separately, because integrating across a crossing point without splitting would allow positive and negative contributions to cancel, giving a smaller value than the true geometric area. Finding all intersection points is therefore the critical first step. The absolute value of the difference can also be used, provided the region boundaries are set correctly. |
| **8.7**<br>Volumes: Cross Sections with Squares and Rectangles | *Definition:* a solid can be built by stacking cross-sectional slices perpendicular to an axis, each with a known area.<br>*Graphical Meaning:* when the base of the solid is a region in the $xy$-plane and each cross section is a square or rectangle, the side length of the cross section equals the width of the base region at each $x$-value. Integrating the area function of those cross sections over the interval gives the total volume. This technique does not involve rotation — the solid grows outward from the base into the third dimension. |
| **8.8**<br>Volumes: Cross Sections with Triangles and Semicircles | *Definition:* the same cross-section principle applies when slices are equilateral triangles, right isosceles triangles, or semicircles — only the formula for the cross-sectional area changes.<br>*Graphical Meaning:* in each case, the key dimension of the shape (side length or diameter) is tied to the width of the base region at each $x$-value. Equilateral triangles introduce a $\frac{\sqrt{3}}{4}$ factor; semicircles introduce $\frac{\pi}{8}$ when the diameter equals the base width. Correctly identifying which dimension of the shape corresponds to the base-region width is the most important step. |
| **8.9**<br>Disc Method: Revolving Around the $x$- or $y$-Axis | *Definition:* when a region bounded by a single curve and an axis is rotated about that axis, the resulting solid is made of circular discs stacked along the axis.<br>*Graphical Meaning:* each disc has a radius equal to the function value at that point and thickness equal to an infinitesimal step along the axis. The volume of each disc is $\pi r^2$ times its thickness, and integrating these over the full interval gives the total volume. The disc method applies whenever there is no hole in the solid — the region touches the axis of revolution. |
| **8.10**<br>Disc Method: Revolving Around Other Axes | *Definition:* when the axis of revolution is not the coordinate axis but a horizontal or vertical line such as $y=k$ or $x=k$, the radius of each disc is the perpendicular distance from the curve to that line rather than to the origin.<br>*Graphical Meaning:* the formula is otherwise identical to the standard disc method — integrate $\pi$ times the squared radius. Carefully determining whether the curve lies above or below (or left or right of) the axis of revolution is essential for computing the correct distance. |
| **8.11**<br>Washer Method: Revolving Around the $x$- or $y$-Axis | *Definition:* when two curves bound a region and that region is rotated around a coordinate axis, the solid has a hole through its center, making each cross-section a washer rather than a full disc.<br>*Graphical Meaning:* the volume is the integral of the outer disc area minus the inner disc area — outer radius squared minus inner radius squared, multiplied by $\pi$. The outer radius is the distance from the axis to the farther curve, and the inner radius is the distance to the closer curve. The washer method reduces to the disc method when the inner radius is zero. |
| **8.12**<br>Washer Method: Revolving Around Other Axes | *Definition:* the washer method extends naturally to any horizontal or vertical axis of revolution, not just the coordinate axes.<br>*Graphical Meaning:* when the axis is the line $y=k$ or $x=k$, the outer and inner radii are both measured as perpendicular distances from the respective curves to that line. The key challenge is determining which curve is farther from the axis — this depends on whether the axis lies below, above, left, or right of the region. Setting up the region relative to the axis correctly requires a careful sketch of the region before writing any integral. |
| **8.13 (BC)**<br>Arc Length of a Smooth Planar Curve | *Definition:* the arc length of a smooth curve is computed by summing the lengths of infinitely many infinitesimal straight-line segments that approximate the curve.<br>*Graphical Meaning:* each segment has length given by the Pythagorean theorem applied to the horizontal and vertical components of movement, which produces a square-root integrand involving the derivative. For a curve expressed as $y=f(x)$, the formula integrates $\sqrt{1+(f')^2}$ over the relevant interval; for parametric curves, both $dx/dt$ and $dy/dt$ appear under the radical. Arc length integrals often cannot be evaluated in closed form and may require a calculator. |
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

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 9: Parametric, Polar & Vectors — Core Definitions</h3>
</div>

| | |
|---|---|
| **9.1**<br>Defining & Differentiating Parametric Equations | *Definition:* parametric equations describe a curve by expressing both $x$ and $y$ as separate functions of a third variable called the parameter, usually $t$. This allows the curve to loop, reverse, and describe motion over time in ways a single function $y=f(x)$ cannot.<br>*Graphical Meaning:* the slope of the curve at any point is found by dividing $dy/dt$ by $dx/dt$, which applies the chain rule to link the rate of change in $y$ to the rate of change in $x$. Horizontal and vertical tangents are identified by where the numerator or denominator of this fraction equals zero, respectively. |
| **9.2**<br>Second Derivatives of Parametric Equations | *Definition:* the second derivative of a parametric curve measures how the slope of the curve itself is changing, that is, its concavity.<br>*Graphical Meaning:* because the first derivative $dy/dx$ is still a function of the parameter, its own rate of change with respect to $t$ must be divided by $dx/dt$ again to convert back to a derivative with respect to $x$. A positive second derivative indicates the curve is concave up at that point, and a negative value indicates concave down. This process is a direct extension of the chain rule applied twice and requires careful bookkeeping of which variable is playing the role of the independent variable. |
| **9.3**<br>Arc Length of Parametric Curves | *Definition:* the arc length of a parametric curve is found by integrating the speed of the moving point over the time interval.<br>*Graphical Meaning:* speed at each instant is computed using the Pythagorean theorem on the horizontal and vertical rates of change, producing a square-root expression under the integral. This gives the total path length traced by the curve regardless of direction, so a curve that retraces itself counts that portion twice. Distance traveled always equals the arc length, while displacement measures the net change in position from start to finish. |
| **9.4**<br>Defining & Differentiating Vector-Valued Functions | *Definition:* a vector-valued function packages the $x$- and $y$-components of a moving object's position into a single vector, making it easier to reason about direction and magnitude simultaneously.<br>*Graphical Meaning:* differentiating component-by-component gives the velocity vector, which points in the direction of motion and has magnitude equal to the object's speed. The second derivative gives the acceleration vector, which describes how velocity is changing over time. The velocity vector being zero at an instant means the object is momentarily at rest; the direction of the velocity vector at any instant gives the object's heading. |
| **9.5**<br>Integrating Vector-Valued Functions | *Definition:* integration of a vector-valued function is performed component-by-component: each component is integrated separately, and a constant vector of integration is added.<br>*Graphical Meaning:* when given a velocity vector and an initial position, integrating the velocity vector recovers the position vector, with the constant of integration determined by the initial condition. Definite integration of a velocity vector gives the displacement vector — the net change in position, not the total distance traveled. This approach mirrors single-variable calculus but extended into two dimensions simultaneously. |
| **9.6**<br>Motion Problems Using Parametric & Vector Functions | *Definition:* analyzing motion in two dimensions requires tracking both horizontal and vertical components of position, velocity, and acceleration simultaneously.<br>*Graphical Meaning:* the object moves right or left based on the sign of $x'(t)$, and up or down based on the sign of $y'(t)$; it is at rest only when both components of velocity are zero at the same time. Total distance traveled is found by integrating speed — the magnitude of the velocity vector — over the time interval, which always yields a non-negative result. This framework unifies parametric equations and vector-valued functions as two equivalent languages for describing the same two-dimensional motion. |
| **9.7**<br>Polar Coordinates & Differentiation | *Definition:* polar coordinates locate a point using its distance $r$ from the origin and an angle $\theta$ measured from the positive $x$-axis, offering a natural system for curves with rotational symmetry.<br>*Graphical Meaning:* converting between polar and rectangular form uses the standard trigonometric relationships, and many curves that require complex equations in rectangular form — like rose curves and cardioids — have elegant polar equations. The slope of a polar curve at a point is found by converting the curve to parametric form (with $\theta$ as the parameter) and applying the parametric derivative formula. Horizontal and vertical tangents are found by setting the resulting numerator or denominator to zero, respectively. |
| **9.8**<br>Area of a Polar Region | *Definition:* the area enclosed by a polar curve is computed by integrating one-half of $r^2$ with respect to $\theta$ over the angular interval that sweeps out the region.<br>*Graphical Meaning:* this formula arises from dividing the region into infinitely thin sectors — like pie slices — each with area approximately $\frac{1}{2}r^2\Delta\theta$. Identifying the correct angular limits is essential: they correspond to the angles at which the curve begins and ends the region of interest. For symmetric curves such as rose petals, it is often efficient to compute the area of one petal and multiply by the number of petals. |
| **9.9**<br>Area Between Two Polar Curves | *Definition:* the area of the region between two polar curves is the integral of one-half times the difference of the squared radii — outer curve squared minus inner curve squared — over the angle interval where the region lies.<br>*Graphical Meaning:* finding the intersection points requires setting the two radius functions equal and also checking the pole separately, since two curves can both pass through the origin at different angles. Sketching both curves before setting up the integral is strongly recommended, as visual inspection is the most reliable way to determine which curve is farther from the origin on the relevant interval. Care must be taken when the relative positions of the two curves switch within the integration interval. |
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

<br><br>

<div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-bottom: none; border-top-left-radius: 12px; border-top-right-radius: 12px; padding: 15px; text-align: center; color: #C09B5A;">
    <h3 style="margin: 0; color: #C09B5A;">Unit 10: Infinite Sequences & Series — Core Definitions</h3>
</div>

| | |
|---|---|
| **10.1**<br>Convergent & Divergent Infinite Series | *Definition:* an infinite series is the sum of infinitely many terms, defined formally as the limit of its sequence of partial sums. If that limit exists and is a finite number, the series converges to that value; if the limit is infinite or fails to exist, the series diverges.<br>*Graphical Meaning:* telescoping series are a special case in which consecutive terms cancel, making the partial sums easy to evaluate directly. Understanding convergence versus divergence is the foundational question of this entire unit — every subsequent test is a tool for answering it. |
| **10.2**<br>Geometric Series | *Definition:* a geometric series has a constant ratio between consecutive terms, making it one of the few infinite series with a simple closed-form sum.<br>*Graphical Meaning:* it converges if and only if the absolute value of the common ratio is strictly less than one, and in that case the sum equals the first term divided by one minus the ratio. When the ratio is one or greater in absolute value, the terms do not shrink to zero and the series diverges. The geometric series formula is also the engine behind representing rational functions as power series. |
| **10.3**<br>The $n$th Term Test for Divergence | *Definition:* the $n$th term test states that if the individual terms of a series do not approach zero, the series cannot possibly converge.<br>*Graphical Meaning:* it is a quick first check: if the general term tends to any nonzero limit or oscillates, divergence is immediate. Crucially, the test cannot confirm convergence — terms approaching zero is a necessary condition for convergence but not a sufficient one. The harmonic series is the classic counterexample: its terms go to zero, yet the series diverges. |
| **10.4**<br>Integral Test for Convergence | *Definition:* the integral test connects the convergence of a series to the convergence of a related improper integral, exploiting the idea that the series can be viewed as a Riemann sum approximation of the integral.<br>*Graphical Meaning:* for the test to apply, the corresponding function must be continuous, positive, and decreasing on the relevant interval. If the improper integral converges, so does the series; if it diverges, so does the series. The actual value of the integral is not the sum of the series — the test only determines whether a finite sum exists. |
| **10.5**<br>Harmonic Series and $p$-Series | *Definition:* a $p$-series takes the form of the sum of one over $n$ raised to a fixed power $p$. The single number $p$ completely determines the outcome: the series converges when $p$ is greater than one and diverges when $p$ is one or less.<br>*Graphical Meaning:* the harmonic series ($p=1$) is the boundary case and is one of the most important divergent series in calculus — its divergence is surprising because the terms shrink to zero. The $p$-series is frequently used as the comparison benchmark when applying the direct or limit comparison tests. |
| **10.6**<br>Comparison Tests for Convergence | *Definition:* comparison tests determine convergence by sandwiching an unknown series between two series whose behavior is already known.<br>*Graphical Meaning:* the direct comparison test requires a clean inequality between terms, while the limit comparison test only requires that the ratio of corresponding terms approaches a finite positive number. Both tests work exclusively on series with non-negative terms. Choosing the right comparison series — usually a $p$-series or geometric series — is the key skill, and it typically involves stripping the dominant terms from a rational expression. |
| **10.7**<br>Alternating Series Test | *Definition:* an alternating series has terms that switch sign with every step, so positive and negative contributions partially cancel each other.<br>*Graphical Meaning:* the alternating series test guarantees convergence when the magnitudes of the terms are decreasing and tending to zero — intuitively, each correction overshoots by less than the previous one, so the partial sums home in on a limiting value. The test applies to any series of the form $\sum(-1)^n b_n$ or $\sum(-1)^{n+1}b_n$ with $b_n>0$. It does not say anything about whether the sum of the absolute values converges. |
| **10.8**<br>Ratio Test for Convergence | *Definition:* the ratio test examines how consecutive terms relate to each other: if the ratio of successive absolute values approaches a limit less than one, the terms shrink fast enough for the series to converge; if the limit exceeds one, the series diverges.<br>*Graphical Meaning:* a limiting ratio of exactly one leaves the question open and requires a different test. The ratio test is especially powerful for series involving factorials or exponentials because the ratio telescopes dramatically when those expressions appear in numerator and denominator. It is the natural first choice when a series is defined by a recursive-looking or factorial-containing formula. |
| **10.9**<br>Absolute and Conditional Convergence | *Definition:* a series converges absolutely if the series formed by taking the absolute value of every term also converges; absolute convergence is a stronger property that implies ordinary convergence.<br>*Graphical Meaning:* a series is conditionally convergent if it converges in its original signed form but the absolute-value series diverges — the cancellation of positive and negative terms is doing real work. The alternating harmonic series is the standard example of conditional convergence. Absolute convergence is preferable because it is more robust: absolutely convergent series can be rearranged freely without changing their sum, while conditionally convergent series cannot. |
| **10.10**<br>Alternating Series Error Bound | *Definition:* when a convergent alternating series is approximated by a partial sum, the error is guaranteed to be no larger than the absolute value of the first term that was left out.<br>*Graphical Meaning:* this bound arises because each successive term corrects the previous overshoot by a smaller amount, so the true sum is always trapped between two consecutive partial sums. The sign of the first omitted term tells you whether the partial sum is an overestimate or an underestimate. This makes alternating series especially practical for numerical approximation, since the error can be controlled simply by including enough terms. |
| **10.11**<br>Taylor Polynomial Approximations | *Definition:* a Taylor polynomial approximates a function near a center point by matching the function's value and as many of its derivatives as the degree allows at that point.<br>*Graphical Meaning:* the higher the degree, the more accurately the polynomial tracks the function in a neighborhood of the center. A Maclaurin polynomial is the special case centered at zero. Taylor polynomials are the bridge between the algebraic world of polynomials and the analytic world of transcendental functions, and they underlie numerical methods, physics approximations, and the derivation of full Taylor series. |
| **10.12**<br>Lagrange Error Bound | *Definition:* the Lagrange error bound provides a guaranteed upper limit on how far a Taylor polynomial's output can stray from the true function value at a given point.<br>*Graphical Meaning:* it depends on the maximum size of the next derivative (one order beyond the polynomial's degree) on the interval between the center and the evaluation point, as well as the distance of that point from the center. A larger bound does not mean the error is that large — it is a worst-case guarantee. Finding a tight bound for the next derivative is usually the most challenging part of applying this theorem. |
| **10.13**<br>Radius and Interval of Convergence | *Definition:* a power series converges for values of $x$ within a certain distance $R$ of its center — this distance is the radius of convergence.<br>*Graphical Meaning:* inside the radius the series converges absolutely; outside it diverges; at the endpoints the behavior must be checked case by case using other convergence tests. The ratio test is the standard method for finding $R$. The resulting interval of convergence may be open, closed, or half-open at each endpoint, and fully specifying it requires testing both endpoints individually. |
| **10.14**<br>Taylor and Maclaurin Series | *Definition:* a Taylor series is an infinite polynomial that represents a function exactly — not just approximately — within its interval of convergence. It is constructed by computing all derivatives of the function at the center point and using them as coefficients in a specific pattern.<br>*Graphical Meaning:* a Maclaurin series is the Taylor series centered at zero, and memorizing the standard ones for $e^x$, $\sin x$, $\cos x$, and $\frac{1}{1-x}$ is essential. These series allow transcendental functions to be manipulated algebraically, integrated, differentiated, and used for approximation with controlled error. |
| **10.15**<br>Representing Functions as Power Series | *Definition:* known power series can be transformed into series for new functions through substitution, differentiation, or integration — avoiding the need to compute all derivatives from scratch.<br>*Graphical Meaning:* substituting an expression for $x$ in the geometric series formula is the most common technique, instantly producing series for functions like $\frac{1}{1+x^2}$. Differentiating or integrating a power series term by term produces the series for the derivative or antiderivative of the original function, and the radius of convergence is preserved (though endpoints may change). This approach connects integration to series and makes otherwise intractable antiderivatives — such as $e^{-x^2}$ — expressible in series form. |
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

# --- 4. Core Application Logic ---
def start_quiz(unit=None):
    if unit:
        response = supabase.table("questions").select("*").eq("unit_number", unit).execute()
        questions = response.data
        
        # ADD THESE TWO LINES TO SHUFFLE THE UNIT QUESTIONS!
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

def submit_answer(selected_option):
    end_time = time.time()
    time_taken = int(end_time - st.session_state.q_start_time)
    
    current_q = st.session_state.quiz_questions[st.session_state.current_q_index]
    is_correct = 1 if selected_option == current_q['correct_option'] else 0
    
    if is_correct:
        st.session_state.quiz_score += 1

    st.session_state.user_answers.append({
        'question_id': current_q['question_id'],
        'question': current_q['question_text'],
        'selected': selected_option,
        'selected_text': current_q[f"option_{selected_option.lower()}"],
        'correct': current_q['correct_option'],
        'correct_text': current_q[f"option_{current_q['correct_option'].lower()}"],
        'is_correct': is_correct
    })

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
        st.toast("🗑️ Question removed from your Vault!", icon="✅")
    except Exception:
        st.toast("Error removing question.", icon="❌")

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
            # 1. Check if the user is currently locked out
            if time.time() < st.session_state.lockout_until:
                remaining_seconds = int(st.session_state.lockout_until - time.time())
                st.error(f"🔒 Account temporarily locked due to too many failed attempts. Try again in {remaining_seconds} seconds.")
            
            elif login_email and login_password:
                try:
                    user_record = supabase.table("users").select("*").eq("email", login_email).execute()
                    
                    if user_record.data:
                        user = user_record.data[0]
                        # Verify the bcrypt password securely
                        if bcrypt.checkpw(login_password.encode('utf-8'), user['password_hash'].encode('utf-8')):
                            # SUCCESS: Reset the strikeout counters!
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
                            # FAILED PASSWORD
                            st.session_state.failed_attempts += 1
                            if st.session_state.failed_attempts >= 5:
                                st.session_state.lockout_until = time.time() + 300 # 5 minute lockout
                                st.error("🔒 Too many failed attempts. You are locked out for 5 minutes.")
                            else:
                                attempts_left = 5 - st.session_state.failed_attempts
                                st.error(f"❌ Invalid email or password. ({attempts_left} attempts remaining)")
                    else:
                        # FAILED EMAIL (We treat it as a failed attempt to avoid giving hackers clues)
                        st.session_state.failed_attempts += 1
                        if st.session_state.failed_attempts >= 5:
                            st.session_state.lockout_until = time.time() + 300
                            st.error("🔒 Too many failed attempts. You are locked out for 5 minutes.")
                        else:
                            attempts_left = 5 - st.session_state.failed_attempts
                            st.error(f"❌ Invalid email or password. ({attempts_left} attempts remaining)")
                except Exception as e:
                    st.error(f"❌ Error during login: {e}")
            else:
                st.warning("⚠️ Please fill in both fields.")

    with tab2:
        reg_username = st.text_input("Full Name / Username", key="reg_username")
        reg_email = st.text_input("Email Address", key="reg_email")
        reg_password = st.text_input("Password", type="password", key="reg_password")
        
        if st.button("Create Account", type="primary"):
            if reg_username and reg_email and reg_password:
                
                # --- NEW: STRICT REGEX EMAIL FORMAT VALIDATION ---
                email_pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
                if not re.match(email_pattern, reg_email):
                    st.warning("⚠️ Please enter a valid email address format (e.g., student@example.com).")
                elif len(reg_password) < 8:
                    st.warning("⚠️ Password must be at least 8 characters long.")
                else:
                    try:
                        # 1. Check if email already exists
                        email_check = supabase.table("users").select("*").eq("email", reg_email).execute()
                        
                        # 2. Check if username already exists
                        username_check = supabase.table("users").select("*").eq("username", reg_username).execute()
                        
                        if email_check.data:
                            st.error("❌ Registration failed: An account with this email already exists.")
                        elif username_check.data:
                            st.error("❌ Registration failed: That username is already taken. Please choose another one.")
                        else:
                            # Securely hash the password using bcrypt
                            salt = bcrypt.gensalt()
                            hashed_pw = bcrypt.hashpw(reg_password.encode('utf-8'), salt).decode('utf-8')
                            
                            supabase.table("users").insert({
                                "username": reg_username,
                                "email": reg_email,
                                "password_hash": hashed_pw 
                            }).execute()
                            st.success("✅ Account created successfully! You can now Log In.")
                    except Exception as e:
                        st.error(f"❌ Registration failed: {e}")
            else:
                st.warning("⚠️ Please fill in all fields.")

def dashboard_screen():
    st.markdown(f"<h1 style='text-align: center; color: #0B1B3D;'>Welcome, {st.session_state.username}!</h1>", unsafe_allow_html=True)
    
    # --- 1. ⏱️ AP EXAM COUNTDOWN & STREAK TRACKER ---
    tz = ZoneInfo("Asia/Tashkent")
    exam_datetime = datetime(2027, 5, 10, 8, 0, 0, tzinfo=tz) 
    now = datetime.now(tz)
    total_seconds = int((exam_datetime - now).total_seconds())
    
    today = date.today()
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

    # --- 🚨 FIX 2: Live JavaScript Countdown Widget ---
    components.html(
    f"""
    <div style="display: flex; justify-content: space-between; font-family: sans-serif; margin-bottom: 5px; margin-top: 15px;">
        <div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-radius: 12px; padding: 18px; width: 48%; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); box-sizing: border-box;">
            <h4 style="color: white; margin-top: 0; margin-bottom: 8px; font-size: 15px;">⏱️ AP Calc Exam</h4>
            <h1 id="countdown" style="color: #C09B5A; margin: 0; font-size: 24px;"></h1>
            <p style="color: white; margin: 8px 0 0 0; font-size: 13px;">Time Left (May 10)</p>
        </div>
        <div style="background-color: #0B1B3D; border: 2px solid #C09B5A; border-radius: 12px; padding: 18px; width: 48%; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); box-sizing: border-box;">
            <h4 style="color: white; margin-top: 0; margin-bottom: 8px; font-size: 15px;">🔥 Daily Streak</h4>
            <h1 style="color: #C09B5A; margin: 0; font-size: 34px;">{streak}</h1>
            <p style="color: white; margin: 8px 0 0 0; font-size: 13px;">Consecutive Days</p>
        </div>
    </div>
    <script>
        let total_seconds = {total_seconds};
        const countdown_div = document.getElementById("countdown");

        function updateTimer() {{
            if (total_seconds <= 0) {{
                countdown_div.innerText = "🎉 Exam Day!";
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
    height=170
    )
    
    # --- 2. 🏆 TROPHY CASE (MASTERY BADGES) ---
    st.markdown("<h3 style='text-align: center; color: #0B1B3D; margin-bottom: 15px;'>🏆 Unit Mastery Trophy Case</h3>", unsafe_allow_html=True)
    
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
            
            icon = "&#x1F3C6;" if is_mastered else "&#x1F512;"
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
    
    with st.expander("📚 View Unit Formulas & Cheat Sheets (Click to Expand)"):
        st.markdown(CHEAT_SHEETS.get(unit_num, "*Add your custom formulas for this unit here!*"), unsafe_allow_html=True)

def quiz_screen():
    # --- POST-QUIZ REVIEW SCREEN ---
    if st.session_state.current_q_index >= len(st.session_state.quiz_questions):
        st.markdown("<h2 style='text-align: center; color: #0B1B3D;'>Quiz Complete! 🎉</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='text-align: center; color: #C09B5A;'>Your Score: {st.session_state.quiz_score} / {len(st.session_state.quiz_questions)}</h3>", unsafe_allow_html=True)
        st.write("---")
        
        st.markdown("<h3 style='color: #0B1B3D;'>Question Review</h3>", unsafe_allow_html=True)
        
        # --- 1. QUICKLY FETCH THE STUDENT'S VAULT FIRST ---
        vault_response = supabase.table("saved_questions").select("question_id").eq("user_id", st.session_state.user_id).execute()
        saved_q_ids = [item['question_id'] for item in vault_response.data] if vault_response.data else []
        
        for i, ans in enumerate(st.session_state.user_answers):
            st.markdown(f"**Q{i+1}:** {ans['question']}")
            
            if ans['is_correct']:
                st.success(f"**✅ Correct:** {ans['selected']}) {ans['selected_text']}")
            else:
                st.error(f"**❌ Incorrect:** You chose {ans['selected']}) {ans['selected_text']} \n\n **💡 Right Answer:** {ans['correct']}) {ans['correct_text']}")
            
            # --- 2. DYNAMICALLY SHOW ONLY ONE BUTTON ---
            if ans['question_id'] in saved_q_ids:
                # If it's already in the vault, ONLY show the Remove button
                st.button("🗑️ Remove from Vault", key=f"remove_btn_{i}_{ans['question_id']}", on_click=remove_from_vault, args=(ans['question_id'],))
            else:
                # If it's not in the vault, ONLY show the Save button
                st.button("⭐ Save to Vault", key=f"save_btn_{i}_{ans['question_id']}", on_click=save_to_vault, args=(ans['question_id'],))
            
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
        <div style="font-family: sans-serif; text-align: right; color: #0B1B3D; font-size: 18px; font-weight: bold; margin: 0; padding-right: 10px;">
            ⏱️ Time Elapsed: <span id="clock"></span>
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
    
    st.markdown(f"### {q['question_text']}")
    
    if q.get('image_url'):
        st.image(q['image_url'], use_container_width=True)
    
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
            # Group by the raw number so it sorts mathematically (1, 2, 3... 10)
            summary = df.groupby('unit_num')['correct'].mean() * 100
            # Add the word "Unit" back in for the chart labels
            summary.index = [f"Unit {i}" for i in summary.index]
            
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

def admin_dashboard_screen():
    st.markdown("<h1 style='text-align: center; color: #0B1B3D;'>👑  Platform Administration</h1>", unsafe_allow_html=True)
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
    
    st.markdown("### 🌍 Global Platform Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Students", len(users))
    c2.metric("Total Questions Answered", len(attempts_res.data))
    global_acc = (sum(1 for a in attempts_res.data if a['is_correct']) / len(attempts_res.data) * 100) if attempts_res.data else 0
    c3.metric("Global Average Accuracy", f"{global_acc:.1f}%")
    
    st.write("---")
    st.markdown("### 📋 Student Roster & Leaderboard")
    
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
        st.markdown("<h2 style='text-align: center; color: white;'>🎓 Novara Profile</h2>", unsafe_allow_html=True)
        
        response = supabase.table("attempts").select("is_correct").eq("user_id", st.session_state.user_id).execute()
        total_score = sum([1 for item in response.data if item['is_correct'] == 1]) if response.data else 0
        
        st.markdown(f"<div style='text-align: center; color: #C09B5A; font-size: 18px; margin-bottom: 20px;'><b>👤 {st.session_state.username}</b><br>⭐ Total XP: {total_score}</div>", unsafe_allow_html=True)
        
        if st.button("🏠 Home", use_container_width=True, type="primary"):
            st.session_state.current_screen = "dashboard"
            st.rerun()
            
        if st.button("🚀 Start Full Adaptive Quiz", use_container_width=True, type="primary"):
            start_quiz()
            
        if st.button("⭐ Saved Questions", use_container_width=True, type="primary"):
            start_saved_quiz()
            
        if st.button("📊 View Analytics", use_container_width=True, type="primary"):
            st.session_state.current_screen = "analytics"
            st.rerun()
            
        # Secure database-level Admin check
        if st.session_state.get("is_admin", False):
            st.write("---")
            if st.button("👑 Admin", use_container_width=True, type="primary"):
                st.session_state.current_screen = "admin_dashboard"
                st.rerun()
            
        st.write("---")
        if st.button("↩️ Log Out", use_container_width=True, type="primary"):
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