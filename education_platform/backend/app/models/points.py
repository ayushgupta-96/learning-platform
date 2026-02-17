# backend/app/models/points.py
from . import db
from datetime import datetime

class PointsTransaction(db.Model):
    __tablename__ = 'points_transactions'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    points = db.Column(db.Integer, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)  # 'earned' or 'redeemed'
    description = db.Column(db.String(200))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'points': self.points,
            'transaction_type': self.transaction_type,
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }


class RedemptionRequest(db.Model):
    __tablename__ = 'redemption_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    points_redeemed = db.Column(db.Integer, nullable=False)
    redemption_type = db.Column(db.String(50), nullable=False)  # 'gift_card' or 'upi'
    upi_id = db.Column(db.String(100))
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        return {
            'id': self.id,
            'points_redeemed': self.points_redeemed,
            'redemption_type': self.redemption_type,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }
