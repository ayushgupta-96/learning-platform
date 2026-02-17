# backend/app/__init__.py
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager
from .config import Config
from .models import db

socketio = SocketIO()
jwt = JWTManager()

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register blueprints
    from .routes import auth, student, teacher, training, points, video
    app.register_blueprint(auth.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(teacher.bp)
    app.register_blueprint(training.bp)
    app.register_blueprint(points.bp)
    app.register_blueprint(video.bp)
    
    # Register Socket.IO handlers
    from . import socketio_handlers
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Seed initial questions
        seed_questions()
    
    return app


def seed_questions():
    from .models.question import Question
    
    # Check if questions already exist
    if Question.query.first():
        return
    
    questions = [
        # Easy MCQs
        Question(
            question_text="What is the past tense of 'go'?",
            question_type='mcq',
            difficulty='easy',
            points_value=10,
            option_a='goed',
            option_b='went',
            option_c='gone',
            option_d='going',
            correct_answer='B'
        ),
        Question(
            question_text="Choose the correct article: ___ apple a day keeps the doctor away.",
            question_type='mcq',
            difficulty='easy',
            points_value=10,
            option_a='A',
            option_b='An',
            option_c='The',
            option_d='No article',
            correct_answer='B'
        ),
        # Medium MCQs
        Question(
            question_text="Which sentence is grammatically correct?",
            question_type='mcq',
            difficulty='medium',
            points_value=20,
            option_a='She don\'t like coffee',
            option_b='She doesn\'t likes coffee',
            option_c='She doesn\'t like coffee',
            option_d='She don\'t likes coffee',
            correct_answer='C'
        ),
        # Hard MCQs
        Question(
            question_text="Choose the correct form: By next year, I ___ my degree.",
            question_type='mcq',
            difficulty='hard',
            points_value=30,
            option_a='will complete',
            option_b='will have completed',
            option_c='would complete',
            option_d='complete',
            correct_answer='B'
        ),
        # Speaking prompts
        Question(
            question_text="Introduce yourself in English (Name, age, profession)",
            question_type='speaking',
            difficulty='easy',
            points_value=10,
            expected_keywords='["name", "age", "profession", "my"]'
        ),
        Question(
            question_text="Describe your daily routine",
            question_type='speaking',
            difficulty='medium',
            points_value=20,
            expected_keywords='["wake", "morning", "work", "evening", "sleep"]'
        ),
    ]
    
    db.session.bulk_save_objects(questions)
    db.session.commit()

from flask import render_template

def register_page_routes(app):
    """Register routes for serving HTML pages"""
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    # Student routes
    @app.route('/student/login')
    def student_login():
        return render_template('student/login.html')
    
    @app.route('/student/signup')
    def student_signup():
        return render_template('student/signup.html')
    
    @app.route('/student/dashboard')
    def student_dashboard():
        return render_template('student/dashboard.html')
    
    @app.route('/student/training')
    def student_training():
        return render_template('student/training.html')
    
    @app.route('/student/video-chat')
    def student_video_chat():
        return render_template('student/video-chat.html')
    
    @app.route('/student/points')
    def student_points():
        return render_template('student/points.html')
    
    # Teacher routes
    @app.route('/teacher/login')
    def teacher_login():
        return render_template('teacher/login.html')
    
    @app.route('/teacher/signup')
    def teacher_signup():
        return render_template('teacher/signup.html')
    
    @app.route('/teacher/dashboard')
    def teacher_dashboard():
        return render_template('teacher/dashboard.html')
    
    @app.route('/teacher/video-chat')
    def teacher_video_chat():
        return render_template('teacher/video-chat.html')

# Then update the create_app function to include:

def create_app(config_class=Config):
    app = Flask(__name__, 
                template_folder='../../frontend/templates',
                static_folder='../../frontend/static')
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    CORS(app)
    jwt.init_app(app)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    
    # Register blueprints
    from .routes import auth, student, teacher, training, points, video
    app.register_blueprint(auth.bp)
    app.register_blueprint(student.bp)
    app.register_blueprint(teacher.bp)
    app.register_blueprint(training.bp)
    app.register_blueprint(points.bp)
    app.register_blueprint(video.bp)
    
    # Register page routes
    register_page_routes(app)
    
    # Register Socket.IO handlers
    from . import socketio_handlers
    
    # Create database tables
    with app.app_context():
        db.create_all()
        # Seed initial questions
        seed_questions()
    
    return app    