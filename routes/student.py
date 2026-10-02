from flask import Blueprint, render_template, session, redirect, url_for, flash
from models.student import Student
from models.marks import Marks
from models.attendance import Attendance
from routes.auth import login_required
from ml.predict import predict_student_performance

student_bp = Blueprint('student', __name__)

@student_bp.route('/student/profile')
@login_required
def profile():
    """
    Student View: Displays personal academic dashboard, subject marks,
    attendance records, early warning alert, and improvement suggestions.
    """
    student_id = session.get('student_id')
    
    # If admin accesses this route, or if student_id is set
    if not student_id:
        if session.get('role') == 'admin':
            flash('Admin viewing first student profile as preview.', 'info')
            student = Student.query.first()
            if not student:
                flash('No student records found in system.', 'warning')
                return redirect(url_for('admin.dashboard'))
        else:
            flash('No student profile linked to your account.', 'danger')
            return redirect(url_for('auth.logout'))
    else:
        student = Student.query.get_or_404(student_id)

    marks_records = student.marks.all()
    attendance_records = student.attendances.all()

    overall_pct = student.calculate_overall_percentage()
    internal_pct = student.calculate_internal_percentage()
    overall_att = student.calculate_overall_attendance()
    passed_count = student.get_passed_subjects_count()
    failed_count = student.get_failed_subjects_count()
    category = student.get_performance_category()
    attendance_status = student.get_attendance_status()

    # Identify specific subjects needing improvement (marks < passing or attendance < 75)
    weak_subjects = []
    for m in marks_records:
        if m.result == 'Fail' or m.percentage < 50.0:
            weak_subjects.append({
                'name': m.subject.subject_name if m.subject else 'Subject',
                'reason': f"Low score: {m.total_marks}/{m.subject.total_max if m.subject else 100} ({m.percentage}%)"
            })
            
    for a in attendance_records:
        if a.attendance_percentage < 75.0:
            weak_subjects.append({
                'name': a.subject.subject_name if a.subject else 'Subject',
                'reason': f"Low attendance: {a.attended_classes}/{a.total_classes} ({a.attendance_percentage}%)"
            })

    # ML Early Warning Prediction
    ml_result = predict_student_performance(
        attendance=overall_att,
        internal=internal_pct,
        previous=student.previous_percentage or 70.0,
        assignment=student.assignment_percentage or 75.0,
        failed_subjects=failed_count
    )

    return render_template(
        'student_portal.html',
        student=student,
        marks_records=marks_records,
        attendance_records=attendance_records,
        overall_pct=overall_pct,
        internal_pct=internal_pct,
        overall_att=overall_att,
        passed_count=passed_count,
        failed_count=failed_count,
        category=category,
        attendance_status=attendance_status,
        weak_subjects=weak_subjects,
        ml_result=ml_result
    )
