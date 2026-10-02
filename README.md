# MSBTE Student Saver

> **MSBTE Student Saver - Academic Performance Analysis & Early Warning System**  
> Designed for 3rd-Year Diploma Computer Engineering / Computer Science Students under MSBTE.

---

## 1. Project Overview

The **MSBTE Student Saver** is an academic analytics and performance monitoring web application built to help polytechnic institutes track student academic progress, monitor subject-wise attendance, identify students at risk of detention or semester backlogs, and provide actionable interventions through a Machine Learning model and Microsoft Power BI reporting.

### Key Objectives
- **Store & Manage Academic Records:** Centralized repository for diploma students, configurable MSBTE curriculum subjects, internal/external/practical marks, and attendance.
- **Automated Academic Calculations:** Real-time computation of subject total marks, percentages, pass/fail status, aggregate attendance, and project-defined performance tiers.
- **Early Warning System (Machine Learning):** Uses a transparent **Decision Tree Classifier** to classify students into risk tiers (*Good*, *Average*, *Needs Improvement*, *At Risk*) based on attendance, internal tests, assignments, and active backlogs.
- **Business Intelligence Integration:** Generates clean, denormalized CSV datasets formatted for direct import into **Microsoft Power BI Desktop**.
- **Fundamental Cybersecurity:** Demonstrates password hashing via Werkzeug, Role-Based Access Control (RBAC), secure session cookies, parameterized SQL queries, and error handling.

---

## 2. Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Backend** | Python 3.13 / Flask 3.x | Lightweight, readable WSGI web framework |
| **Database** | SQLite 3 / Flask-SQLAlchemy | Serverless relational database with ORM |
| **Frontend** | HTML5, CSS3, JavaScript (ES6) | Responsive, modern user interface |
| **UI Framework** | Bootstrap 5.3 & FontAwesome 6 | Clean academic dashboard and cards |
| **Data Visualization** | Chart.js 4.x | Interactive browser-based charts |
| **Data Analysis** | Pandas & NumPy | Data manipulation and CSV export preparation |
| **Machine Learning** | Scikit-learn (DecisionTreeClassifier) | Explainable white-box classification model |
| **Business Intelligence** | Microsoft Power BI Compatible | Denormalized CSV data export |
| **Security** | Werkzeug Security & Flask Sessions | SHA-256 password hashing & RBAC |

---

## 3. Project Architecture & Viva Flow

```text
┌────────────────────────────────────────────────────────┐
│                   Student Data Entry                   │
│   (Enrollment, Internal/External Marks, Attendance)    │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│           SQLite Relational Database (ORM)             │
│    (users, students, subjects, marks, attendance)      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│               Python Flask Application                 │
│         - Academic Percentage Calculations             │
│         - Pass / Fail / Attendance Evaluations         │
└──────────────┬───────────────────────────┬─────────────┘
               │                           │
               ▼                           ▼
┌──────────────────────────────┐ ┌──────────────────────────────┐
│  Machine Learning Prediction │ │     Power BI Export Pipeline │
│  - Decision Tree Classifier  │ │     - Students & Marks CSV   │
│  - Real Test Accuracy (~79%) │ │     - Master Analytics CSV   │
│  - Early Warning Guidance    │ │     - Power BI Dashboard     │
└──────────────────────────────┘ └──────────────────────────────┘
```

---

## 4. Configurable Demo MSBTE Academic Structure

To ensure branch flexibility across different polytechnics, the application does not hard-code subjects. The administrator can dynamically configure:
- **Branch** (e.g., Computer Engineering, Information Technology)
- **Semester** (Sem 1 to Sem 6)
- **Subject Code & Name** (e.g., `22516` - Operating Systems)
- **Evaluation Scheme:** Internal Max, External Max, Practical Max, Total Max, Passing Marks, and Credits.

> **Notice:** The pre-populated subjects represent a **"Demo MSBTE Academic Structure"** for 3rd Year Diploma Computer Engineering (Semester 5 & 6) and can be adapted to any MSBTE curriculum scheme.

---

## 5. User Roles & Security (RBAC)

### 1. Administrator (`admin`)
- Full access to Admin Dashboard and 5 live Chart.js analytics charts.
- Student Management (Add, Edit, Delete, Search, Filter).
- Configurable Subject Management.
- Marks & Attendance entry modules with validation limits.
- Interactive ML Prediction Studio.
- Power BI CSV data exports.

### 2. Student (`student`)
- Authenticated login via Enrollment Number.
- Read-only access to personal profile, marks breakdown, and attendance.
- Personalized early warning alert and areas needing improvement.
- One-click printable **Academic Analysis Report**.
- Cannot modify or tamper with any marks or database records.

---

## 6. Machine Learning Model Details

- **Algorithm:** `DecisionTreeClassifier(criterion='gini', max_depth=4, random_state=42)`
- **Why Decision Tree for Viva?**  
  Decision trees use clear if-else threshold rules (e.g., `attendance < 60% AND failed_subjects >= 2 -> At Risk`). This avoids complex "black-box" mathematics and allows students to explain every branch during viva defense.
- **Input Features:**
  1. `attendance_percentage`
  2. `internal_percentage`
  3. `previous_percentage`
  4. `assignment_percentage`
  5. `failed_subjects` (active backlogs)
- **Target Performance Classes:** `Good`, `Average`, `Needs Improvement`, `At Risk`.
- **Training Dataset:** 350 realistic synthetic diploma student records.
- **Model Test Accuracy:** **78.6%** (displayed transparently without exaggeration).

---

## 7. Power BI Integration

The application includes a dedicated **Power BI Integration** module:
1. Export the denormalized dataset (`powerbi_master_analytics.csv`) from `/powerbi` or `/export/powerbi-analytics`.
2. Open **Microsoft Power BI Desktop**.
3. Select **Get Data &rarr; Text/CSV**, browse to the downloaded CSV, and click **Load**.
4. Build interactive visuals:
   - **KPI Cards:** Total Students, Avg %, Avg Attendance, Pass %, At-Risk Count.
   - **Visuals:** Subject Average Bar Chart, Category Donut Chart, Attendance vs Score Scatter Plot.
   - **Slicers:** Branch, Semester, Subject, Academic Year.

---

## 8. Installation & Setup Instructions

### Prerequisites
- Python 3.10+ installed on your system.
- `pip` package manager.

### Quick 1-Click Launch (Windows)
Double-click `run.bat` in the project folder, or run:
```cmd
run.bat
```
This script automatically checks Python, ensures the ML model and database are initialized, launches the Flask web server, and opens `http://127.0.0.1:5000` in your default browser.

---

### Step 1: Clone or Open the Project Directory
```bash
cd "e:/Intern Project"
```

### Step 2: (Optional) Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Train ML Model & Initialize Demo Database
```bash
# Train the Decision Tree model
python ml/train_model.py

# Seed the SQLite database with 120 demo students & subjects
python seed_data.py
```

### Step 5: Run the Flask Web Application
```bash
python app.py
```

Open your web browser and navigate to:
```text
http://127.0.0.1:5000
```

---

## 9. Demo Login Credentials

| Role | Username | Password | Notes |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin123` | Full administrative & analytics access |
| **Student (Demo 1)** | `2300520001` | `stud@0001` | Student portal (Sem 5 Computer Engg) |
| **Student (Demo 2)** | `2300520015` | `stud@0015` | Student portal (Needs Improvement demo) |

---

## 10. Automated Testing

Run the built-in test suite to verify authentication, security, marks validation, and ML pipelines:
```bash
python test_app.py
```

---

## 11. 15 Likely Viva Questions & Answers

### Q1: What is the main purpose of this project?
**Answer:** The purpose is to analyze diploma students' academic performance, track subject-wise marks and attendance, and provide an early warning system using a Decision Tree model to identify at-risk students before final MSBTE exams.

### Q2: Why did you choose Flask instead of Django?
**Answer:** Flask is a lightweight micro-framework that is easy to understand, modular, and does not add unnecessary overhead. It allows us to clearly demonstrate core routing, database ORM, and session management concepts.

### Q3: How is password security implemented?
**Answer:** We never store plain-text passwords. We use `werkzeug.security.generate_password_hash()` which generates a salted SHA-256 hash. During login, `check_password_hash()` verifies the entered password against the stored hash.

### Q4: How does the application prevent SQL Injection?
**Answer:** We use SQLAlchemy ORM with parameterized queries (`Student.query.filter_by(...)`). SQL parameters are passed separately from SQL command syntax, preventing attackers from injecting malicious SQL commands.

### Q5: What is Role-Based Access Control (RBAC)?
**Answer:** RBAC restricts access based on user roles. In our system, the `@admin_required` decorator checks `session['role'] == 'admin'`. If a student attempts to open an admin page, the system responds with a `403 Forbidden` error.

### Q6: Why did you choose a Decision Tree Classifier for Machine Learning?
**Answer:** A Decision Tree is a "white-box" model. It splits data based on simple threshold conditions (like `attendance < 60%`), making the prediction logic transparent and easy to explain during viva defense.

### Q7: What features (inputs) are fed into the Machine Learning model?
**Answer:** Five academic features: (1) Attendance percentage, (2) Internal marks percentage, (3) Previous semester percentage, (4) Assignment/lab work score, and (5) Number of active failed subjects.

### Q8: What does the ML model output?
**Answer:** The model predicts one of four performance categories: *Good*, *Average*, *Needs Improvement*, or *At Risk*, along with class probability distributions and actionable recommendations.

### Q9: Does this ML model predict official MSBTE board results?
**Answer:** No. It is an academic early-warning tool designed for educational demonstration. It assists mentors in identifying students who need extra coaching or attendance recovery.

### Q10: How are subject marks validated?
**Answer:** The marks entry route validates entered marks against the subject's configured `internal_max`, `external_max`, and `practical_max`. If a user enters marks higher than the maximum allowed, the system rejects the input.

### Q11: How is attendance calculated and categorized?
**Answer:** Attendance percentage is calculated as `(Attended Classes / Total Classes) * 100`. In our demo criteria:
- &ge; 75%: *Good*
- 60% - 74%: *Needs Attention*
- &lt; 60%: *Low Attendance*

### Q12: How does Power BI integration work?
**Answer:** Flask exports a denormalized master dataset (`powerbi_master_analytics.csv`). In Microsoft Power BI Desktop, we import this CSV file using the Text/CSV connector to build KPI cards and interactive charts.

### Q13: Why is the MSBTE subject structure configurable?
**Answer:** Different diploma branches (Computer, IT, Mechanical, Civil) and schemes (I-Scheme, K-Scheme) have different subjects, mark distributions, and credit structures. Configurable subjects allow the system to adapt without code changes.

### Q14: What happens during session logout?
**Answer:** The `/logout` route calls `session.clear()`, destroying all stored session keys on the server and invalidating the client session cookie.

### Q15: What are the main limitations and future scope of this project?
**Answer:** 
- **Limitations:** Uses synthetic training data; ML predictions are for demonstration; Power BI runs as a separate desktop tool.
- **Future Scope:** Adding automated SMS/WhatsApp alerts for parents, biometric attendance integration, and cloud deployment on AWS/Azure.

---

## 12. Project Limitations & Future Scope

### Project Limitations
1. Uses synthetic demo data for student records and training.
2. ML predictions are educational early warnings, not official MSBTE board awards.
3. The academic structure is a demo scheme and should be customized per college branch.

### Future Scope
1. Real-time REST API connection to Power BI Service.
2. Biometric RFID / QR-code attendance integration.
3. Automated WhatsApp / Email alert triggers to mentors and parents for attendance drops below 75%.
4. Role hierarchy extension for Head of Department (HOD) and Class Teachers.
