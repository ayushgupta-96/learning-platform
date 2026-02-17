# backend/app/routes/student.py
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db
from ..models.user import User
from ..models.student import Student
from ..utils.decorators import student_required

bp = Blueprint('student', __name__, url_prefix='/api/student')

@bp.route('/profile', methods=['GET'])
@student_required
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        student = user.student_profile
        
        return jsonify({
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/profile', methods=['PUT'])
@student_required
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        student = user.student_profile
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            student.name = data['name']
        if 'age' in data:
            student.age = data['age']
        if 'education' in data:
            student.education = data['education']
        if 'profession' in data:
            student.profession = data['profession']
        if 'mobile' in data:
            student.mobile = data['mobile']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': student.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/dashboard-stats', methods=['GET'])
@student_required
def get_dashboard_stats():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        student = user.student_profile
        
        from ..models.session import VideoSession
        total_sessions = VideoSession.query.filter_by(student_id=student.id).count()
        
        stats = {
            'points_balance': student.points_balance,
            'total_video_time': student.total_video_time,
            'training_progress': student.training_progress,
            'total_sessions': total_sessions
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


 