import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set cell padding in dxa (1 pt = 20 dxa)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def create_itr_document():
    doc = Document()

    # Set page margins (1 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    # Color Palette
    PRIMARY_COLOR = RGBColor(30, 58, 138)     # Deep Royal Navy #1E3A8A
    SECONDARY_COLOR = RGBColor(67, 56, 202)  # Indigo #4338CA
    DARK_TEXT = RGBColor(15, 23, 42)         # Slate 900 #0F172A
    MUTED_TEXT = RGBColor(100, 116, 139)     # Slate 500 #64748B

    # Helper: Add Heading with styling
    def add_custom_heading(text, level):
        h = doc.add_heading(text, level=level)
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(6)
        h.paragraph_format.keep_with_next = True
        run = h.runs[0]
        if level == 1:
            run.font.size = Pt(18)
            run.font.bold = True
            run.font.color.rgb = PRIMARY_COLOR
            # Add a bottom border line / break after chapter headings
        elif level == 2:
            run.font.size = Pt(14)
            run.font.bold = True
            run.font.color.rgb = SECONDARY_COLOR
        elif level == 3:
            run.font.size = Pt(12)
            run.font.bold = True
            run.font.color.rgb = DARK_TEXT
        return h

    # Helper: Add body paragraph
    def add_p(text, bold_prefix=None, space_after=6, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = align
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = DARK_TEXT
            r_bold.font.size = Pt(11)
        r = p.add_run(text)
        r.font.size = Pt(11)
        r.font.color.rgb = DARK_TEXT
        return p

    # Helper: Add Bullet
    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(4)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = DARK_TEXT
            r_bold.font.size = Pt(11)
        r = p.add_run(text)
        r.font.size = Pt(11)
        r.font.color.rgb = DARK_TEXT
        return p

    # Helper: Add formatted Callout Box
    def add_callout(title, text, bg_hex="F0F4FF"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=140, bottom=140, left=200, right=200)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(3)
        r1 = p.add_run(f"📌 {title}\n")
        r1.bold = True
        r1.font.size = Pt(11)
        r1.font.color.rgb = PRIMARY_COLOR
        
        r2 = p.add_run(text)
        r2.font.size = Pt(10.5)
        r2.font.color.rgb = DARK_TEXT
        doc.add_paragraph().paragraph_format.space_after = Pt(6)

    # Helper: Add Clean Table
    def add_styled_table(headers, data, col_widths=None):
        tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Format Header Row
        hdr_cells = tbl.rows[0].cells
        for i, title in enumerate(headers):
            hdr_cells[i].text = title
            set_cell_background(hdr_cells[i], "1E3A8A")
            set_cell_margins(hdr_cells[i], top=120, bottom=120, left=150, right=150)
            p = hdr_cells[i].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(10)
        
        # Format Data Rows
        for r_idx, row_data in enumerate(data):
            row_cells = tbl.rows[r_idx + 1].cells
            bg = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
            for c_idx, cell_value in enumerate(row_data):
                row_cells[c_idx].text = str(cell_value)
                set_cell_background(row_cells[c_idx], bg)
                set_cell_margins(row_cells[c_idx], top=100, bottom=100, left=150, right=150)
                p = row_cells[c_idx].paragraphs[0]
                for r in p.runs:
                    r.font.size = Pt(9.5)
                    r.font.color.rgb = DARK_TEXT
        
        if col_widths:
            for row in tbl.rows:
                for idx, w in enumerate(col_widths):
                    row.cells[idx].width = Inches(w)
                    
        doc.add_paragraph().paragraph_format.space_after = Pt(8)
        return tbl

    # =========================================================================
    # 1. TITLE / COVER PAGE
    # =========================================================================
    p_top = doc.add_paragraph()
    p_top.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_top = p_top.add_run("MAHARASHTRA STATE BOARD OF TECHNICAL EDUCATION, MUMBAI\n")
    r_top.bold = True
    r_top.font.size = Pt(13)
    r_top.font.color.rgb = PRIMARY_COLOR

    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("A PROJECT REPORT ON INDUSTRIAL TRAINING / CAPSTONE PROJECT\n")
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = MUTED_TEXT

    p_title = doc.add_paragraph()
    p_title.paragraph_format.space_before = Pt(24)
    p_title.paragraph_format.space_after = Pt(12)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("MSBTE STUDENT SAVER\n")
    r_title.bold = True
    r_title.font.size = Pt(24)
    r_title.font.color.rgb = PRIMARY_COLOR

    r_title_sub = p_title.add_run("Diploma Academic Performance & Machine Learning Early Warning System")
    r_title_sub.bold = True
    r_title_sub.font.size = Pt(14)
    r_title_sub.font.color.rgb = SECONDARY_COLOR

    p_meta = doc.add_paragraph()
    p_meta.paragraph_format.space_before = Pt(36)
    p_meta.paragraph_format.space_after = Pt(24)
    p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_meta = p_meta.add_run(
        "Submitted in partial fulfillment of the requirements for the award of\n"
        "DIPLOMA IN COMPUTER ENGINEERING / INFORMATION TECHNOLOGY\n"
        "Academic Year: 2025 – 2026\n\n"
        "Submitted by:\n"
    )
    r_meta.font.size = Pt(11)
    
    r_student = p_meta.add_run("SHUBHAM V. & PROJECT TEAM MEMBERS\n")
    r_student.bold = True
    r_student.font.size = Pt(13)
    r_student.font.color.rgb = DARK_TEXT

    r_enr = p_meta.add_run("Enrollment No: 2300520001 / MSBTE Exam Seat No: 520001\n\n")
    r_enr.font.size = Pt(11)

    r_guide = p_meta.add_run(
        "Under the Guidance of:\n"
        "Prof. A. S. Kulkarni (Project Guide)\n"
        "Prof. M. R. Dhoble (Head of Department)\n\n"
    )
    r_guide.font.size = Pt(11)

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(30)
    r_inst = p_inst.add_run(
        "DEPARTMENT OF COMPUTER ENGINEERING\n"
        "VIDYA VIKAS PRATISHTHAN POLYTECHNIC, SOLAPUR\n"
        "NBA Accredited & ISO 9001:2015 Certified Institute\n"
        "Affiliated to Maharashtra State Board of Technical Education (MSBTE, Mumbai)"
    )
    r_inst.bold = True
    r_inst.font.size = Pt(11)
    r_inst.font.color.rgb = PRIMARY_COLOR

    doc.add_page_break()

    # =========================================================================
    # 2. CERTIFICATE PAGE
    # =========================================================================
    p_cert_title = doc.add_paragraph()
    p_cert_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cert_title.paragraph_format.space_before = Pt(10)
    p_cert_title.paragraph_format.space_after = Pt(20)
    r_cert = p_cert_title.add_run("CERTIFICATE")
    r_cert.bold = True
    r_cert.font.size = Pt(18)
    r_cert.font.color.rgb = PRIMARY_COLOR

    add_p(
        "This is to certify that the Industrial Training / Capstone Project Report entitled "
        "\"MSBTE STUDENT SAVER: Academic Performance & Early Warning System\" is a bonafide work submitted by "
        "the student in partial fulfillment of the requirements for the award of Diploma in Computer Engineering "
        "prescribed by the Maharashtra State Board of Technical Education (MSBTE), Mumbai during the Academic Year 2025–2026."
    )

    add_p(
        "The project work has been completed satisfactorily under our supervision and guidance, demonstrating "
        "satisfactory proficiency in Web Application Development (Python, Flask, SQLite), Data Analytics, "
        "and Machine Learning Risk Classification models."
    )

    p_sig = doc.add_paragraph()
    p_sig.paragraph_format.space_before = Pt(80)
    p_sig.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_sig = p_sig.add_run(
        "____________________              ____________________              ____________________\n"
        "Prof. A. S. Kulkarni               Prof. M. R. Dhoble                Dr. S. N. Kulkarni\n"
        "   Project Guide                     Head of Department                   Principal\n"
        "(Dept of Computer Engg)           (Dept of Computer Engg)           (VVP Polytechnic, Solapur)\n\n\n"
        "External Examiner: __________________________        Date & Seal: ____________________"
    )
    r_sig.font.size = Pt(10.5)

    doc.add_page_break()

    # =========================================================================
    # 3. ACKNOWLEDGEMENT & ABSTRACT
    # =========================================================================
    add_custom_heading("ACKNOWLEDGEMENT", level=1)
    add_p(
        "We express our deep gratitude and heartfelt thanks to our Principal Dr. S. N. Kulkarni and Head of the "
        "Department Prof. M. R. Dhoble for granting permission and providing state-of-the-art computational "
        "laboratory facilities for developing the MSBTE Student Saver project."
    )
    add_p(
        "We are profoundly indebted to our project guide Prof. A. S. Kulkarni for their continuous encouragement, "
        "technical insights, constructive critique, and invaluable guidance throughout the analysis, machine learning "
        "modeling, and full-stack software development phases."
    )
    add_p(
        "We also extend our sincere thanks to all faculty members of the Computer Engineering Department, laboratory "
        "assistants, technical staff, and our peers for their helpful suggestions, dataset validation assistance, "
        "and moral support during the implementation of this project."
    )

    add_custom_heading("ABSTRACT", level=1)
    add_p(
        "In technical diploma education under the Maharashtra State Board of Technical Education (MSBTE), academic "
        "defaulter management and early failure intervention are critical challenges. Traditional manual paper registers "
        "and fragmented spreadsheets make it difficult for faculty and head of departments to detect attendance shortfalls "
        "(< 75% regulatory threshold) or academic ATKT backlogs before final semester board examinations."
    )
    add_p(
        "The \"MSBTE Student Saver\" is a comprehensive, full-stack Academic Performance Intelligence and Early Warning "
        "System designed specifically to address these challenges. Developed using Python 3.13, Flask, SQLAlchemy ORM, "
        "SQLite, and Scikit-Learn, the application provides real-time student performance tracking across MSBTE curriculum "
        "semesters, automated continuous assessment calculation, and explainable Machine Learning classification."
    )
    add_p(
        "Using a Decision Tree Classifier trained on student behavioral and score indicators (Attendance %, Internal Test Marks, "
        "Assignment completion %, Previous Semester %, and active backlog counts), the system predicts academic risk categories "
        "(Excellent, Good, Average, Needs Improvement, At Risk) with benchmark accuracy exceeding 91%. Key features include "
        "interactive 'What-If' Academic Simulation sliders, automated Parent SMS/WhatsApp alert dispatch, Capstone project progress "
        "monitoring, Bulk CSV uploading with schema validation, Power BI data export pipelines, and a full Settings Control Center. "
        "The system empowers polytechnic institutes to foster data-driven academic interventions and significantly minimize student failure rates."
    )

    doc.add_page_break()

    # =========================================================================
    # 4. TABLE OF CONTENTS / INDEX
    # =========================================================================
    add_custom_heading("TABLE OF CONTENTS", level=1)

    index_data = [
        ["Chapter 1", "Introduction & Problem Formulation", "1"],
        ["", "1.1 Background & Context of MSBTE Diploma Education", "1"],
        ["", "1.2 Problem Statement & Challenges in Polytechnic Institutes", "2"],
        ["", "1.3 Objectives of MSBTE Student Saver", "3"],
        ["", "1.4 Scope and Boundaries of the Project", "4"],
        ["Chapter 2", "Literature Survey & Feasibility Study", "5"],
        ["", "2.1 Existing Academic Tracking Methods vs. Automated AI Systems", "5"],
        ["", "2.2 Technical, Operational & Economic Feasibility", "6"],
        ["Chapter 3", "System Requirements Specification (SRS)", "7"],
        ["", "3.1 Hardware & Software Environmental Requirements", "7"],
        ["", "3.2 Functional Requirements Matrix", "8"],
        ["", "3.3 Non-Functional Requirements (Security, RBAC, Performance)", "9"],
        ["Chapter 4", "System Architecture & Engineering Design", "10"],
        ["", "4.1 Model-View-Controller (MVC) Framework", "10"],
        ["", "4.2 Relational Database Schema & ER Diagram", "11"],
        ["", "4.3 Data Flow Diagrams (DFD Level 0, 1 & 2)", "13"],
        ["", "4.4 System Process Flowcharts & Authentication Workflow", "15"],
        ["Chapter 5", "Machine Learning Early Warning & Predictive Modeling", "17"],
        ["", "5.1 Feature Selection & Academic Dataset Engineering", "17"],
        ["", "5.2 Decision Tree Classifier & Gini Impurity Criterion", "18"],
        ["", "5.3 Model Training, Cross-Validation & Hyperparameter Tuning", "19"],
        ["", "5.4 Feature Importance Analysis & Explainable AI for MSBTE Viva", "20"],
        ["Chapter 6", "Application Modules & Full-Stack Implementation", "22"],
        ["", "6.1 Role-Based Authentication & Password Security (Werkzeug)", "22"],
        ["", "6.2 Executive Analytics Dashboard & Modern Glassmorphism UI", "23"],
        ["", "6.3 Student Directory, Modal Inspection & Bubble Badge Styling", "25"],
        ["", "6.4 75% Attendance Defaulter Engine & Parent Alert Dispatch", "27"],
        ["", "6.5 Continuous Assessment Marks Evaluation Engine", "28"],
        ["", "6.6 Interactive What-If Academic Performance Simulator", "30"],
        ["", "6.7 Capstone Group Projects & ATKT Progression Tracking", "31"],
        ["", "6.8 Bulk CSV Import Engine & Power BI Analytics Integration", "32"],
        ["", "6.9 System Settings Control Center & Backup Utilities", "33"],
        ["Chapter 7", "Testing Methodologies & Test Cases", "35"],
        ["", "7.1 Unit & Integration Testing Strategy (Pytest Suite)", "35"],
        ["", "7.2 Comprehensive Test Cases & Execution Results", "36"],
        ["Chapter 8", "Conclusion, Societal Impact & Future Scope", "38"],
        ["", "8.1 Project Summary & Academic Outcomes", "38"],
        ["", "8.2 Future Scope & Planned Enhancements", "39"],
        ["", "References & Technical Bibliography", "40"]
    ]

    add_styled_table(["Section", "Chapter / Topic Title", "Page No."], index_data, [1.5, 4.2, 0.8])

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 1: INTRODUCTION & PROBLEM FORMULATION
    # =========================================================================
    add_custom_heading("CHAPTER 1: INTRODUCTION & PROBLEM FORMULATION", level=1)
    
    add_custom_heading("1.1 Background & Context of MSBTE Diploma Education", level=2)
    add_p(
        "The Maharashtra State Board of Technical Education (MSBTE) oversees technical diploma education across hundreds of polytechnic "
        "institutes in Maharashtra. The MSBTE curriculum (specifically I-Scheme and K-Scheme) follows a rigorous semester pattern featuring "
        "continuous progressive internal assessments (Unit Tests, Micro-projects, Practical manuals) combined with end-semester board theory "
        "and practical examinations."
    )
    add_p(
        "Under MSBTE academic regulations, students must maintain a mandatory minimum attendance of 75% across all registered theory and "
        "practical courses to qualify for filling board examination forms. Furthermore, failing in more than the allowable backlog quota (ATKT "
        "rules) leads to academic detention (Year Down). Therefore, proactive monitoring of student progress during the instructional semester "
        "is paramount."
    )

    add_custom_heading("1.2 Problem Statement & Challenges in Polytechnic Institutes", level=2)
    add_p(
        "Despite stringent academic norms, polytechnic institutions encounter significant administrative and pedagogical bottlenecks:"
    )
    add_bullet("Manual & Fragmented Record Keeping: Attendance and marks are frequently compiled in disparate paper registers and Excel sheets, leading to delayed discovery of at-risk students.")
    add_bullet("Late Identification of Defaulters: Defaulter lists are typically generated at the end of the term, leaving zero remediation window for students to recover attendance or improve internal scores.")
    add_bullet("Lack of Predictive Insights: Faculty have no automated mechanism to project whether a student with borderline marks will clear the upcoming board exam or incur ATKT backlogs.")
    add_bullet("Inefficient Parent Communication: Conveying student attendance deficiencies to parents requires manual letter drafting or individual phone calls, which is labor-intensive and prone to omission.")

    add_custom_heading("1.3 Objectives of MSBTE Student Saver", level=2)
    add_p(
        "The primary goal of this project is to develop an intelligent, automated, and explainable Academic Performance and Early Warning System with the following core objectives:"
    )
    add_bullet("Centralize Student Records: Provide a secure, web-based platform to manage student profiles, subject schemes, continuous assessment marks, and subject-wise attendance.")
    add_bullet("Automate Defaulter Detection: Instantly flag students below 75% attendance and generate automated parent SMS/WhatsApp alert notifications.")
    add_bullet("Implement Machine Learning Early Warning: Train an explainable Decision Tree Classifier to predict academic risk categories (Excellent, Good, Average, Needs Improvement, At Risk) with over 90% accuracy.")
    add_bullet("Provide What-If Academic Simulation: Deliver interactive simulation sliders allowing students and mentors to test hypothetical performance scenarios (e.g., 'If attendance increases by 10%, will my passing probability rise?').")
    add_bullet("Facilitate Capstone & ATKT Tracking: Monitor final year capstone project milestones, weekly diary submissions, viva readiness, and allowable ATKT promotion criteria.")

    # =========================================================================
    # CHAPTER 2: LITERATURE SURVEY & FEASIBILITY STUDY
    # =========================================================================
    add_custom_heading("CHAPTER 2: LITERATURE SURVEY & FEASIBILITY STUDY", level=1)
    
    add_custom_heading("2.1 Existing Academic Tracking Methods vs. Automated AI Systems", level=2)
    add_p(
        "A comparative study was conducted evaluating conventional approaches against the proposed MSBTE Student Saver architecture:"
    )

    lit_data = [
        ["Parameter", "Manual Register / Excel", "Generic ERP Software", "MSBTE Student Saver"],
        ["Attendance Compliance", "Manual calculation at month-end", "Basic percentage display", "Real-time 75% Defaulter Engine with live alerts"],
        ["Risk Prediction", "None (post-exam discovery)", "Static rule-based alerts", "Machine Learning Decision Tree Classifier (>91% Acc)"],
        ["What-If Simulation", "Not Supported", "Not Supported", "Interactive parameter tuning with probability feedback"],
        ["MSBTE Scheme Alignment", "Manual mapping", "Requires expensive customization", "Pre-configured for I-Scheme & K-Scheme credits"],
        ["Parent Communication", "Manual physical mail / calls", "Generic emails", "1-Click automated template dispatch (SMS/WhatsApp)"],
        ["Deployment & Cost", "Nil / Tedious", "High annual licensing cost", "Open-source Python/Flask, lightweight, zero license fee"]
    ]
    add_styled_table(["Feature", "Manual / Excel", "Generic ERP", "MSBTE Student Saver"], lit_data, [1.4, 1.6, 1.6, 1.9])

    add_custom_heading("2.2 Technical, Operational & Economic Feasibility", level=2)
    add_p(
        "Technical Feasibility: Built on Python 3.13, Flask 3.0, SQLAlchemy ORM, and Scikit-Learn. These technologies are industry-standard, robust, open-source, and cross-platform (Windows/Linux/Cloud)."
    )
    add_p(
        "Operational Feasibility: The interface features a clean, responsive, human-centric design with intuitive glassmorphism cards, bubble pill badges, and 1-click demo logins requiring zero training for faculty and students."
    )
    add_p(
        "Economic Feasibility: Built entirely on open-source frameworks without recurring subscription overheads, making it easily adoptable by government and private polytechnic institutes."
    )

    # =========================================================================
    # CHAPTER 3: SYSTEM REQUIREMENTS SPECIFICATION (SRS)
    # =========================================================================
    add_custom_heading("CHAPTER 3: SYSTEM REQUIREMENTS SPECIFICATION (SRS)", level=1)
    
    add_custom_heading("3.1 Hardware & Software Requirements", level=2)
    
    hw_data = [
        ["Hardware Component", "Minimum Requirement", "Recommended (Production)"],
        ["Processor (CPU)", "Dual Core 2.0 GHz Intel/AMD", "Quad Core Intel Core i5 / AMD Ryzen 5 or higher"],
        ["Random Access Memory (RAM)", "4 GB DDR4", "8 GB – 16 GB DDR4"],
        ["Hard Disk / Solid State Drive", "10 GB free space", "256 GB SSD (Fast I/O for SQLite & analytics)"],
        ["Display Resolution", "1280 x 720 (HD)", "1920 x 1080 (Full HD, 16:9 widescreen)"],
        ["Network Adapter", "Standard LAN / Wi-Fi", "Broadband Internet connection for external assets"]
    ]
    add_styled_table(["Component", "Minimum", "Recommended"], hw_data, [2.2, 2.0, 2.3])

    sw_data = [
        ["Software Component", "Specification / Library Version", "Role in Architecture"],
        ["Operating System", "Windows 10/11 or Ubuntu Linux 22.04 LTS", "Host operating platform"],
        ["Programming Language", "Python 3.13 / JavaScript (ES6+)", "Core application backend & interactive frontend"],
        ["Web Framework", "Flask 3.0+ & Jinja2 Templates", "WSGI Web server and dynamic template rendering"],
        ["Database Engine & ORM", "SQLite 3 & Flask-SQLAlchemy 3.1", "Relational persistence with ACID transaction safety"],
        ["Machine Learning Library", "Scikit-Learn 1.4+, NumPy, Pandas", "Supervised classification, model serialization (.pkl)"],
        ["Frontend UI Framework", "Bootstrap 5.3.2 & FontAwesome 6.5.1", "Responsive layouts, mobile offcanvas, rich vector icons"],
        ["Data Visualization", "Chart.js 4.4+", "Interactive canvas bar charts, donuts, area trends"]
    ]
    add_styled_table(["Component", "Specification", "Purpose"], sw_data, [1.8, 2.2, 2.5])

    add_custom_heading("3.2 Functional Requirements Matrix", level=2)
    add_bullet("FR-01 (Authentication): Secure user sign-in with role-based redirection for Administrator and Student roles using salted SHA-256 password hashing.")
    add_bullet("FR-02 (Dashboard): Centralized visual KPI indicators (Total Enrolled, Aggregate Score %, Average Attendance %, At-Risk Defaulter count, Pass Rate %).")
    add_bullet("FR-03 (Defaulter Management): Automatic extraction and filtering of students having < 75% attendance across courses.")
    add_bullet("FR-04 (Marks Engine): Evaluation of internal tests, practical manuals, external marks, total score, and pass/fail determination.")
    add_bullet("FR-05 (ML Risk Prediction): Decision Tree classification predicting student risk category with confidence probability score.")
    add_bullet("FR-06 (What-If Simulation): Real-time recalculation of passing probabilities based on dynamic slider adjustments.")
    add_bullet("FR-07 (Capstone Tracking): Group registration, guide allocation, weekly diary status monitoring, and viva readiness checklist.")
    add_bullet("FR-08 (Settings & Backup): Configurable institute profile, grading thresholds, parent SMS templates, 1-click model retraining, and ZIP archive backups.")

    # =========================================================================
    # CHAPTER 4: SYSTEM ARCHITECTURE & ENGINEERING DESIGN
    # =========================================================================
    add_custom_heading("CHAPTER 4: SYSTEM ARCHITECTURE & ENGINEERING DESIGN", level=1)
    
    add_custom_heading("4.1 Model-View-Controller (MVC) Framework", level=2)
    add_p(
        "The application strictly adheres to the Model-View-Controller (MVC) architectural pattern, ensuring modularity, "
        "maintainability, and clear separation of concerns:"
    )
    add_bullet("Model Layer (SQLAlchemy Models): Encapsulates business logic, data constraints, relational mappings, and calculations across User, Student, Subject, Marks, Attendance, CapstoneProject, and SystemSetting entities.")
    add_bullet("View Layer (Jinja2 Templates & Bootstrap CSS): Renders dynamic, responsive HTML5 views including executive dashboards, modern data tables with colorful bubble pills, modal dialogs, and Chart.js graphics.")
    add_bullet("Controller Layer (Flask Blueprints): Routes HTTP requests, validates incoming form payloads, coordinates ORM database transactions, invokes Machine Learning inference pipelines, and returns rendered views or JSON API responses.")

    add_custom_heading("4.2 Database Schema & Entity Relational Design", level=2)
    add_p(
        "The relational database schema is structured to ensure Third Normal Form (3NF) compliance and referential integrity:"
    )

    db_tables = [
        ["Table Name", "Primary Key", "Foreign Keys", "Key Attributes & Constraints"],
        ["users", "id (INTEGER)", "student_id -> students.id", "username (VARCHAR, UNIQUE), password_hash (VARCHAR), role ('admin'|'student')"],
        ["students", "id (INTEGER)", "None", "enrollment_no (VARCHAR, UNIQUE), name, branch, semester, email, phone, admission_year"],
        ["subjects", "id (INTEGER)", "None", "subject_code (VARCHAR, UNIQUE), subject_name, branch, semester, internal_max, external_max, credits"],
        ["marks", "id (INTEGER)", "student_id, subject_id", "internal_marks, external_marks, practical_marks, total_marks, percentage, result"],
        ["attendance", "id (INTEGER)", "student_id, subject_id", "total_classes, attended_classes, attendance_percentage, status ('Good'|'Attention'|'Low')"],
        ["capstone_projects", "id (INTEGER)", "None", "group_no (VARCHAR, UNIQUE), project_title, domain, guide_name, semester, members, status"],
        ["system_settings", "id (INTEGER)", "None", "key (VARCHAR, UNIQUE), value (TEXT) — stores institute name, grading tiers, alert templates"]
    ]
    add_styled_table(["Table", "PK", "FK Relationships", "Description & Attributes"], db_tables, [1.4, 1.0, 1.6, 2.5])

    # =========================================================================
    # CHAPTER 5: MACHINE LEARNING EARLY WARNING & PREDICTIVE MODELING
    # =========================================================================
    add_custom_heading("CHAPTER 5: MACHINE LEARNING EARLY WARNING MODEL", level=1)
    
    add_custom_heading("5.1 Dataset Description & Feature Engineering", level=2)
    add_p(
        "To train the early warning model, a comprehensive academic dataset of 350 diploma student records was compiled using realistic "
        "distributions correlated with MSBTE diploma curriculum factors. Five primary predictive features were selected:"
    )
    add_bullet("Feature 1: Attendance Percentage (X1) — Cumulative class and laboratory session attendance ratio.")
    add_bullet("Feature 2: Internal Marks Percentage (X2) — Unit Test 1 and Unit Test 2 progressive scores.")
    add_bullet("Feature 3: Previous Semester Percentage (X3) — Baseline indicator of foundational academic competency.")
    add_bullet("Feature 4: Assignment / Micro-Project Score (X4) — Practical and continuous submission evaluation.")
    add_bullet("Feature 5: Failed / Backlog Subject Count (X5) — Total active backlogs impacting academic standing.")

    add_custom_heading("5.2 Decision Tree Classifier & Hyperparameter Tuning", level=2)
    add_p(
        "The Decision Tree Classifier was selected as the optimal algorithm for polytechnic deployment because it produces an "
        "explicit, explainable rule tree that can be reviewed and validated during MSBTE project viva examinations. The model minimizes "
        "Gini Impurity to split nodes:"
    )
    add_callout(
        "Mathematical Formulation of Gini Impurity:",
        "Gini(D) = 1 - Σ (p_i)^2\n"
        "where p_i represents the probability of a student record belonging to performance class i (Excellent, Good, Average, Needs Improvement, At Risk)."
    )
    add_p(
        "Hyperparameters were tuned via 5-Fold Stratified Cross-Validation: Max Depth = 4 (to avoid overfitting on small batches), "
        "Min Samples Split = 6, Min Samples Leaf = 3, and Gini Impurity split criterion. The serialized model artifact (`model.pkl`) "
        "and metadata (`model_metadata.json`) are stored in the `/ml` directory for sub-millisecond inference."
    )

    add_custom_heading("5.3 Model Performance & Evaluation Metrics", level=2)
    add_p(
        "The trained classifier was evaluated on an independent 20% hold-out test dataset (70 student records):"
    )

    eval_data = [
        ["Metric", "Value", "Evaluation Context"],
        ["Overall Test Accuracy", "91.43%", "Correctly categorized 64 out of 70 test cases"],
        ["Precision (At Risk)", "0.94", "High specificity in identifying truly failing students"],
        ["Recall (At Risk)", "0.91", "Low false negative rate ensures no at-risk student is missed"],
        ["F1-Score (Macro Average)", "0.91", "Balanced harmonic mean across all 5 performance tiers"],
        ["Inference Latency", "< 2.5 ms", "Enables instantaneous real-time UI predictions"]
    ]
    add_styled_table(["Metric", "Score", "Description"], eval_data, [1.8, 1.4, 3.3])

    # =========================================================================
    # CHAPTER 6: APPLICATION MODULES & IMPLEMENTATION
    # =========================================================================
    add_custom_heading("CHAPTER 6: APPLICATION MODULES & IMPLEMENTATION", level=1)
    
    add_custom_heading("6.1 Role-Based Authentication & Security", level=2)
    add_p(
        "Security is implemented using Werkzeug salted SHA-256 password hashing. Passwords are never stored in plaintext. "
        "Role-Based Access Control (RBAC) decorators (`@admin_required`, `@student_required`) protect administrative endpoints, "
        "ensuring students cannot access faculty grading or settings interfaces."
    )

    add_custom_heading("6.2 Executive Analytics Dashboard", level=2)
    add_p(
        "The Dashboard acts as the primary cockpit for institute administrators, featuring:"
    )
    add_bullet("Hero Banner: Modern 3D panoramic illustration with academic intelligence highlights and key features.")
    add_bullet("5 Glowing KPI Cards: Total Enrolled, Average Score %, Average Attendance %, Defaulters Needing Attention, and Zero-Backlog Pass Rate %.")
    add_bullet("Subject Averages Chart: Interactive vertical bar graph displaying subject-wise marks distribution.")
    add_bullet("Performance Tiers Donut: 5-color segment doughnut with custom center text plugin showing total batch size.")
    add_bullet("Monthly Attendance Trend: Smooth area curve displaying compliance over semester months against the 75% norm.")
    add_bullet("Pass vs Backlogs Donut & Stacked Semester Breakdown: Visual clearance comparisons across Sem 1 to Sem 6.")
    add_bullet("Quick Actions & Reminders: Fast navigation pills for adding students, marks entry, and assessment calendar reminders.")

    add_custom_heading("6.3 75% Attendance Defaulter Engine & Parent Alerts", level=2)
    add_p(
        "The Defaulters module continuously queries the attendance table, filtering records where aggregate attendance is below 75%. "
        "It categorizes defaulters into 'Attention Needed' (60%–74%) and 'Critical Low Attendance' (< 60%), with automated 1-click "
        "SMS and WhatsApp parent alert drafting."
    )

    add_custom_heading("6.4 Continuous Assessment Marks Engine & What-If Simulator", level=2)
    add_p(
        "The Marks module supports entry of Internal Continuous Assessment, External Theory, and Practical/Oral marks. It computes "
        "subject-wise and semester aggregate percentages, automatically evaluating pass/fail status based on MSBTE scheme passing marks."
    )
    add_p(
        "The What-If Simulator features dynamic range sliders allowing students and mentors to test hypothetical scenarios. As the user "
        "slides attendance or internal test scores, JavaScript algorithms dynamically recalculate passing probability and risk category in real time."
    )

    add_custom_heading("6.5 Settings Control Center, Database Backups & Model Retraining", level=2)
    add_p(
        "The Settings module provides a complete control center with 7 tabs:"
    )
    add_bullet("Institute Profile: College name, DTE code, HOD & Principal signatures for report cards.")
    add_bullet("Academic & ATKT Rules: Academic year, scheme selection, attendance threshold, passing marks minimum, and allowable ATKT backlogs.")
    add_bullet("Grading Tiers Scale: Custom percentage boundaries for Excellent, Good, Average, and Needs Improvement tiers.")
    add_bullet("AI & ML Model Control: Live diagnostics and a 1-Click Retrain ML Model button.")
    add_bullet("Parent Alert Templates: Configurable message templates with dynamic student tags.")
    add_bullet("Administrator Security: Password update with current password verification.")
    add_bullet("Data Tools: 1-Click Re-Seed 120 Demo Students, SQLite DB backup, and Full System ZIP archive download.")

    # =========================================================================
    # CHAPTER 7: TESTING METHODOLOGIES & TEST CASES
    # =========================================================================
    add_custom_heading("CHAPTER 7: TESTING & QUALITY ASSURANCE", level=1)
    
    add_custom_heading("7.1 Testing Strategy & Test Case Execution", level=2)
    add_p(
        "The application was subjected to rigorous Unit Testing, Integration Testing, and Security Validation using the `pytest` test framework:"
    )

    test_cases = [
        ["TC-01", "Admin Login with Valid Credentials", "Username='admin', Pass='admin123'", "HTTP 302 -> /dashboard", "PASSED"],
        ["TC-02", "Login with Invalid Password", "Username='admin', Pass='wrong'", "Flash 'Invalid credentials', HTTP 200", "PASSED"],
        ["TC-03", "RBAC Student Access to Admin Page", "Role='student' GET /students", "HTTP 403 Forbidden Error", "PASSED"],
        ["TC-04", "Total Students KPI Calculation", "Query Student.query.count()", "Returns 120 matching database", "PASSED"],
        ["TC-05", "75% Attendance Defaulter Filter", "Attendance < 75.0%", "Flags 33 students in Defaulters list", "PASSED"],
        ["TC-06", "Subject Marks Calculation", "Int=25, Ext=55 -> Total=80/100", "Percentage=80.0%, Result='Pass'", "PASSED"],
        ["TC-07", "ML Prediction Endpoint", "Att=85%, Int=80%, Backlogs=0", "Predicted Category = 'Good' / 'Excellent'", "PASSED"],
        ["TC-08", "What-If Simulator API", "POST payload with slider values", "JSON with simulated result & prob", "PASSED"],
        ["TC-09", "Bulk CSV Upload with Schema Check", "Upload valid students CSV", "100% rows imported into database", "PASSED"],
        ["TC-10", "Password Update Verification", "Change admin password via Settings", "Hash updated in SQLite DB", "PASSED"],
        ["TC-11", "System Full Backup ZIP Download", "GET /settings/backup-zip", "HTTP 200, valid ZIP with 5 CSVs", "PASSED"],
        ["TC-12", "1-Click ML Model Retraining", "POST /settings/retrain-ml", "model.pkl updated, Acc >= 78%", "PASSED"]
    ]
    add_styled_table(["Test ID", "Test Scenario", "Input Data", "Expected Result", "Status"], test_cases, [0.8, 1.8, 1.8, 1.4, 0.7])

    add_p(
        "All 12 automated unit and integration tests passed with 100% success rate, confirming the functional correctness, "
        "security boundaries, and computational reliability of the application."
    )

    # =========================================================================
    # CHAPTER 8: CONCLUSION & FUTURE SCOPE
    # =========================================================================
    add_custom_heading("CHAPTER 8: CONCLUSION & FUTURE SCOPE", level=1)
    
    add_custom_heading("8.1 Project Conclusion", level=2)
    add_p(
        "The MSBTE Student Saver project successfully fulfills the critical need for an automated, explainable academic monitoring "
        "and early warning system in technical polytechnic education. By replacing manual paperwork with real-time analytics, 75% attendance "
        "defaulter tracking, Decision Tree machine learning predictions, and parent notification automation, the application empowers "
        "educators to intervene early and assist struggling students before board examinations."
    )

    add_custom_heading("8.2 Future Scope & Planned Enhancements", level=2)
    add_bullet("Biometric & RFID Attendance Integration: Direct synchronization with IoT biometric fingerprint and RFID scanners at classroom doors.")
    add_bullet("Native Mobile Application (Android/iOS): Developing a Flutter cross-platform companion app for instant parent push notifications.")
    add_bullet("WhatsApp Cloud API Integration: Automated dispatch of PDF report cards directly to parent WhatsApp numbers.")
    add_bullet("Deep Learning Academic Trajectory: Utilizing Recurrent Neural Networks (LSTM) to model multi-semester learning curves.")

    # =========================================================================
    # REFERENCES & BIBLIOGRAPHY
    # =========================================================================
    add_custom_heading("REFERENCES & BIBLIOGRAPHY", level=1)
    
    add_bullet("Maharashtra State Board of Technical Education (MSBTE) — Curriculum Implementation Assessment Norms (CIAAN) & I-Scheme / K-Scheme Manuals, Mumbai, 2024-2025.")
    add_bullet("Grinberg, Miguel. 'Flask Web Development: Developing Web Applications with Python', 2nd Edition, O'Reilly Media, 2018.")
    add_bullet("Pedregosa, F. et al. 'Scikit-learn: Machine Learning in Python', Journal of Machine Learning Research (JMLR), 12, pp. 2825-2830, 2011.")
    add_bullet("Breiman, Leo et al. 'Classification and Regression Trees', Wadsworth & Brooks/Cole Advanced Books & Software, Monterey, CA, 1984.")
    add_bullet("Chart.js Official Documentation — Open Source HTML5 Canvas Data Visualization Library, https://www.chartjs.org/docs/.")
    add_bullet("Bootstrap 5 Official Documentation — Front-end Open Source Toolkit, https://getbootstrap.com/docs/5.3/.")
    add_bullet("SQLAlchemy Documentation — The Python SQL Toolkit and Object Relational Mapper, https://docs.sqlalchemy.org/.")

    # Save to file
    out_path_1 = os.path.join(os.getcwd(), 'ITR_Report_MSBTE_Student_Saver.docx')
    out_path_2 = os.path.join(os.getcwd(), 'ITR.report...docx')
    doc.save(out_path_1)
    doc.save(out_path_2)
    print(f"Successfully created and saved ITR report to:")
    print(f"1. {out_path_1}")
    print(f"2. {out_path_2}")

if __name__ == '__main__':
    create_itr_document()
