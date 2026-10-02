import io
import csv
from datetime import datetime
from flask import Blueprint, render_template, Response, make_response, request
import pandas as pd
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from models.attendance import Attendance
from routes.auth import login_required, admin_required
from ml.predict import predict_student_performance

reports_bp = Blueprint('reports', __name__)

# ===================================================================
# 1. PRINTABLE PDF-READY REPORT VIEWS (WITH @media print)
# ===================================================================

@reports_bp.route('/reports/student/<int:id>')
@login_required
def student_report(id):
    """Generate printable individual Academic Analysis Report."""
    student = Student.query.get_or_404(id)
    marks_records = student.marks.all()
    attendance_records = student.attendances.all()

    overall_pct = student.calculate_overall_percentage()
    internal_pct = student.calculate_internal_percentage()
    overall_att = student.calculate_overall_attendance()
    passed_count = student.get_passed_subjects_count()
    failed_count = student.get_failed_subjects_count()
    category = student.get_performance_category()
    atkt_info = student.get_atkt_status()
    msbte_class = student.get_msbte_class()

    # ML Early Warning Prediction
    ml_result = predict_student_performance(
        attendance=overall_att,
        internal=internal_pct,
        previous=student.previous_percentage or 70.0,
        assignment=student.assignment_percentage or 75.0,
        failed_subjects=failed_count
    )

    generated_date = datetime.now().strftime('%d-%b-%Y %I:%M %p')

    return render_template(
        'report.html',
        student=student,
        marks_records=marks_records,
        attendance_records=attendance_records,
        overall_pct=overall_pct,
        internal_pct=internal_pct,
        overall_att=overall_att,
        passed_count=passed_count,
        failed_count=failed_count,
        category=category,
        atkt_info=atkt_info,
        msbte_class=msbte_class,
        ml_result=ml_result,
        generated_date=generated_date
    )

@reports_bp.route('/reports/students/print')
@admin_required
def print_students_directory():
    """Printable sheet of all enrolled students."""
    students = Student.query.order_by(Student.enrollment_no.asc()).all()
    student_rows = []
    for s in students:
        student_rows.append({
            'student': s,
            'percentage': s.calculate_overall_percentage(),
            'attendance': s.calculate_overall_attendance(),
            'category': s.get_performance_category(),
            'failed_count': s.get_failed_subjects_count(),
            'atkt': s.get_atkt_status()
        })
    generated_date = datetime.now().strftime('%d-%b-%Y %I:%M %p')
    return render_template('print_students.html', student_rows=student_rows, generated_date=generated_date)

@reports_bp.route('/reports/defaulters/print')
@admin_required
def print_defaulters_notice():
    """Printable official MSBTE Monthly Attendance Defaulter Notice with HOD & Principal sign blocks."""
    students = Student.query.all()
    defaulters = []
    for s in students:
        att = s.calculate_overall_attendance()
        if att < 75.0:
            records = s.attendances.all()
            total_cond = sum(a.total_classes for a in records) if records else 50
            total_att = sum(a.attended_classes for a in records) if records else int(50 * att / 100)
            missed = max(0, total_cond - total_att)
            defaulters.append({
                'student': s,
                'attendance': att,
                'total_conducted': total_cond,
                'attended': total_att,
                'missed': missed,
                'category': 'Critical Detention (<60%)' if att < 60.0 else 'Undertaking Required (60-74%)',
                'severity': 'danger' if att < 60.0 else 'warning'
            })
    defaulters.sort(key=lambda x: x['attendance'])
    generated_date = datetime.now().strftime('%d-%b-%Y %I:%M %p')
    return render_template('print_defaulters.html', defaulters=defaulters, generated_date=generated_date)

@reports_bp.route('/reports/marks/print')
@admin_required
def print_marks_ledger():
    """Printable Subject Marks Ledger."""
    marks_list = Marks.query.order_by(Marks.subject_id.asc(), Marks.student_id.asc()).all()
    generated_date = datetime.now().strftime('%d-%b-%Y %I:%M %p')
    return render_template('print_marks.html', marks_list=marks_list, generated_date=generated_date)

@reports_bp.route('/reports/attendance/print')
@admin_required
def print_attendance_ledger():
    """Printable Attendance Ledger."""
    attendance_list = Attendance.query.order_by(Attendance.subject_id.asc(), Attendance.student_id.asc()).all()
    generated_date = datetime.now().strftime('%d-%b-%Y %I:%M %p')
    return render_template('print_attendance.html', attendance_list=attendance_list, generated_date=generated_date)

@reports_bp.route('/powerbi')
@login_required
def powerbi_guide():
    """Power BI integration overview and export portal."""
    student_count = Student.query.count()
    marks_count = Marks.query.count()
    attendance_count = Attendance.query.count()

    return render_template(
        'powerbi.html',
        student_count=student_count,
        marks_count=marks_count,
        attendance_count=attendance_count
    )

# ===================================================================
# 2. UNIVERSAL CSV EXPORTS
# ===================================================================

@reports_bp.route('/export/students/csv')
@reports_bp.route('/export/students')
@admin_required
def export_students_csv():
    """Export student directory to CSV."""
    students = Student.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Enrollment_No', 'Student_Name', 'Branch', 'Semester', 
        'Academic_Year', 'Email', 'Phone', 'Admission_Year',
        'Overall_Percentage', 'Attendance_Percentage', 'Performance_Category',
        'ATKT_Status', 'MSBTE_Class'
    ])
    for s in students:
        writer.writerow([
            s.enrollment_no, s.name, s.branch, s.semester,
            s.academic_year, s.email, s.phone, s.admission_year,
            s.calculate_overall_percentage(),
            s.calculate_overall_attendance(),
            s.get_performance_category(),
            s.get_atkt_status()['status'],
            s.get_msbte_class()
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=msbte_students_directory.csv'}
    )

@reports_bp.route('/export/marks/csv')
@reports_bp.route('/export/marks')
@admin_required
def export_marks_csv():
    """Export all marks records to CSV."""
    marks_list = Marks.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Enrollment_No', 'Student_Name', 'Branch', 'Semester',
        'Subject_Code', 'Subject_Name', 'Subject_Type', 'Internal_Marks',
        'External_Marks', 'Practical_Marks', 'Total_Marks', 'Max_Marks',
        'Percentage', 'Result'
    ])
    for m in marks_list:
        student = m.student
        subject = m.subject
        writer.writerow([
            student.enrollment_no if student else '',
            student.name if student else '',
            student.branch if student else '',
            subject.semester if subject else '',
            subject.subject_code if subject else '',
            subject.subject_name if subject else '',
            subject.subject_type if subject else '',
            m.internal_marks,
            m.external_marks,
            m.practical_marks,
            m.total_marks,
            subject.total_max if subject else 100,
            m.percentage,
            m.result
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=msbte_marks_records.csv'}
    )

@reports_bp.route('/export/attendance/csv')
@reports_bp.route('/export/attendance')
@admin_required
def export_attendance_csv():
    """Export all attendance records to CSV."""
    attendances = Attendance.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Enrollment_No', 'Student_Name', 'Branch', 'Semester',
        'Subject_Code', 'Subject_Name', 'Total_Classes', 'Attended_Classes',
        'Attendance_Percentage', 'Attendance_Status'
    ])
    for a in attendances:
        student = a.student
        subject = a.subject
        writer.writerow([
            student.enrollment_no if student else '',
            student.name if student else '',
            student.branch if student else '',
            subject.semester if subject else '',
            subject.subject_code if subject else '',
            subject.subject_name if subject else '',
            a.total_classes,
            a.attended_classes,
            a.attendance_percentage,
            a.status
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=msbte_attendance_records.csv'}
    )

@reports_bp.route('/export/defaulters/csv')
@admin_required
def export_defaulters_csv():
    """Export attendance defaulter list (<75%) to CSV."""
    students = Student.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Enrollment_No', 'Student_Name', 'Branch', 'Semester',
        'Attendance_Percentage', 'Classes_Conducted', 'Classes_Attended',
        'Classes_Missed', 'Defaulter_Severity', 'Parent_Phone'
    ])
    for s in students:
        att = s.calculate_overall_attendance()
        if att < 75.0:
            records = s.attendances.all()
            cond = sum(a.total_classes for a in records) if records else 50
            att_count = sum(a.attended_classes for a in records) if records else int(50 * att / 100)
            writer.writerow([
                s.enrollment_no, s.name, s.branch, s.semester,
                att, cond, att_count, max(0, cond - att_count),
                'Critical (<60%)' if att < 60.0 else 'Warning (60-74%)',
                s.phone or ''
            ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=msbte_attendance_defaulters.csv'}
    )

@reports_bp.route('/export/subjects/csv')
@admin_required
def export_subjects_csv():
    """Export configured MSBTE subjects structure to CSV."""
    subjects = Subject.query.order_by(Subject.semester.asc()).all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Subject_Code', 'Subject_Name', 'Branch', 'Semester',
        'Subject_Type', 'Internal_Max', 'External_Max', 'Practical_Max',
        'Total_Max', 'Passing_Marks', 'Credits'
    ])
    for sub in subjects:
        writer.writerow([
            sub.subject_code, sub.subject_name, sub.branch, sub.semester,
            sub.subject_type, sub.internal_max, sub.external_max, sub.practical_max,
            sub.total_max, sub.passing_marks, sub.credits
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=msbte_subjects_structure.csv'}
    )

@reports_bp.route('/export/powerbi-analytics')
@reports_bp.route('/export/powerbi/csv')
@admin_required
def export_powerbi_master_csv():
    """Export unified Power BI-ready dataset."""
    marks_list = Marks.query.all()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Student_ID', 'Enrollment_No', 'Student_Name', 'Branch', 'Semester', 'Academic_Year',
        'Subject_Code', 'Subject_Name', 'Subject_Type', 'Credits',
        'Internal_Marks', 'External_Marks', 'Practical_Marks', 'Total_Marks', 'Max_Marks',
        'Subject_Percentage', 'Subject_Result',
        'Student_Overall_Percentage', 'Student_Overall_Attendance',
        'Student_Performance_Category', 'Attendance_Status', 'Predicted_Risk_Category',
        'ATKT_Status', 'MSBTE_Class'
    ])
    for m in marks_list:
        student = m.student
        subject = m.subject
        if not student or not subject:
            continue
        overall_pct = student.calculate_overall_percentage()
        overall_att = student.calculate_overall_attendance()
        category = student.get_performance_category()
        att_status = student.get_attendance_status()

        ml_res = predict_student_performance(
            attendance=overall_att,
            internal=student.calculate_internal_percentage(),
            previous=student.previous_percentage or 70.0,
            assignment=student.assignment_percentage or 75.0,
            failed_subjects=student.get_failed_subjects_count()
        )
        writer.writerow([
            student.id, student.enrollment_no, student.name, student.branch,
            subject.semester, student.academic_year,
            subject.subject_code, subject.subject_name, subject.subject_type, subject.credits,
            m.internal_marks, m.external_marks, m.practical_marks, m.total_marks, subject.total_max,
            m.percentage, m.result, overall_pct, overall_att,
            category, att_status, ml_res['predicted_category'],
            student.get_atkt_status()['status'], student.get_msbte_class()
        ])
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=powerbi_master_analytics.csv'}
    )

# ===================================================================
# 3. UNIVERSAL EXCEL (.XLSX) EXPORTS USING PANDAS & OPENPYXL
# ===================================================================

@reports_bp.route('/export/students/excel')
@admin_required
def export_students_excel():
    """Export student directory to Excel (.xlsx)."""
    students = Student.query.all()
    data = []
    for s in students:
        data.append({
            'Enrollment No': s.enrollment_no,
            'Student Name': s.name,
            'Branch': s.branch,
            'Semester': s.semester,
            'Academic Year': s.academic_year,
            'Email': s.email or '',
            'Phone': s.phone or '',
            'Overall Score (%)': s.calculate_overall_percentage(),
            'Attendance (%)': s.calculate_overall_attendance(),
            'Performance Tier': s.get_performance_category(),
            'ATKT Eligibility': s.get_atkt_status()['status'],
            'MSBTE Class Award': s.get_msbte_class()
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Students_Directory')
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=msbte_students_directory.xlsx'}
    )

@reports_bp.route('/export/marks/excel')
@admin_required
def export_marks_excel():
    """Export marks ledger to Excel (.xlsx)."""
    marks_list = Marks.query.all()
    data = []
    for m in marks_list:
        s = m.student
        sub = m.subject
        data.append({
            'Enrollment No': s.enrollment_no if s else '',
            'Student Name': s.name if s else '',
            'Branch': s.branch if s else '',
            'Semester': sub.semester if sub else '',
            'Subject Code': sub.subject_code if sub else '',
            'Subject Name': sub.subject_name if sub else '',
            'Internal Marks': m.internal_marks,
            'External Marks': m.external_marks,
            'Practical Marks': m.practical_marks,
            'Total Marks': m.total_marks,
            'Max Marks': sub.total_max if sub else 100,
            'Percentage (%)': m.percentage,
            'Result': m.result
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Marks_Ledger')
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=msbte_marks_records.xlsx'}
    )

@reports_bp.route('/export/attendance/excel')
@admin_required
def export_attendance_excel():
    """Export attendance ledger to Excel (.xlsx)."""
    attendances = Attendance.query.all()
    data = []
    for a in attendances:
        s = a.student
        sub = a.subject
        data.append({
            'Enrollment No': s.enrollment_no if s else '',
            'Student Name': s.name if s else '',
            'Branch': s.branch if s else '',
            'Semester': sub.semester if sub else '',
            'Subject Code': sub.subject_code if sub else '',
            'Subject Name': sub.subject_name if sub else '',
            'Total Classes': a.total_classes,
            'Attended Classes': a.attended_classes,
            'Attendance (%)': a.attendance_percentage,
            'Attendance Status': a.status
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance_Ledger')
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=msbte_attendance_records.xlsx'}
    )

@reports_bp.route('/export/defaulters/excel')
@admin_required
def export_defaulters_excel():
    """Export defaulters notice to Excel (.xlsx)."""
    students = Student.query.all()
    data = []
    for s in students:
        att = s.calculate_overall_attendance()
        if att < 75.0:
            records = s.attendances.all()
            cond = sum(a.total_classes for a in records) if records else 50
            att_count = sum(a.attended_classes for a in records) if records else int(50 * att / 100)
            data.append({
                'Enrollment No': s.enrollment_no,
                'Student Name': s.name,
                'Branch': s.branch,
                'Semester': s.semester,
                'Attendance (%)': att,
                'Conducted': cond,
                'Attended': att_count,
                'Missed Classes': max(0, cond - att_count),
                'Severity Level': 'Critical Detention (<60%)' if att < 60.0 else 'Warning Undertaking (60-74%)',
                'Parent Phone': s.phone or ''
            })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance_Defaulters')
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=msbte_attendance_defaulters.xlsx'}
    )

@reports_bp.route('/export/subjects/excel')
@admin_required
def export_subjects_excel():
    """Export subjects list to Excel (.xlsx)."""
    subjects = Subject.query.order_by(Subject.semester.asc()).all()
    data = []
    for sub in subjects:
        data.append({
            'Subject Code': sub.subject_code,
            'Subject Name': sub.subject_name,
            'Branch': sub.branch,
            'Semester': sub.semester,
            'Type': sub.subject_type,
            'Internal Max': sub.internal_max,
            'External Max': sub.external_max,
            'Practical Max': sub.practical_max,
            'Total Max': sub.total_max,
            'Passing Threshold': sub.passing_marks,
            'Credits': sub.credits
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='MSBTE_Subjects')
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=msbte_subjects_structure.xlsx'}
    )

@reports_bp.route('/export/powerbi/excel')
@reports_bp.route('/export/powerbi-analytics/excel')
@admin_required
def export_powerbi_excel():
    """Export Master Analytics dataset to Excel (.xlsx)."""
    marks_list = Marks.query.all()
    data = []
    for m in marks_list:
        student = m.student
        subject = m.subject
        if not student or not subject:
            continue
        overall_pct = student.calculate_overall_percentage()
        overall_att = student.calculate_overall_attendance()
        category = student.get_performance_category()
        att_status = student.get_attendance_status()

        ml_res = predict_student_performance(
            attendance=overall_att,
            internal=student.calculate_internal_percentage(),
            previous=student.previous_percentage or 70.0,
            assignment=student.assignment_percentage or 75.0,
            failed_subjects=student.get_failed_subjects_count()
        )
        data.append({
            'Enrollment No': student.enrollment_no,
            'Student Name': student.name,
            'Branch': student.branch,
            'Semester': subject.semester,
            'Subject Code': subject.subject_code,
            'Subject Name': subject.subject_name,
            'Credits': subject.credits,
            'Internal Marks': m.internal_marks,
            'External Marks': m.external_marks,
            'Practical Marks': m.practical_marks,
            'Total Marks': m.total_marks,
            'Max Marks': subject.total_max,
            'Subject Score (%)': m.percentage,
            'Result': m.result,
            'Overall Student Score (%)': overall_pct,
            'Overall Attendance (%)': overall_att,
            'Performance Tier': category,
            'Attendance Status': att_status,
            'ML Predicted Tier': ml_res['predicted_category'],
            'ATKT Eligibility': student.get_atkt_status()['status'],
            'MSBTE Class': student.get_msbte_class()
        })
    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='PowerBI_Master_Analytics')
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=msbte_master_analytics.xlsx'}
    )
