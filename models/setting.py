from models import db

class SystemSetting(db.Model):
    """Key-value system setting configuration model for MSBTE Student Saver."""
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(80), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=False)

    @classmethod
    def get(cls, key, default=None):
        """Retrieve setting value or fallback to default."""
        setting = cls.query.filter_by(key=key).first()
        return setting.value if setting else default

    @classmethod
    def set(cls, key, value):
        """Save or update setting value."""
        setting = cls.query.filter_by(key=key).first()
        if not setting:
            setting = cls(key=key, value=str(value))
            db.session.add(setting)
        else:
            setting.value = str(value)
        db.session.commit()

    @classmethod
    def get_all_settings(cls):
        """Get all settings as a key-value dictionary with defaults."""
        defaults = {
            # Institute Profile
            'institute_name': 'Government Polytechnic, Mumbai (Autonomous)',
            'institute_code': 'MSBTE Code: 0018 / DTE: 3012',
            'department_name': 'Department of Computer Engineering',
            'hod_name': 'Prof. A. S. Kulkarni (M.E. Comp, Ph.D)',
            'principal_name': 'Dr. S. M. Patil (Principal)',

            # Academic Rules
            'academic_year': '2025-2026',
            'msbte_scheme': 'I-Scheme',
            'attendance_threshold': '75',
            'passing_threshold': '40',
            'max_atkt_backlogs': '3',

            # Performance Tier Boundaries
            'tier_excellent': '90',
            'tier_good': '75',
            'tier_average': '60',
            'tier_needs_imp': '40',

            # Alerts & Notifications
            'auto_defaulter_alert': 'true',
            'atkt_warning_alert': 'true',
            'parent_sms_template': 'Dear Parent, your ward [Student Name] (Enr: [Enrollment]) in Sem [Semester] has attendance [Attendance]% which is below MSBTE 75% norm. Please contact HOD.',
            'parent_marks_template': 'Dear Parent, your ward [Student Name] has scored [Percentage]% in Sem [Semester] with [Backlogs] backlogs. Academic counseling is scheduled.',

            # UX Preferences
            'default_page_size': '25',
            'dense_table_mode': 'false',
            'ui_theme': 'Light Theme'
        }

        all_records = cls.query.all()
        for rec in all_records:
            defaults[rec.key] = rec.value
        return defaults
