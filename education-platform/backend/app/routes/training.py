# backend/app/routes/training.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db
from ..models.user import User
from ..models.question import Question
from ..models.student import Student
from ..models.points import PointsTransaction
from ..utils.decorators import student_required
import random

bp = Blueprint('training', __name__, url_prefix='/api/training')

@bp.route('/questions', methods=['GET'])
@student_required
def get_questions():
    try:
        difficulty = request.args.get('difficulty', 'easy')
        question_type = request.args.get('type', 'mcq')
        count = request.args.get('count', 5, type=int)
        
        questions = Question.query.filter_by(
            difficulty=difficulty,
            question_type=question_type,
            is_active=True
        ).all()
        
        # Randomly select questions
        if len(questions) > count:
            questions = random.sample(questions, count)
        
        return jsonify({
            'questions': [q.to_dict() for q in questions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/submit-answer', methods=['POST'])
@student_required
def submit_answer():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        student = user.student_profile
        
        data = request.get_json()
        question_id = data.get('question_id')
        answer = data.get('answer')
        
        if not question_id or not answer:
            return jsonify({'error': 'Question ID and answer required'}), 400
        
        question = Question.query.get(question_id)
        if not question:
            return jsonify({'error': 'Question not found'}), 404
        
        is_correct = False
        points_earned = 0
        
        if question.question_type == 'mcq':
            is_correct = answer.upper() == question.correct_answer
        else:
            # For speaking prompts, we'll accept any answer for now
            # In production, you'd integrate speech recognition
            is_correct = True
        
        if is_correct:
            points_earned = question.points_value
            student.points_balance += points_earned
            
            # Create points transaction
            transaction = PointsTransaction(
                student_id=student.id,
                points=points_earned,
                transaction_type='earned',
                description=f'Answered {question.difficulty} question',
                question_id=question_id
            )
            db.session.add(transaction)
            
            # Update training progress
            total_questions = Question.query.filter_by(is_active=True).count()
            answered = PointsTransaction.query.filter_by(
                student_id=student.id,
                transaction_type='earned'
            ).count()
            student.training_progress = min(100, int((answered / total_questions) * 100))
        
        db.session.commit()
        
        return jsonify({
            'is_correct': is_correct,
            'points_earned': points_earned,
            'total_points': student.points_balance,
            'training_progress': student.training_progress
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


 