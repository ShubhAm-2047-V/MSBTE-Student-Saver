import os
import random
from app import create_app
from models import db
from models.user import User
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from models.attendance import Attendance

app = create_app()

FIRST_NAMES = [
    "Aarav", "Sneha", "Rohan", "Priya", "Aditya", "Neha", "Rohit", "Ananya", "Tanvi", "Sahil",
    "Pooja", "Vikram", "Shreya", "Kunal", "Rutuja", "Omkar", "Divya", "Sanket", "Pranali", "Akash",
    "Gauri", "Tejas", "Sayali", "Prathamesh", "Komal", "Swapnil", "Meera", "Mayur", "Shraddha", "Harsh",
    "Kavita", "Siddhesh", "Nikita", "Aniket", "Samiksha", "Yash", "Ishita", "Atharva", "Pallavi", "Nikhil"
]

LAST_NAMES = [
    "Patil", "Deshmukh", "Kulkarni", "Shinde", "Joshi", "Jadhav", "Pawar", "Mehta", "Chavan", "Bhosale",
    "More", "Sawant", "Kadam", "Gaikwad", "Tambe", "Mane", "Wagh", "Bhide", "Sane", "Gore",
    "Shah", "Sharma", "Verma", "Gupta", "Naik", "Shetty", "Rane", "Pandey", "Tiwari", "Bhat"
]

DEMO_SUBJECTS = [
    # Semester 5 (Demo MSBTE Academic Structure)
    {
        "code": "22516",
        "name": "Operating Systems",
        "branch": "Computer Engineering",
        "semester": 5,
        "type": "Theory",
        "int_max": 30.0,
        "ext_max": 70.0,
        "prac_max": 0.0,
        "total_max": 100.0,
        "pass_marks": 40.0,
        "credits": 4
    },
    {
        "code": "22517",
        "name": "Advanced Java Programming",
        "branch": "Computer Engineering",
        "semester": 5,
        "type": "Theory + Practical",
        "int_max": 30.0,
        "ext_max": 70.0,
        "prac_max": 50.0,
        "total_max": 150.0,
        "pass_marks": 60.0,
        "credits": 5
    },
    {
        "code": "22518",
        "name": "Software Engineering",
        "branch": "Computer Engineering",
        "semester": 5,
        "type": "Theory",
        "int_max": 30.0,
        "ext_max": 70.0,
        "prac_max": 0.0,
        "total_max": 100.0,
        "pass_marks": 40.0,
        "credits": 4
    },
    {
        "code": "22519",
        "name": "Client Side Scripting Language",
        "branch": "Computer Engineering",
        "semester": 5,
        "type": "Practical/Lab",
        "int_max": 25.0,
        "ext_max": 0.0,
        "prac_max": 50.0,
        "total_max": 75.0,
        "pass_marks": 30.0,
        "credits": 3
    },
    {
        "code": "22520",
        "name": "Environmental Studies",
        "branch": "Computer Engineering",
        "semester": 5,
        "type": "Theory",
        "int_max": 30.0,
        "ext_max": 70.0,
        "prac_max": 0.0,
        "total_max": 100.0,
        "pass_marks": 40.0,
        "credits": 3
    },
    {
        "code": "22057",
        "name": "Capstone Project Planning",
        "branch": "Computer Engineering",
        "semester": 5,
        "type": "Project",
        "int_max": 25.0,
        "ext_max": 0.0,
        "prac_max": 25.0,
        "total_max": 50.0,
        "pass_marks": 20.0,
        "credits": 2
    },
    # Semester 6 (Demo MSBTE Academic Structure)
    {
        "code": "22616",
        "name": "Programming with Python",
        "branch": "Computer Engineering",
        "semester": 6,
        "type": "Theory + Practical",
        "int_max": 30.0,
        "ext_max": 70.0,
        "prac_max": 50.0,
        "total_max": 150.0,
        "pass_marks": 60.0,
        "credits": 5
    },
    {
        "code": "22617",
        "name": "Mobile Application Development",
        "branch": "Computer Engineering",
        "semester": 6,
        "type": "Theory + Practical",
        "int_max": 30.0,
        "ext_max": 70.0,
        "prac_max": 50.0,
        "total_max": 150.0,
        "pass_marks": 60.0,
        "credits": 5
    },
    {
        "code": "22618",
        "name": "Emerging Trends in Computer & IT",
        "branch": "Computer Engineering",
        "semester": 6,
        "type": "Theory",
        "int_max": 30.0,
        "ext_max": 70.0,
        "prac_max": 0.0,
        "total_max": 100.0,
        "pass_marks": 40.0,
        "credits": 4
    },
    {
        "code": "22619",
        "name": "Web Based Application using PHP",
        "branch": "Computer Engineering",
        "semester": 6,
        "type": "Practical/Lab",
        "int_max": 25.0,
        "ext_max": 0.0,
        "prac_max": 50.0,
        "total_max": 75.0,
        "pass_marks": 30.0,
        "credits": 3
    },
    {
        "code": "22058",
        "name": "Capstone Project Execution",
        "branch": "Computer Engineering",
        "semester": 6,
        "type": "Project",
        "int_max": 50.0,
        "ext_max": 0.0,
        "prac_max": 50.0,
        "total_max": 100.0,
        "pass_marks": 40.0,
        "credits": 4
    }
]

def seed_database(num_students=120):
    """Seed the SQLite database with realistic MSBTE diploma demo records."""
    random.seed(42)
    with app.app_context():
        # Clear existing tables
        db.drop_all()
        db.create_all()
        print("[DB] Tables created.")

        # 1. Create Admin Account
        admin = User(username='admin', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        print("[DB] Admin user created: admin / admin123")

        # 2. Create Demo Subjects
        created_subjects = []
        for s_data in DEMO_SUBJECTS:
            subj = Subject(
                subject_code=s_data["code"],
                subject_name=s_data["name"],
                branch=s_data["branch"],
                semester=s_data["semester"],
                subject_type=s_data["type"],
                internal_max=s_data["int_max"],
                external_max=s_data["ext_max"],
                practical_max=s_data["prac_max"],
                total_max=s_data["total_max"],
                passing_marks=s_data["pass_marks"],
                credits=s_data["credits"]
            )
            db.session.add(subj)
            created_subjects.append(subj)

        db.session.commit()
        print(f"[DB] {len(created_subjects)} Demo MSBTE Subjects created.")

        # 3. Create Demo Students
        sem5_subjects = [s for s in created_subjects if s.semester == 5]
        sem6_subjects = [s for s in created_subjects if s.semester == 6]

        created_students = []
        for i in range(1, num_students + 1):
            enrollment_no = f"230052{i:04d}"
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            name = f"{fname} {lname}"
            email = f"{fname.lower()}.{lname.lower()}{i}@polytechnic.edu.in"
            phone = f"98{random.randint(10000000, 99999999)}"
            
            # Semester distribution: 70% Sem 5, 30% Sem 6
            semester = 5 if i <= int(num_students * 0.70) else 6
            
            # Realistic academic baseline distribution
            rand_tier = random.random()
            if rand_tier < 0.20:
                # Top performers (Excellent: 85-95%)
                prev_pct = round(random.uniform(85.0, 96.0), 1)
                assign_pct = round(random.uniform(88.0, 98.0), 1)
                att_base = random.uniform(85.0, 96.0)
                perf_factor = 0.90
            elif rand_tier < 0.65:
                # Average to Good (65-84%)
                prev_pct = round(random.uniform(66.0, 84.0), 1)
                assign_pct = round(random.uniform(70.0, 85.0), 1)
                att_base = random.uniform(72.0, 88.0)
                perf_factor = 0.75
            elif rand_tier < 0.85:
                # Needs Improvement (50-64%)
                prev_pct = round(random.uniform(50.0, 64.0), 1)
                assign_pct = round(random.uniform(55.0, 68.0), 1)
                att_base = random.uniform(60.0, 74.0)
                perf_factor = 0.58
            else:
                # At Risk (<50%)
                prev_pct = round(random.uniform(36.0, 48.0), 1)
                assign_pct = round(random.uniform(40.0, 52.0), 1)
                att_base = random.uniform(42.0, 62.0)
                perf_factor = 0.42

            student = Student(
                enrollment_no=enrollment_no,
                name=name,
                branch="Computer Engineering",
                semester=semester,
                academic_year="2025-2026",
                email=email,
                phone=phone,
                admission_year=2023,
                previous_percentage=prev_pct,
                assignment_percentage=assign_pct
            )
            db.session.add(student)
            db.session.flush()  # to get student.id

            # Create student user account
            user = User(
                username=enrollment_no,
                role='student',
                student_id=student.id
            )
            user.set_password(f"stud@{enrollment_no[-4:]}")
            db.session.add(user)

            # 4. Create Marks and Attendance for Semester subjects
            active_subjects = sem5_subjects if semester == 5 else sem6_subjects
            for subj in active_subjects:
                # Compute realistic marks based on performance tier
                noise = random.uniform(-0.08, 0.08)
                score_ratio = max(0.20, min(0.98, perf_factor + noise))

                internal = round(subj.internal_max * score_ratio, 1) if subj.internal_max > 0 else 0.0
                external = round(subj.external_max * score_ratio, 1) if subj.external_max > 0 else 0.0
                practical = round(subj.practical_max * score_ratio, 1) if subj.practical_max > 0 else 0.0

                marks_rec = Marks(
                    student_id=student.id,
                    subject_id=subj.id,
                    internal_marks=internal,
                    external_marks=external,
                    practical_marks=practical
                )
                marks_rec.calculate_total_and_result(subj)
                db.session.add(marks_rec)

                # Compute realistic attendance
                total_classes = random.choice([48, 50, 52, 56])
                att_noise = random.uniform(-6.0, 6.0)
                att_ratio = max(0.35, min(0.98, (att_base + att_noise) / 100.0))
                attended_classes = int(round(total_classes * att_ratio))

                att_rec = Attendance(
                    student_id=student.id,
                    subject_id=subj.id,
                    total_classes=total_classes,
                    attended_classes=attended_classes
                )
                att_rec.calculate_percentage_and_status()
                db.session.add(att_rec)

            created_students.append(student)

        db.session.commit()
        print(f"[DB] {len(created_students)} Students and associated records seeded successfully.")

if __name__ == '__main__':
    seed_database()
