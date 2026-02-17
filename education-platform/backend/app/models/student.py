# backend/app/models/student.py
from . import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    education = db.Column(db.String(200))
    profession = db.Column(db.String(100))
    mobile = db.Column(db.String(15))
    points_balance = db.Column(db.Integer, default=0)
    total_video_time = db.Column(db.Integer, default=0)  # in seconds
    training_progress = db.Column(db.Integer, default=0)  # percentage
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    points_history = db.relationship('PointsTransaction', backref='student', lazy='dynamic')
    sessions = db.relationship('VideoSession', foreign_keys='VideoSession.student_id', backref='student')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'education': self.education,
            'profession': self.profession,
            'mobile': self.mobile,
            'points_balance': self.points_balance,
            'total_video_time': self.total_video_time,
            'training_progress': self.training_progress
        }