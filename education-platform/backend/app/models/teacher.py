from . import db
from datetime import datetime

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer)
    education = db.Column(db.String(200))
    profession = db.Column(db.String(100))
    mobile = db.Column(db.String(15), nullable=False)
    total_teaching_time = db.Column(db.Integer, default=0)  # in seconds
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    sessions = db.relationship('VideoSession', foreign_keys='VideoSession.teacher_id', backref='teacher')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'age': self.age,
            'education': self.education,
            'profession': self.profession,
            'mobile': self.mobile,
            'total_teaching_time': self.total_teaching_time,
            'is_available': self.is_available
        }