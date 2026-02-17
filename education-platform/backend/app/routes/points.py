# backend/app/routes/points.py
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..models import db
from ..models.user import User
from ..models.student import Student
from ..models.points import PointsTransaction, RedemptionRequest
from ..utils.decorators import student_required

bp = Blueprint('points', __name__, url_prefix='/api/points')

@bp.route('/balance', methods=['GET'])
@student_required
def get_balance():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        student = user.student_profile
        
        return jsonify({
            'points_balance': student.points_balance
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/history', methods=['GET'])
@student_required
def get_history():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        student = user.student_profile
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        transactions = PointsTransaction.query.filter_by(student_id=student.id)\
            .order_by(PointsTransaction.created_at.desc())\
            .paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'transactions': [t.to_dict() for t in transactions.items],
            'total': transactions.total,
            'pages': transactions.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/redeem', methods=['POST'])
@student_required
def redeem_points():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        student = user.student_profile
        
        data = request.get_json()
        points = data.get('points', 0)
        redemption_type = data.get('type')  # 'gift_card' or 'upi'
        upi_id = data.get('upi_id')
        
        if points <= 0:
            return jsonify({'error': 'Invalid points amount'}), 400
        
        if points > student.points_balance:
            return jsonify({'error': 'Insufficient points'}), 400
        
        if redemption_type not in ['gift_card', 'upi']:
            return jsonify({'error': 'Invalid redemption type'}), 400
        
        if redemption_type == 'upi' and not upi_id:
            return jsonify({'error': 'UPI ID required for UPI redemption'}), 400
        
        # Deduct points
        student.points_balance -= points
        
        # Create transaction
        transaction = PointsTransaction(
            student_id=student.id,
            points=-points,
            transaction_type='redeemed',
            description=f'Redeemed for {redemption_type}'
        )
        db.session.add(transaction)
        
        # Create redemption request
        redemption = RedemptionRequest(
            student_id=student.id,
            points_redeemed=points,
            redemption_type=redemption_type,
            upi_id=upi_id
        )
        db.session.add(redemption)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Redemption request submitted successfully',
            'remaining_balance': student.points_balance,
            'redemption': redemption.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/redemptions', methods=['GET'])
@student_required
def get_redemptions():
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        student = user.student_profile
        
        redemptions = RedemptionRequest.query.filter_by(student_id=student.id)\
            .order_by(RedemptionRequest.created_at.desc())\
            .all()
        
        return jsonify({
            'redemptions': [r.to_dict() for r in redemptions]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500