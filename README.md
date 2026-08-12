# 🎓 Novara Academy — Adaptive AP Calculus Learning Engine

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg)](https://streamlit.io/)
[![Supabase](https://img.shields.io/badge/Database-Supabase%20PostgreSQL-3ECF8E.svg)](https://supabase.com/)
[![Security](https://img.shields.io/badge/Auth-Bcrypt%20Salted-green.svg)](https://en.wikipedia.org/wiki/Bcrypt)

**Novara Academy** is an open-access, cloud-connected adaptive learning engine designed to expand Advanced Placement (AP) STEM education among youth in Uzbekistan and beyond. By combining data-driven performance analytics, latency tracking, and adaptive question queuing, Novara Academy empowers students to master AP Calculus efficiently—even in regions where AP coursework is traditionally inaccessible.

---

## 🚀 The Mission

In many developing regions, Advanced Placement courses remain uncommon, leaving talented youth without structured pathways to world-class STEM preparation. **Novara Academy** was built to break that barrier. By offering a free, high-rigor, adaptive learning environment, the platform helps local students build conceptual mastery, accelerate their learning pace, and compete on the international academic stage.

---

## 🌟 Key Features

### 🧠 1. Rule-Based Adaptive Algorithm
* **Weak Topic Prioritization:** The engine queries historical attempt data in real time. If a student's performance in any of the 10 AP Calculus units drops below **60%**, the platform dynamically reshuffles the queue to target those weak points.
* **Latency & Pacing Alerts:** Custom JavaScript timing components monitor per-question response speeds. Correct answers taking longer than **90 seconds** trigger pacing warnings to help students adapt to the College Board's strict exam time constraints.

### 🔒 2. Enterprise-Grade Security Architecture
* **Bcrypt Password Hashing:** User credentials are encrypted using salted `bcrypt` hashing to ensure banking-level data security.
* **Role-Based Access Control:** Administrative access ("God Mode") is managed via row-level boolean flags (`is_admin`) in Supabase, eliminating exposed API secrets or hardcoded credentials.

### 🏆 3. Gamification & Student Habit Building
* **Mastery Trophy Case:** Dynamically calculates accuracy across all units. Reaching **$\ge80\%$ accuracy** unlocks Champagne Gold trophy badges.
* **Daily Streak Tracker:** Logs consecutive active learning days to encourage daily study habits.
* **Starred Question Vault:** Allows students to bookmark challenging questions post-quiz and generate custom review sessions using only saved items.

### 👑 4. Administrator Analytics Dashboard
* **Global Performance Overview:** Tracks total registered students, global questions answered, and aggregate platform accuracy.
* **Student Leaderboard & Weakness Tracking:** Displays student progress, total XP, and identifies each student's weakest unit for targeted educational guidance.

---

## 🛠️ Tech Stack & Architecture

| Component | Technology | Description |
| :--- | :--- | :--- |
| **Frontend Framework** | `Streamlit` | Interactive web UI styled with custom CSS injection. |
| **Database** | `Supabase (PostgreSQL)` | Cloud relational database storing tables for `users`, `questions`, `attempts`, and `saved_questions`. |
| **Authentication** | `Bcrypt` | Salted password hashing and session verification. |
| **Analytics & Visualization** | `Pandas`, `Matplotlib` | Historical trend aggregation, accuracy tracking, and performance charting. |
| **Caching Optimization** | `@st.cache_data` | Server-side data memoization to eliminate redundant database queries. |

---

## 📁 Repository Structure

```text
├── .streamlit/
│   └── config.toml         # Custom Novara Academy Deep Navy & Gold theme settings
├── app.py                  # Core application logic, routing, and UI views
├── seed_all_units.py       # Cloud database bulk question bank importer
├── requirements.txt        # Production Python dependencies
└── README.md               # Documentation & project overview
