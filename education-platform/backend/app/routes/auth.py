# backend/app/routes/auth.py
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from ..models import db
from ..models.user import User
from ..models.student import Student
from ..models.teacher import Teacher
from ..utils.validators import validate_email, validate_password, validate_mobile

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/student/signup', methods=['POST'])
def student_signup():
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password', 'name', 'mobile']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate email
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Validate password
        if not validate_password(data['password']):
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Validate mobile
        if not validate_mobile(data['mobile']):
            return jsonify({'error': 'Invalid mobile number'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user = User(email=data['email'], role='student')
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        # Create student profile
        student = Student(
            user_id=user.id,
            name=data['name'],
            age=data.get('age'),
            education=data.get('education'),
            profession=data.get('profession'),
            mobile=data['mobile']
        )
        db.session.add(student)
        db.session.commit()
        
        # Create token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Student registered successfully',
            'access_token': access_token,
            'user': user.to_dict(),
            'profile': student.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/teacher/signup', methods=['POST'])
def teacher_signup():
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['email', 'password', 'name', 'mobile']
        if not all(field in data for field in required):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate
        if not validate_email(data['email']):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(data['password']):
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        if not validate_mobile(data['mobile']):
            return jsonify({'error': 'Invalid mobile number'}), 400
        
        # Check if user exists
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user = User(email=data['email'], role='teacher')
        user.set_password(data['password'])
        db.session.add(user)
        db.session.flush()
        
        # Create teacher profile
        teacher = Teacher(
            user_id=user.id,
            name=data['name'],
            age=data.get('age'),
            education=data.get('education'),
            profession=data.get('profession'),
            mobile=data['mobile']
        )
        db.session.add(teacher)
        db.session.commit()
        
        # Create token
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Teacher registered successfully',
            'access_token': access_token,
            'user': user.to_dict(),
            'profile': teacher.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/student/login', methods=['POST'])
def student_login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email'], role='student').first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict(),
            'profile': user.student_profile.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/teacher/login', methods=['POST'])
def teacher_login():
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email'], role='teacher').first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is deactivated'}), 403
        
        access_token = create_access_token(identity=user.id)
        
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict(),
            'profile': user.teacher_profile.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        profile = user.student_profile if user.role == 'student' else user.teacher_profile
        
        return jsonify({
            'user': user.to_dict(),
            'profile': profile.to_dict() if profile else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500