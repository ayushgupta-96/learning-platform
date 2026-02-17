# backend/app/routes/video.py
from flask import Blueprint, request, jsonify, render_template
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db
from ..models.user import User
from ..models.session import VideoSession
from ..models.student import Student
from ..models.teacher import Teacher
from ..utils.decorators import student_required, teacher_required
from datetime import datetime
import uuid

bp = Blueprint('video', __name__, url_prefix='/api/video')

@bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if user.role == 'student':
            student = user.student_profile
            sessions = VideoSession.query.filter_by(student_id=student.id)\
                .order_by(VideoSession.created_at.desc()).limit(20).all()
        else:
            teacher = user.teacher_profile
            sessions = VideoSession.query.filter_by(teacher_id=teacher.id)\
                .order_by(VideoSession.created_at.desc()).limit(20).all()
        
        return jsonify({
            'sessions': [s.to_dict() for s in sessions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/session/<int:session_id>', methods=['GET'])
@jwt_required()
def get_session(session_id):
    try:
        session = VideoSession.query.get(session_id)
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        return jsonify({
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


 