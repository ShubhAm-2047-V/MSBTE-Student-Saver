import os
import unittest
from config import Config
from app import create_app
from models import db
from models.user import User
from models.student import Student
from models.subject import Subject
from models.marks import Marks
from models.attendance import Attendance
from ml.predict import predict_student_performance

TEST_DB_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test_database.db')

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{TEST_DB_PATH}"
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test_secret_key'

class MSBTEStudentSaverTestCase(unittest.TestCase):
    def setUp(self):
        """Set up test client with dedicated test database."""
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except OSError:
                pass

        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client()
        
        db.create_all()

        # Create Admin
        admin = User(username='testadmin', role='admin')
        admin.set_password('adminpass123')
        db.session.add(admin)

        # Create Demo Subject
        subj = Subject(
            subject_code='22516',
            subject_name='Operating Systems',
            branch='Computer Engineering',
            semester=5,
            subject_type='Theory',
            internal_max=30.0,
            external_max=70.0,
            practical_max=0.0,
            total_max=100.0,
            passing_marks=40.0,
            credits=4
        )
        db.session.add(subj)

        # Create Demo Student
        student = Student(
            enrollment_no='TESTSTU001',
            name='Test Student',
            branch='Computer Engineering',
            semester=5,
            academic_year='2025-2026',
            previous_percentage=75.0,
            assignment_percentage=80.0
        )
        db.session.add(student)
        db.session.flush()

        # Create Student User Account
        stud_user = User(username='TESTSTU001', role='student', student_id=student.id)
        stud_user.set_password('stud@0001')
        db.session.add(stud_user)
        db.session.commit()

    def tearDown(self):
        """Clean up test database."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        if os.path.exists(TEST_DB_PATH):
            try:
                os.remove(TEST_DB_PATH)
            except OSError:
                pass

    # 1. Test Authentication & Password Hashing
    def test_password_hashing(self):
        user = User.query.filter_by(username='testadmin').first()
        self.assertNotEqual(user.password_hash, 'adminpass123')
        self.assertTrue(user.check_password('adminpass123'))
        self.assertFalse(user.check_password('wrongpass'))

    def test_login_success_and_failure(self):
        # Successful login
        resp = self.client.post('/login', data={'username': 'testadmin', 'password': 'adminpass123'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Dashboard', resp.data)

        # Logout
        self.client.get('/logout')

        # Invalid login
        resp_invalid = self.client.post('/login', data={'username': 'testadmin', 'password': 'wrongpassword'}, follow_redirects=True)
        self.assertIn(b'Invalid username or password', resp_invalid.data)

    # 2. Test Authorization & RBAC
    def test_rbac_student_blocked_from_admin(self):
        # Login as student
        self.client.post('/login', data={'username': 'TESTSTU001', 'password': 'stud@0001'})
        # Attempt to access admin dashboard
        resp = self.client.get('/dashboard')
        self.assertEqual(resp.status_code, 403)
        self.assertIn(b'403', resp.data)

    # 3. Test Marks Calculation & Validation
    def test_marks_calculation_and_validation(self):
        student = Student.query.filter_by(enrollment_no='TESTSTU001').first()
        subject = Subject.query.filter_by(subject_code='22516').first()
        
        # Valid Marks
        marks = Marks(
            student_id=student.id,
            subject_id=subject.id,
            internal_marks=22.0,
            external_marks=55.0,
            practical_marks=0.0
        )
        marks.calculate_total_and_result(subject)
        self.assertEqual(marks.total_marks, 77.0)
        self.assertEqual(marks.percentage, 77.0)
        self.assertEqual(marks.result, 'Pass')

        # Failing Marks
        marks_fail = Marks(
            student_id=student.id,
            subject_id=subject.id,
            internal_marks=10.0,
            external_marks=20.0,
            practical_marks=0.0
        )
        marks_fail.calculate_total_and_result(subject)
        self.assertEqual(marks_fail.total_marks, 30.0)
        self.assertEqual(marks_fail.result, 'Fail')

    # 4. Test Attendance Calculation & Status
    def test_attendance_status(self):
        student = Student.query.filter_by(enrollment_no='TESTSTU001').first()
        subject = Subject.query.filter_by(subject_code='22516').first()

        att = Attendance(
            student_id=student.id,
            subject_id=subject.id,
            total_classes=50,
            attended_classes=42
        )
        att.calculate_percentage_and_status()
        self.assertEqual(att.attendance_percentage, 84.0)
        self.assertEqual(att.status, 'Good')

        # Low Attendance (< 60%)
        att_low = Attendance(
            student_id=student.id,
            subject_id=subject.id,
            total_classes=50,
            attended_classes=25
        )
        att_low.calculate_percentage_and_status()
        self.assertEqual(att_low.attendance_percentage, 50.0)
        self.assertEqual(att_low.status, 'Low Attendance')

    # 5. Test Machine Learning Prediction Pipeline
    def test_ml_prediction(self):
        res = predict_student_performance(
            attendance=85.0,
            internal=78.0,
            previous=80.0,
            assignment=85.0,
            failed_subjects=0
        )
        self.assertIn('predicted_category', res)
        self.assertIn(res['predicted_category'], ['Good', 'Average', 'Needs Improvement', 'At Risk'])
        self.assertIn('recommendations', res)
        self.assertIn('disclaimer', res)

    # 6. Test Universal CSV & Excel Export Endpoints
    def test_universal_exports_csv_and_excel(self):
        # Login as admin
        self.client.post('/login', data={'username': 'testadmin', 'password': 'adminpass123'})
        
        # Test student CSV & Excel export
        resp_csv = self.client.get('/export/students')
        self.assertEqual(resp_csv.status_code, 200)
        self.assertEqual(resp_csv.mimetype, 'text/csv')
        self.assertIn(b'Enrollment_No', resp_csv.data)

        resp_excel = self.client.get('/export/students/excel')
        self.assertEqual(resp_excel.status_code, 200)
        self.assertEqual(resp_excel.mimetype, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        # Test marks Excel export
        resp_marks_xlsx = self.client.get('/export/marks/excel')
        self.assertEqual(resp_marks_xlsx.status_code, 200)

        # Test attendance Excel export
        resp_att_xlsx = self.client.get('/export/attendance/excel')
        self.assertEqual(resp_att_xlsx.status_code, 200)

        # Test defaulters CSV & Excel export
        resp_def_csv = self.client.get('/export/defaulters/csv')
        self.assertEqual(resp_def_csv.status_code, 200)
        resp_def_xlsx = self.client.get('/export/defaulters/excel')
        self.assertEqual(resp_def_xlsx.status_code, 200)

        # Test master Power BI export
        resp_master = self.client.get('/export/powerbi-analytics')
        self.assertEqual(resp_master.status_code, 200)
        self.assertEqual(resp_master.mimetype, 'text/csv')
        self.assertIn(b'Subject_Percentage', resp_master.data)

        resp_master_xlsx = self.client.get('/export/powerbi-analytics/excel')
        self.assertEqual(resp_master_xlsx.status_code, 200)

    # 7. Test PDF / Print Report Endpoints
    def test_print_pdf_reports(self):
        self.client.post('/login', data={'username': 'testadmin', 'password': 'adminpass123'})
        
        # Print Students
        resp = self.client.get('/reports/students/print')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Student Academic Directory', resp.data)

        # Print Defaulters
        resp_def = self.client.get('/reports/defaulters/print')
        self.assertEqual(resp_def.status_code, 200)
        self.assertIn(b'Head of Department', resp_def.data)

        # Print Marks
        resp_marks = self.client.get('/reports/marks/print')
        self.assertEqual(resp_marks.status_code, 200)

        # Print Attendance
        resp_att = self.client.get('/reports/attendance/print')
        self.assertEqual(resp_att.status_code, 200)

    # 8. Test MSBTE Defaulters & Notice Generation View
    def test_defaulters_view(self):
        self.client.post('/login', data={'username': 'testadmin', 'password': 'adminpass123'})
        resp = self.client.get('/defaulters')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Monthly Attendance Defaulters', resp.data)

    # 9. Test What-If Academic Simulator & Real-time AJAX ML API
    def test_simulator_and_api(self):
        self.client.post('/login', data={'username': 'testadmin', 'password': 'adminpass123'})
        
        # Simulator page load
        resp_page = self.client.get('/simulator')
        self.assertEqual(resp_page.status_code, 200)
        self.assertIn(b'Interactive Academic & Grade Simulator', resp_page.data)

        # Simulator AJAX prediction API
        resp_api = self.client.post('/prediction/api', json={
            'attendance': 88.0,
            'internal': 85.0,
            'previous': 76.0,
            'assignment': 80.0,
            'failed_subjects': 0
        })
        self.assertEqual(resp_api.status_code, 200)
        data = resp_api.get_json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('predicted_category', data['data'])

    # 10. Test Capstone Projects & ATKT Portal
    def test_capstone_projects(self):
        self.client.post('/login', data={'username': 'testadmin', 'password': 'adminpass123'})
        
        # View page
        resp = self.client.get('/capstone-projects')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'Capstone Project Planning & ATKT Eligibility Portal', resp.data)

        # Add new capstone project
        resp_add = self.client.post('/capstone-projects', data={
            'group_no': 'GRP-99',
            'project_title': 'AI Student Performance Predictor',
            'domain': 'Machine Learning & Web',
            'semester': 5,
            'guide_name': 'Prof. A. K. Sharma',
            'members': 'Test Student (TESTSTU001)',
            'status': 'In Progress',
            'weekly_diary_status': 'Up to Date'
        }, follow_redirects=True)
        self.assertEqual(resp_add.status_code, 200)
        self.assertIn(b'GRP-99', resp_add.data)
        self.assertIn(b'AI Student Performance Predictor', resp_add.data)

    # 11. Test Bulk Upload Template Downloads
    def test_bulk_upload_templates(self):
        self.client.post('/login', data={'username': 'testadmin', 'password': 'adminpass123'})
        
        # View page
        resp_page = self.client.get('/bulk-upload')
        self.assertEqual(resp_page.status_code, 200)
        self.assertIn(b'Bulk Students & Marks Importer', resp_page.data)

        # Download students template
        resp_stu_tpl = self.client.get('/bulk-upload/template/students')
        self.assertEqual(resp_stu_tpl.status_code, 200)
        self.assertEqual(resp_stu_tpl.mimetype, 'text/csv')
        self.assertIn(b'Enrollment_No', resp_stu_tpl.data)

        # Download marks template
        resp_marks_tpl = self.client.get('/bulk-upload/template/marks')
        self.assertEqual(resp_marks_tpl.status_code, 200)
        self.assertEqual(resp_marks_tpl.mimetype, 'text/csv')
        self.assertIn(b'Enrollment_No', resp_marks_tpl.data)

if __name__ == '__main__':
    unittest.main()

