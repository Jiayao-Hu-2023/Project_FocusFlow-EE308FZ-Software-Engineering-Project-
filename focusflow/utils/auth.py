from functools import wraps
from flask import session, redirect, url_for, flash

# 登录装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('请先登录')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# 验证用户身份
def verify_user_identity(user, phone, first_name, last_name, school, email):
    """验证用户身份信息，用于忘记密码功能"""
    if not user:
        return False
    
    if user['phone'] != phone:
        return False
    if user['first_name'] != first_name:
        return False
    if user['last_name'] != last_name:
        return False
    if user['school'] != school:
        return False
    if user['email'] != email:
        return False
    
    return True