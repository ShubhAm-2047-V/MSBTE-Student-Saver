from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.student import student_bp
from routes.marks import marks_bp
from routes.attendance import attendance_bp
from routes.prediction import prediction_bp
from routes.reports import reports_bp

def register_routes(app):
    """Register all modular Flask Blueprints."""
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(prediction_bp)
    app.register_blueprint(reports_bp)
