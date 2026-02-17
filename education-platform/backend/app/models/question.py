# backend/app/models/question.py
from . import db
from datetime import datetime

class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(20), nullable=False)  # 'mcq' or 'speaking'
    difficulty = db.Column(db.String(20), default='easy')  # easy, medium, hard
    points_value = db.Column(db.Integer, nullable=False)
    
    # For MCQ questions
    option_a = db.Column(db.String(200))
    option_b = db.Column(db.String(200))
    option_c = db.Column(db.String(200))
    option_d = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))  # A, B, C, or D
    
    # For speaking prompts
    expected_keywords = db.Column(db.Text)  # JSON string of keywords
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        result = {
            'id': self.id,
            'question_text': self.question_text,
            'question_type': self.question_type,
            'difficulty': self.difficulty,
            'points_value': self.points_value
        }
        
        if self.question_type == 'mcq':
            result.update({
                'option_a': self.option_a,
                'option_b': self.option_b,
                'option_c': self.option_c,
                'option_d': self.option_d
            })
        
        return result


 