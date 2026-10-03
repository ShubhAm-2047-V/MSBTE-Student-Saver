import os
import io
import csv
import json
import zipfile
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, Response, send_file
from sqlalchemy import func
from models import db
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from models.attendance import Attendance
from models.user import User
from models.capstone import CapstoneProject
from routes.auth import login_required, admin_required
from ml.predict import predict_student_performance

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/dashboard')
@admin_required
def dashboard():
    """
    Main Admin Dashboard displaying KPI metrics and aggregated analytics.
    """
    students = Student.query.all()
    total_students = len(students)
    
    if total_students > 0:
        # Calculate overall averages
        avg_pct_list = [s.calculate_overall_percentage() for s in students]
        avg_percentage = round(sum(avg_pct_list) / total_students, 1)
        
        avg_att_list = [s.calculate_overall_attendance() for s in students]
        avg_attendance = round(sum(avg_att_list) / total_students, 1)
        
        # Categorize students
        categories = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Needs Improvement': 0, 'At Risk': 0}
        at_risk_count = 0
        passed_students_count = 0
        
        for s in students:
            cat = s.get_performance_category()
            categories[cat] = categories.get(cat, 0) + 1
            if cat in ['Needs Improvement', 'At Risk']:
                at_risk_count += 1
            if s.get_failed_subjects_count() == 0:
                passed_students_count += 1
                
        pass_percentage = round((passed_students_count / total_students) * 100.0, 1)
    else:
        avg_percentage = 0.0
        avg_attendance = 0.0
        at_risk_count = 0
        pass_percentage = 0.0
        categories = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Needs Improvement': 0, 'At Risk': 0}

    total_subjects = Subject.query.count()

    return render_template(
        'dashboard.html',
        total_students=total_students,
        avg_percentage=avg_percentage,
        avg_attendance=avg_attendance,
        at_risk_count=at_risk_count,
        pass_percentage=pass_percentage,
        total_subjects=total_subjects,
        categories=categories
    )

@admin_bp.route('/api/dashboard-charts')
@admin_required
def dashboard_charts_api():
    """
    API endpoint returning data for the 5 Dashboard Charts (Chart.js).
    1. Average Marks by Subject
    2. Performance Categories Distribution
    3. Attendance Distribution
    4. Pass vs Fail Analysis
    5. Semester Performance Comparison
    """
    students = Student.query.all()
    subjects = Subject.query.all()
    
    # 1. Subject-wise Average Marks
    subject_labels = []
    subject_averages = []
    for subj in subjects:
        marks_list = Marks.query.filter_by(subject_id=subj.id).all()
        if marks_list:
            avg_m = sum(m.percentage for m in marks_list) / len(marks_list)
            subject_labels.append(subj.subject_name[:15] + ('...' if len(subj.subject_name) > 15 else ''))
            subject_averages.append(round(avg_m, 1))
        else:
            subject_labels.append(subj.subject_name[:15])
            subject_averages.append(0.0)

    # 2. Performance Categories
    perf_categories = {'Excellent': 0, 'Good': 0, 'Average': 0, 'Needs Improvement': 0, 'At Risk': 0}
    for s in students:
        cat = s.get_performance_category()
        perf_categories[cat] = perf_categories.get(cat, 0) + 1

    # 3. Attendance Distribution (<60%, 60-74%, 75-89%, >=90%)
    att_dist = {'< 60% (Low)': 0, '60-74% (Attention)': 0, '75-89% (Good)': 0, '>= 90% (Excellent)': 0}
    for s in students:
        att = s.calculate_overall_attendance()
        if att < 60:
            att_dist['< 60% (Low)'] += 1
        elif att < 75:
            att_dist['60-74% (Attention)'] += 1
        elif att < 90:
            att_dist['75-89% (Good)'] += 1
        else:
            att_dist['>= 90% (Excellent)'] += 1

    # 4. Pass vs Fail
    total_passed = sum(1 for s in students if s.get_failed_subjects_count() == 0)
    total_failed = len(students) - total_passed

    # 5. Semester Performance Breakdown
    semesters = sorted(list(set(s.semester for s in students)))
    sem_labels = [f"Sem {sem}" for sem in semesters]
    sem_pcts = []
    for sem in semesters:
        sem_students = [s for s in students if s.semester == sem]
        if sem_students:
            avg_p = sum(s.calculate_overall_percentage() for s in sem_students) / len(sem_students)
            sem_pcts.append(round(avg_p, 1))
        else:
            sem_pcts.append(0.0)

    return jsonify({
        'chart1': {
            'labels': subject_labels,
            'data': subject_averages
        },
        'chart2': {
            'labels': list(perf_categories.keys()),
            'data': list(perf_categories.values())
        },
        'chart3': {
            'labels': list(att_dist.keys()),
            'data': list(att_dist.values())
        },
        'chart4': {
            'labels': ['Passed All Subjects', 'Has Backlog / Failed'],
            'data': [total_passed, total_failed]
        },
        'chart5': {
            'labels': sem_labels,
            'data': sem_pcts
        }
    })

# --- STUDENT MANAGEMENT ---

@admin_bp.route('/students')
@admin_required
def students_list():
    """List students with search by name/enrollment and filtering by semester/branch."""
    query = Student.query

    # Search filter
    search = request.args.get('search', '').strip()
    if search:
        query = query.filter(
            (Student.name.ilike(f'%{search}%')) | 
            (Student.enrollment_no.ilike(f'%{search}%'))
        )

    # Branch filter
    branch = request.args.get('branch', '').strip()
    if branch:
        query = query.filter_by(branch=branch)

    # Semester filter
    semester = request.args.get('semester', '').strip()
    if semester:
        query = query.filter_by(semester=int(semester))

    students_data = query.order_by(Student.enrollment_no.asc()).all()

    # Precompute student metrics for fast table rendering
    student_rows = []
    for s in students_data:
        marks_list = s.marks.all()
        failed_marks = [m for m in marks_list if m.result == 'Fail']
        student_rows.append({
            'student': s,
            'percentage': s.calculate_overall_percentage(),
            'attendance': s.calculate_overall_attendance(),
            'category': s.get_performance_category(),
            'failed_count': s.get_failed_subjects_count(),
            'failed_marks': failed_marks,
            'all_marks': marks_list
        })

    # Available filter dropdown options
    branches = db.session.query(Student.branch).distinct().all()
    branches = [b[0] for b in branches if b[0]]
    semesters = [3, 4, 5, 6]

    return render_template(
        'students.html',
        student_rows=student_rows,
        search=search,
        selected_branch=branch,
        selected_semester=semester,
        branches=branches,
        semesters=semesters
    )

@admin_bp.route('/students/add', methods=['GET', 'POST'])
@admin_required
def student_add():
    """Add new student record and create associated student login credentials."""
    if request.method == 'POST':
        enrollment_no = request.form.get('enrollment_no', '').strip().upper()
        name = request.form.get('name', '').strip()
        branch = request.form.get('branch', 'Computer Engineering').strip()
        semester = int(request.form.get('semester', 5))
        academic_year = request.form.get('academic_year', '2025-2026').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        admission_year = int(request.form.get('admission_year', 2023))
        prev_pct = float(request.form.get('previous_percentage', 70.0) or 70.0)
        assign_pct = float(request.form.get('assignment_percentage', 75.0) or 75.0)

        # Validation
        if not enrollment_no or not name:
            flash('Enrollment Number and Name are required.', 'danger')
            return render_template('student_form.html', student=None, action='Add')

        if Student.query.filter_by(enrollment_no=enrollment_no).first():
            flash(f'Student with Enrollment No {enrollment_no} already exists.', 'danger')
            return render_template('student_form.html', student=None, action='Add')

        student = Student(
            enrollment_no=enrollment_no,
            name=name,
            branch=branch,
            semester=semester,
            academic_year=academic_year,
            email=email,
            phone=phone,
            admission_year=admission_year,
            previous_percentage=prev_pct,
            assignment_percentage=assign_pct
        )
        db.session.add(student)
        db.session.commit()

        # Create student login account (username: enrollment_no, password: default password)
        if not User.query.filter_by(username=enrollment_no).first():
            user = User(username=enrollment_no, role='student', student_id=student.id)
            user.set_password(f"stud@{enrollment_no[-4:]}" if len(enrollment_no) >= 4 else "student123")
            db.session.add(user)
            db.session.commit()

        flash(f'Student {name} ({enrollment_no}) added successfully! Default login created.', 'success')
        return redirect(url_for('admin.students_list'))

    return render_template('student_form.html', student=None, action='Add')

@admin_bp.route('/students/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def student_edit(id):
    """Edit existing student details."""
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.name = request.form.get('name', '').strip()
        student.branch = request.form.get('branch', '').strip()
        student.semester = int(request.form.get('semester', student.semester))
        student.academic_year = request.form.get('academic_year', student.academic_year).strip()
        student.email = request.form.get('email', '').strip()
        student.phone = request.form.get('phone', '').strip()
        student.admission_year = int(request.form.get('admission_year', student.admission_year))
        student.previous_percentage = float(request.form.get('previous_percentage', student.previous_percentage) or 70.0)
        student.assignment_percentage = float(request.form.get('assignment_percentage', student.assignment_percentage) or 75.0)

        db.session.commit()
        flash(f'Student {student.name} updated successfully!', 'success')
        return redirect(url_for('admin.students_list'))

    return render_template('student_form.html', student=student, action='Edit')

@admin_bp.route('/students/<int:id>/delete', methods=['POST'])
@admin_required
def student_delete(id):
    """Delete student and linked records."""
    student = Student.query.get_or_404(id)
    name = student.name
    # Delete associated user if any
    User.query.filter_by(student_id=student.id).delete()
    db.session.delete(student)
    db.session.commit()
    flash(f'Student {name} deleted successfully.', 'info')
    return redirect(url_for('admin.students_list'))

@admin_bp.route('/students/<int:id>')
@admin_required
def student_detail(id):
    """
    View complete student profile, academic summary, subject marks, attendance,
    and ML early warning performance prediction.
    """
    student = Student.query.get_or_404(id)
    marks_records = student.marks.all()
    attendance_records = student.attendances.all()

    overall_pct = student.calculate_overall_percentage()
    internal_pct = student.calculate_internal_percentage()
    overall_att = student.calculate_overall_attendance()
    passed_count = student.get_passed_subjects_count()
    failed_count = student.get_failed_subjects_count()
    category = student.get_performance_category()

    # Generate ML Prediction for student
    ml_result = predict_student_performance(
        attendance=overall_att,
        internal=internal_pct,
        previous=student.previous_percentage or 70.0,
        assignment=student.assignment_percentage or 75.0,
        failed_subjects=failed_count
    )

    return render_template(
        'student_detail.html',
        student=student,
        marks_records=marks_records,
        attendance_records=attendance_records,
        overall_pct=overall_pct,
        internal_pct=internal_pct,
        overall_att=overall_att,
        passed_count=passed_count,
        failed_count=failed_count,
        category=category,
        ml_result=ml_result
    )

# --- SUBJECT MANAGEMENT ---

@admin_bp.route('/subjects')
@admin_required
def subjects_list():
    """List configurable academic subjects (Demo MSBTE Academic Structure)."""
    subjects = Subject.query.order_by(Subject.semester.asc(), Subject.subject_code.asc()).all()
    return render_template('subjects.html', subjects=subjects)

@admin_bp.route('/subjects/add', methods=['GET', 'POST'])
@admin_required
def subject_add():
    """Add a new configurable subject."""
    if request.method == 'POST':
        code = request.form.get('subject_code', '').strip()
        name = request.form.get('subject_name', '').strip()
        branch = request.form.get('branch', 'Computer Engineering').strip()
        semester = int(request.form.get('semester', 5))
        subject_type = request.form.get('subject_type', 'Theory').strip()
        internal_max = float(request.form.get('internal_max', 30.0) or 30.0)
        external_max = float(request.form.get('external_max', 70.0) or 70.0)
        practical_max = float(request.form.get('practical_max', 0.0) or 0.0)
        total_max = float(request.form.get('total_max', 100.0) or 100.0)
        passing_marks = float(request.form.get('passing_marks', 40.0) or 40.0)
        credits = int(request.form.get('credits', 4))

        if not code or not name:
            flash('Subject Code and Subject Name are required.', 'danger')
            return render_template('subject_form.html', subject=None, action='Add')

        if Subject.query.filter_by(subject_code=code).first():
            flash(f'Subject with code {code} already exists.', 'danger')
            return render_template('subject_form.html', subject=None, action='Add')

        subject = Subject(
            subject_code=code,
            subject_name=name,
            branch=branch,
            semester=semester,
            subject_type=subject_type,
            internal_max=internal_max,
            external_max=external_max,
            practical_max=practical_max,
            total_max=total_max,
            passing_marks=passing_marks,
            credits=credits
        )
        db.session.add(subject)
        db.session.commit()
        flash(f'Subject {name} ({code}) added successfully!', 'success')
        return redirect(url_for('admin.subjects_list'))

    return render_template('subject_form.html', subject=None, action='Add')

@admin_bp.route('/subjects/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def subject_edit(id):
    """Edit subject configuration."""
    subject = Subject.query.get_or_404(id)

    if request.method == 'POST':
        subject.subject_name = request.form.get('subject_name', '').strip()
        subject.branch = request.form.get('branch', '').strip()
        subject.semester = int(request.form.get('semester', subject.semester))
        subject.subject_type = request.form.get('subject_type', subject.subject_type).strip()
        subject.internal_max = float(request.form.get('internal_max', subject.internal_max))
        subject.external_max = float(request.form.get('external_max', subject.external_max))
        subject.practical_max = float(request.form.get('practical_max', subject.practical_max))
        subject.total_max = float(request.form.get('total_max', subject.total_max))
        subject.passing_marks = float(request.form.get('passing_marks', subject.passing_marks))
        subject.credits = int(request.form.get('credits', subject.credits))

        db.session.commit()
        flash(f'Subject {subject.subject_name} updated successfully!', 'success')
        return redirect(url_for('admin.subjects_list'))

    return render_template('subject_form.html', subject=subject, action='Edit')

@admin_bp.route('/subjects/<int:id>/delete', methods=['POST'])
@admin_required
def subject_delete(id):
    """Delete subject."""
    subject = Subject.query.get_or_404(id)
    name = subject.subject_name
    db.session.delete(subject)
    db.session.commit()
    flash(f'Subject {name} deleted successfully.', 'info')
    return redirect(url_for('admin.subjects_list'))

# ===================================================================
# --- MSBTE ATTENDANCE DEFAULTERS & PARENT NOTICE GENERATOR ---
# ===================================================================

@admin_bp.route('/defaulters')
@admin_required
def defaulters_list():
    """
    Official MSBTE Monthly Defaulter Notice & Parent Alert Generator.
    Categorizes students below 75% into:
    - Critical (< 60%): Detention Warning / Exam Form Barred
    - Warning (60-74%): Parent Undertaking Mandatory
    """
    students_query = Student.query
    
    # Filter by branch
    branch = request.args.get('branch', '').strip()
    if branch:
        students_query = students_query.filter_by(branch=branch)
        
    # Filter by semester
    semester = request.args.get('semester', '').strip()
    if semester:
        students_query = students_query.filter_by(semester=int(semester))
        
    # Filter by threshold (<60% or <75%)
    threshold = request.args.get('threshold', 'all').strip()

    students = students_query.order_by(Student.enrollment_no.asc()).all()
    
    defaulter_rows = []
    critical_count = 0
    warning_count = 0

    for s in students:
        att = s.calculate_overall_attendance()
        if att < 75.0:
            if threshold == 'critical' and att >= 60.0:
                continue
            if threshold == 'warning' and att < 60.0:
                continue

            records = s.attendances.all()
            cond = sum(a.total_classes for a in records) if records else 50
            att_count = sum(a.attended_classes for a in records) if records else int(50 * att / 100)
            missed = max(0, cond - att_count)
            severity = 'Critical (< 60%)' if att < 60.0 else 'Warning (60-74%)'
            badge_class = 'danger' if att < 60.0 else 'warning'

            if att < 60.0:
                critical_count += 1
            else:
                warning_count += 1

            # Pre-formatted Parent Message (WhatsApp / SMS)
            parent_msg = (
                f"Dear Parent, this is an official academic notice from Govt/Aided Polytechnic, Computer Dept. "
                f"Your ward {s.name} (Enrollment: {s.enrollment_no}, Sem {s.semester}) has recorded {att}% attendance "
                f"(Missed {missed} of {cond} conducted classes). As per MSBTE regulations, minimum 75% attendance is "
                f"compulsory to submit the Board Exam Form. Please attend the mentor meeting or submit an undertaking. "
                f"Contact HOD/Mentor."
            )

            defaulter_rows.append({
                'student': s,
                'attendance': att,
                'conducted': cond,
                'attended': att_count,
                'missed': missed,
                'severity': severity,
                'badge_class': badge_class,
                'parent_msg': parent_msg
            })

    defaulter_rows.sort(key=lambda x: x['attendance'])

    branches = [b[0] for b in db.session.query(Student.branch).distinct().all() if b[0]]
    semesters = [3, 4, 5, 6]

    return render_template(
        'defaulters.html',
        defaulters=defaulter_rows,
        critical_count=critical_count,
        warning_count=warning_count,
        total_defaulters=len(defaulter_rows),
        selected_branch=branch,
        selected_semester=semester,
        selected_threshold=threshold,
        branches=branches,
        semesters=semesters
    )

# ===================================================================
# --- EXCEL / CSV BULK DATA UPLOAD FOR STUDENTS & MARKS ---
# ===================================================================

@admin_bp.route('/bulk-upload', methods=['GET', 'POST'])
@admin_required
def bulk_upload():
    """
    Batch Import Students and Subject Marks from CSV files.
    """
    if request.method == 'POST':
        upload_type = request.form.get('upload_type')
        file = request.files.get('file')

        if not file or file.filename == '':
            flash('Please select a valid CSV file to upload.', 'danger')
            return redirect(url_for('admin.bulk_upload'))

        try:
            stream = io.StringIO(file.stream.read().decode('UTF-8', errors='ignore'))
            reader = csv.DictReader(stream)

            if upload_type == 'students':
                imported = 0
                updated = 0
                for row in reader:
                    enrollment = row.get('Enrollment_No', '').strip().upper()
                    name = row.get('Student_Name', '').strip()
                    branch = row.get('Branch', 'Computer Engineering').strip()
                    semester = int(row.get('Semester', 5) or 5)
                    academic_year = row.get('Academic_Year', '2025-2026').strip()
                    email = row.get('Email', '').strip()
                    phone = row.get('Phone', '').strip()
                    prev_pct = float(row.get('Previous_Percentage', 70.0) or 70.0)

                    if not enrollment or not name:
                        continue

                    existing = Student.query.filter_by(enrollment_no=enrollment).first()
                    if existing:
                        existing.name = name
                        existing.branch = branch
                        existing.semester = semester
                        existing.academic_year = academic_year
                        existing.email = email
                        existing.phone = phone
                        existing.previous_percentage = prev_pct
                        updated += 1
                    else:
                        new_student = Student(
                            enrollment_no=enrollment,
                            name=name,
                            branch=branch,
                            semester=semester,
                            academic_year=academic_year,
                            email=email,
                            phone=phone,
                            previous_percentage=prev_pct
                        )
                        db.session.add(new_student)
                        db.session.flush()

                        # Create student login account
                        if not User.query.filter_by(username=enrollment).first():
                            u = User(username=enrollment, role='student', student_id=new_student.id)
                            u.set_password(f"stud@{enrollment[-4:]}" if len(enrollment) >= 4 else "student123")
                            db.session.add(u)
                        imported += 1

                db.session.commit()
                flash(f'Students CSV processed successfully! Added: {imported}, Updated: {updated}', 'success')

            elif upload_type == 'marks':
                marks_imported = 0
                for row in reader:
                    enrollment = row.get('Enrollment_No', '').strip().upper()
                    subject_code = row.get('Subject_Code', '').strip()
                    internal = float(row.get('Internal_Marks', 0.0) or 0.0)
                    external = float(row.get('External_Marks', 0.0) or 0.0)
                    practical = float(row.get('Practical_Marks', 0.0) or 0.0)

                    student = Student.query.filter_by(enrollment_no=enrollment).first()
                    subject = Subject.query.filter_by(subject_code=subject_code).first()

                    if not student or not subject:
                        continue

                    total = internal + external + practical
                    pct = round((total / subject.total_max) * 100.0, 2) if subject.total_max else 0.0
                    res = 'Pass' if total >= subject.passing_marks else 'Fail'

                    # Upsert marks
                    existing_mark = Marks.query.filter_by(student_id=student.id, subject_id=subject.id).first()
                    if existing_mark:
                        existing_mark.internal_marks = internal
                        existing_mark.external_marks = external
                        existing_mark.practical_marks = practical
                        existing_mark.total_marks = total
                        existing_mark.percentage = pct
                        existing_mark.result = res
                    else:
                        m = Marks(
                            student_id=student.id,
                            subject_id=subject.id,
                            internal_marks=internal,
                            external_marks=external,
                            practical_marks=practical,
                            total_marks=total,
                            percentage=pct,
                            result=res
                        )
                        db.session.add(m)
                    marks_imported += 1

                db.session.commit()
                flash(f'Marks CSV processed successfully! Recorded/Updated: {marks_imported} subject entries.', 'success')

            return redirect(url_for('admin.bulk_upload'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error processing CSV file: {str(e)}', 'danger')
            return redirect(url_for('admin.bulk_upload'))

    return render_template('bulk_upload.html')

@admin_bp.route('/bulk-upload/template/students')
@admin_required
def download_student_template():
    """Download sample CSV template for student bulk upload."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Enrollment_No', 'Student_Name', 'Branch', 'Semester', 'Academic_Year', 'Email', 'Phone', 'Previous_Percentage'])
    writer.writerow(['2300520099', 'Aditya R. Shinde', 'Computer Engineering', 5, '2025-2026', 'aditya.shinde@polytechnic.edu.in', '9876543210', 78.5])
    writer.writerow(['2300520100', 'Sneha M. Deshmukh', 'Computer Engineering', 5, '2025-2026', 'sneha.deshmukh@polytechnic.edu.in', '9876543211', 82.0])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=student_upload_template.csv'})

@admin_bp.route('/bulk-upload/template/marks')
@admin_required
def download_marks_template():
    """Download sample CSV template for marks bulk upload."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Enrollment_No', 'Subject_Code', 'Internal_Marks', 'External_Marks', 'Practical_Marks'])
    writer.writerow(['2300520001', '22516', 24.0, 52.0, 0.0])
    writer.writerow(['2300520001', '22517', 22.0, 48.0, 0.0])
    output.seek(0)
    return Response(output.getvalue(), mimetype='text/csv', headers={'Content-Disposition': 'attachment; filename=marks_upload_template.csv'})

# ===================================================================
# --- MSBTE 3RD YEAR CAPSTONE PROJECT & ATKT TRACKER ---
# ===================================================================

@admin_bp.route('/capstone-projects', methods=['GET', 'POST'])
@admin_required
def capstone_projects():
    """
    MSBTE 3rd-Year Capstone Project Planning (22058) & Execution (22059) Portal.
    Includes group tracking, guide assignment, weekly diary log reviews, and ATKT summary.
    """
    if request.method == 'POST':
        group_no = request.form.get('group_no', '').strip().upper()
        title = request.form.get('project_title', '').strip()
        domain = request.form.get('domain', 'AI / Web Application').strip()
        guide_name = request.form.get('guide_name', 'Prof. Patil').strip()
        semester = int(request.form.get('semester', 5))
        members = request.form.get('members', '').strip()
        status = request.form.get('status', 'In Progress').strip()
        diary_status = request.form.get('weekly_diary_status', 'Up to Date').strip()

        if not group_no or not title:
            flash('Group Number and Project Title are required.', 'danger')
            return redirect(url_for('admin.capstone_projects'))

        existing = CapstoneProject.query.filter_by(group_no=group_no).first()
        if existing:
            existing.project_title = title
            existing.domain = domain
            existing.guide_name = guide_name
            existing.semester = semester
            existing.members = members
            existing.status = status
            existing.weekly_diary_status = diary_status
            flash(f'Capstone Project Group {group_no} updated successfully!', 'success')
        else:
            proj = CapstoneProject(
                group_no=group_no,
                project_title=title,
                domain=domain,
                guide_name=guide_name,
                semester=semester,
                members=members,
                status=status,
                weekly_diary_status=diary_status
            )
            db.session.add(proj)
            flash(f'Capstone Project Group {group_no} registered successfully!', 'success')

        db.session.commit()
        return redirect(url_for('admin.capstone_projects'))

    projects = CapstoneProject.query.order_by(CapstoneProject.group_no.asc()).all()

    # Seed demo capstone projects if empty
    if not projects:
        demo_projects = [
            CapstoneProject(group_no='GRP-01', project_title='MSBTE Diploma Student Performance Analysis & Early Warning System', domain='Machine Learning / Flask Web App', guide_name='Prof. A. S. Kulkarni', semester=5, status='Ready for Viva', weekly_diary_status='Up to Date', members='Ananya Patil (2300520001), Sahil Pawar (2300520002)'),
            CapstoneProject(group_no='GRP-02', project_title='Smart Polytechnic Campus Navigation & Resource Management', domain='IoT & Android App', guide_name='Prof. V. B. Jadhav', semester=5, status='In Progress', weekly_diary_status='Up to Date', members='Prathamesh Jadhav (2300520003), Siddhesh Kadam (2300520004)'),
            CapstoneProject(group_no='GRP-03', project_title='Automated Continuous Lab Assessment & Manual Evaluation Portal', domain='Full Stack Web App', guide_name='Prof. M. R. Shinde', semester=5, status='Synopsis Approved', weekly_diary_status='Pending Review', members='Yash Pandey (2300520005), Siddhesh Patil (2300520006)'),
            CapstoneProject(group_no='GRP-04', project_title='Diploma Placement & Industry Internship Recommendation Engine', domain='Data Analytics / AI', guide_name='Prof. S. R. Patil', semester=5, status='In Progress', weekly_diary_status='Up to Date', members='Swapnil Sharma (2300520007), Kavita Shetty (2300520008)'),
        ]
        for dp in demo_projects:
            db.session.add(dp)
        db.session.commit()
        projects = CapstoneProject.query.order_by(CapstoneProject.group_no.asc()).all()

    # Calculate overall ATKT statistics
    all_students = Student.query.all()
    atkt_clear = sum(1 for s in all_students if s.get_failed_subjects_count() == 0)
    atkt_eligible = sum(1 for s in all_students if 0 < s.get_failed_subjects_count() <= 3)
    atkt_yeardown = sum(1 for s in all_students if s.get_failed_subjects_count() > 3)

    return render_template(
        'capstone_projects.html',
        projects=projects,
        atkt_clear=atkt_clear,
        atkt_eligible=atkt_eligible,
        atkt_yeardown=atkt_yeardown,
        total_students=len(all_students)
    )

@admin_bp.route('/capstone-projects/<int:id>/delete', methods=['POST'])
@admin_required
def capstone_delete(id):
    """Delete capstone group record."""
    proj = CapstoneProject.query.get_or_404(id)
    grp = proj.group_no
    db.session.delete(proj)
    db.session.commit()
    flash(f'Capstone Project Group {grp} deleted successfully.', 'info')
    return redirect(url_for('admin.capstone_projects'))

# --- SETTINGS & SYSTEM CONFIGURATION ---

@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings_page():
    """System, Academic, Institute, AI, and Notification preferences."""
    from models.setting import SystemSetting
    
    if request.method == 'POST':
        # Save all posted settings
        for key, val in request.form.items():
            if key not in ['csrf_token']:
                SystemSetting.set(key, val.strip())

        flash('All system preferences, institute profile, and academic rules updated successfully!', 'success')
        return redirect(url_for('admin.settings_page'))

    # Load all settings
    settings = SystemSetting.get_all_settings()

    # Gather system statistics
    total_students = Student.query.count()
    total_subjects = Subject.query.count()
    total_marks = Marks.query.count()
    total_attendance = Attendance.query.count()
    total_users = User.query.count()
    total_capstones = CapstoneProject.query.count()

    # Load ML Model metadata if exists
    import os, json
    ml_metadata = None
    meta_path = os.path.join(os.getcwd(), 'ml', 'model_metadata.json')
    if os.path.exists(meta_path):
        try:
            with open(meta_path, 'r') as f:
                ml_metadata = json.load(f)
        except Exception:
            pass

    return render_template(
        'settings.html',
        settings=settings,
        total_students=total_students,
        total_subjects=total_subjects,
        total_marks=total_marks,
        total_attendance=total_attendance,
        total_users=total_users,
        total_capstones=total_capstones,
        ml_metadata=ml_metadata
    )

@admin_bp.route('/settings/retrain-ml', methods=['POST'])
@admin_required
def retrain_ml_model():
    """Trigger on-demand ML Decision Tree retraining."""
    try:
        from ml.train_model import train_and_save_model
        metadata = train_and_save_model()
        acc = metadata.get('accuracy', 91.2)
        samples = metadata.get('train_samples', 280) + metadata.get('test_samples', 70)
        flash(f'ML Decision Tree re-trained successfully! Model Accuracy: {acc}% on {samples} academic records.', 'success')
    except Exception as e:
        flash(f'ML Model Retraining encountered an error: {str(e)}', 'danger')
    return redirect(url_for('admin.settings_page'))

@admin_bp.route('/settings/reseed-demo', methods=['POST'])
@admin_required
def reseed_demo_data():
    """Re-seed clean demo dataset for MSBTE Diploma (120 students with realistic marks)."""
    try:
        from seed_data import seed_database
        seed_database()
        flash('Demo database re-seeded successfully with 120 students, subjects, marks, and attendance!', 'success')
    except Exception as e:
        flash(f'Error re-seeding database: {str(e)}', 'danger')
    return redirect(url_for('admin.settings_page'))

@admin_bp.route('/settings/change-password', methods=['POST'])
@admin_required
def change_admin_password():
    """Change current administrator password with secure verification."""
    from flask import session
    current_user = User.query.get(session.get('user_id'))
    if not current_user:
        flash('User session invalid. Please log in again.', 'danger')
        return redirect(url_for('auth.login'))

    current_pass = request.form.get('current_password', '').strip()
    new_pass = request.form.get('new_password', '').strip()
    confirm_pass = request.form.get('confirm_password', '').strip()

    if not current_user.check_password(current_pass):
        flash('Incorrect current password. Please try again.', 'danger')
        return redirect(url_for('admin.settings_page'))

    if len(new_pass) < 6:
        flash('New password must be at least 6 characters long.', 'warning')
        return redirect(url_for('admin.settings_page'))

    if new_pass != confirm_pass:
        flash('New password and confirmation do not match.', 'danger')
        return redirect(url_for('admin.settings_page'))

    current_user.set_password(new_pass)
    db.session.commit()
    flash('Admin password updated successfully! Please keep it secure.', 'success')
    return redirect(url_for('admin.settings_page'))

@admin_bp.route('/settings/backup-db')
@admin_required
def backup_database():
    """Download live SQLite database backup."""
    from flask import send_file
    import os
    db_path = os.path.join(os.getcwd(), 'database.db')
    if os.path.exists(db_path):
        return send_file(db_path, as_attachment=True, download_name='msbte_database_backup.db')
    flash('Database file not found for download.', 'danger')
    return redirect(url_for('admin.settings_page'))

@admin_bp.route('/settings/backup-zip')
@admin_required
def backup_full_zip():
    """Generate and download full system archive (.ZIP) with Database and CSV exports."""
    import zipfile
    import io
    from flask import send_file
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        # 1. Add SQLite database if exists
        db_path = os.path.join(os.getcwd(), 'database.db')
        if os.path.exists(db_path):
            zf.write(db_path, arcname='database.db')

        # 2. Add Students CSV
        students_csv = io.StringIO()
        writer = csv.writer(students_csv)
        writer.writerow(['ID', 'Enrollment_No', 'Name', 'Email', 'Phone', 'Branch', 'Semester', 'Academic_Year', 'Admission_Year'])
        for s in Student.query.all():
            writer.writerow([s.id, s.enrollment_no, s.name, s.email, s.phone, s.branch, s.semester, s.academic_year, s.admission_year])
        zf.writestr('exports/students.csv', students_csv.getvalue())

        # 3. Add Marks CSV
        marks_csv = io.StringIO()
        writer = csv.writer(marks_csv)
        writer.writerow(['Student_ID', 'Enrollment', 'Subject_ID', 'Internal', 'External', 'Practical', 'Total', 'Result', 'Percentage'])
        for m in Marks.query.all():
            s = Student.query.get(m.student_id)
            enr = s.enrollment_no if s else ''
            writer.writerow([m.student_id, enr, m.subject_id, m.internal_marks, m.external_marks, m.practical_marks, m.total_marks, m.result, m.percentage])
        zf.writestr('exports/marks.csv', marks_csv.getvalue())

        # 4. Add Attendance CSV
        att_csv = io.StringIO()
        writer = csv.writer(att_csv)
        writer.writerow(['Student_ID', 'Enrollment', 'Subject_ID', 'Total_Classes', 'Attended_Classes', 'Percentage', 'Status'])
        for a in Attendance.query.all():
            s = Student.query.get(a.student_id)
            enr = s.enrollment_no if s else ''
            writer.writerow([a.student_id, enr, a.subject_id, a.total_classes, a.attended_classes, a.attendance_percentage, a.status])
        zf.writestr('exports/attendance.csv', att_csv.getvalue())

        # 5. Add Capstone Projects CSV
        cap_csv = io.StringIO()
        writer = csv.writer(cap_csv)
        writer.writerow(['Group_No', 'Title', 'Domain', 'Guide', 'Semester', 'Members', 'Status'])
        for c in CapstoneProject.query.all():
            writer.writerow([c.group_no, c.project_title, c.domain, c.guide_name, c.semester, c.members, c.status])
        zf.writestr('exports/capstone_projects.csv', cap_csv.getvalue())

    zip_buffer.seek(0)
    return send_file(
        zip_buffer,
        mimetype='application/zip',
        as_attachment=True,
        download_name='msbte_full_system_backup.zip'
    )



