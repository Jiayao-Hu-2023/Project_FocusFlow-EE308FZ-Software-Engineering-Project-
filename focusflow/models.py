from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, id=None, phone=None, first_name=None, last_name=None, email=None, 
                 gender=None, birth_date=None, school=None, education_level=None, grade=None, 
                 password=None, created_at=None):
        self.id = id
        self.phone = phone
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.gender = gender
        self.birth_date = birth_date
        self.school = school
        self.education_level = education_level
        self.grade = grade
        self.password = password
        self.created_at = created_at
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password, password)
    
    def get_initials(self):
        return self.first_name[0] + self.last_name[0]

class Task:
    def __init__(self, id=None, user_id=None, title=None, description=None, course=None, 
                 priority='medium', status='pending', due_date=None, repeat=None, 
                 created_at=None, updated_at=None):
        self.id = id
        self.user_id = user_id
        self.title = title
        self.description = description
        self.course = course
        self.priority = priority  # high, medium, low
        self.status = status      # pending, in_progress, completed
        self.due_date = due_date
        self.repeat = repeat      # daily, weekly, monthly
        self.created_at = created_at
        self.updated_at = updated_at

class Subtask:
    def __init__(self, id=None, task_id=None, title=None, completed=0):
        self.id = id
        self.task_id = task_id
        self.title = title
        self.completed = completed

class FocusSession:
    def __init__(self, id=None, user_id=None, task_id=None, duration=None, 
                 start_time=None, end_time=None):
        self.id = id
        self.user_id = user_id
        self.task_id = task_id
        self.duration = duration
        self.start_time = start_time
        self.end_time = end_time

class Grade:
    def __init__(self, id=None, user_id=None, course=None, assessment_type=None, 
                 score=None, weight=1.0, date=None):
        self.id = id
        self.user_id = user_id
        self.course = course
        self.assessment_type = assessment_type
        self.score = score
        self.weight = weight
        self.date = date

class Checkin:
    def __init__(self, id=None, user_id=None, date=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.created_at = created_at