import os
from flask import Flask, render_template, redirect, url_for, session
from config import Config
from models import db
from models.user import User
from models.student import Student
from routes import register_routes

def create_app(config_class=Config):
    """Application factory for MSBTE Student Saver."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)

    # Register blueprints
    register_routes(app)

    # Context processor to expose session & user details to all templates
    @app.context_processor
    def inject_user_context():
        current_user = None
        linked_student = None
        if 'user_id' in session:
            current_user = User.query.get(session['user_id'])
            if current_user and current_user.student_id:
                linked_student = Student.query.get(current_user.student_id)
        return dict(
            current_user=current_user,
            linked_student=linked_student,
            app_name="MSBTE Student Saver"
        )

    # Root redirect
    @app.route('/')
    def index():
        if 'user_id' in session:
            if session.get('role') == 'admin':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('student.profile'))
        return redirect(url_for('auth.login'))

    # Custom Error Handlers
    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("\n=======================================================")
    print("                 MSBTE Student Saver                  ")
    print(" Running on: http://127.0.0.1:5000 ")
    print("=======================================================\n")
    app.run(debug=True, host='127.0.0.1', port=5000)
