# backend/app/routes/teacher.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db
from ..models.user import User
from ..models.teacher import Teacher
from ..utils.decorators import teacher_required

bp = Blueprint('teacher', __name__, url_prefix='/api/teacher')

@bp.route('/profile', methods=['GET'])
@teacher_required
def get_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        teacher = user.teacher_profile
        
        return jsonify({
            'profile': teacher.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/profile', methods=['PUT'])
@teacher_required
def update_profile():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        teacher = user.teacher_profile
        
        data = request.get_json()
        
        # Update allowed fields
        if 'name' in data:
            teacher.name = data['name']
        if 'age' in data:
            teacher.age = data['age']
        if 'education' in data:
            teacher.education = data['education']
        if 'profession' in data:
            teacher.profession = data['profession']
        if 'mobile' in data:
            teacher.mobile = data['mobile']
        if 'is_available' in data:
            teacher.is_available = data['is_available']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'profile': teacher.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/dashboard-stats', methods=['GET'])
@teacher_required
def get_dashboard_stats():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        teacher = user.teacher_profile
        
        from ..models.session import VideoSession
        from datetime import datetime, timedelta
        
        total_sessions = VideoSession.query.filter_by(teacher_id=teacher.id).count()
        
        # Sessions this month
        first_day = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        sessions_this_month = VideoSession.query.filter(
            VideoSession.teacher_id == teacher.id,
            VideoSession.created_at >= first_day
        ).count()
        
        stats = {
            'total_teaching_time': teacher.total_teaching_time,
            'total_sessions': total_sessions,
            'sessions_this_month': sessions_this_month,
            'is_available': teacher.is_available
        }
        
        return jsonify(stats), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/toggle-availability', methods=['POST'])
@teacher_required
def toggle_availability():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        teacher = user.teacher_profile
        
        teacher.is_available = not teacher.is_available
        db.session.commit()
        
        return jsonify({
            'message': 'Availability updated',
            'is_available': teacher.is_available
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/session-history', methods=['GET'])
@teacher_required
def get_session_history():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        teacher = user.teacher_profile
        
        from ..models.session import VideoSession
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        sessions = VideoSession.query.filter_by(teacher_id=teacher.id)\
            .order_by(VideoSession.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'sessions': [s.to_dict() for s in sessions.items],
            'total': sessions.total,
            'pages': sessions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500