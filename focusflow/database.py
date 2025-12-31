import sqlite3
import os
from datetime import datetime
from app import app

# 获取数据库连接
def get_db_connection():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

# 关闭数据库连接
def close_db_connection(conn):
    if conn:
        conn.close()

# 用户相关操作
class UserDB:
    @staticmethod
    def get_user_by_id(user_id):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def get_user_by_phone(phone):
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
        conn.close()
        return user
    
    @staticmethod
    def create_user(user_data):
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO users (phone, first_name, last_name, email, gender, birth_date, 
                            school, education_level, grade, password)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data['phone'], user_data['first_name'], user_data['last_name'], 
            user_data['email'], user_data.get('gender', ''), user_data.get('birth_date', ''),
            user_data.get('school', ''), user_data['education_level'], user_data.get('grade', ''),
            user_data['password']
        ))
        conn.commit()
        user_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return user_id
    
    @staticmethod
    def update_user(user_id, user_data):
        conn = get_db_connection()
        # 构建更新语句
        update_fields = []
        update_values = []
        
        for key, value in user_data.items():
            if key != 'id' and value is not None:
                update_fields.append(f"{key} = ?")
                update_values.append(value)
        
        update_values.append(user_id)
        
        conn.execute(f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?", tuple(update_values))
        conn.commit()
        conn.close()

# 任务相关操作
class TaskDB:
    @staticmethod
    def get_tasks_by_user(user_id):
        conn = get_db_connection()
        tasks = conn.execute('''
            SELECT * FROM tasks WHERE user_id = ? ORDER BY due_date ASC
        ''', (user_id,)).fetchall()
        conn.close()
        return tasks
    
    @staticmethod
    def get_task_by_id(task_id):
        conn = get_db_connection()
        task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
        conn.close()
        return task
    @staticmethod
    def create_task(task_data):
        conn = get_db_connection()
        conn.execute('''
            INSERT INTO tasks (user_id, title, description, course, priority, status, 
                             due_date, repeat, estimated_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            task_data['user_id'], task_data['title'], task_data.get('description', ''),
            task_data.get('course', ''), task_data.get('priority', 'medium'),
            task_data.get('status', 'pending'), task_data.get('due_date', ''),
            task_data.get('repeat', ''), task_data.get('estimated_time', 60)
        ))
        conn.commit()
        task_id = conn.execute('SELECT last_insert_rowid()').fetchone()[0]
        conn.close()
        return task_id
    
    @staticmethod
    def update_task(task_id, task_data):
        conn = get_db_connection()
        # 构建更新语句
        update_fields = []
        update_values = []
        
        for key, value in task_data.items():
            if key != 'id' and value is not None:
                update_fields.append(f"{key} = ?")
                update_values.append(value)
        
        update_values.append(task_id)
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        conn.execute(f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?", tuple(update_values))
        conn.commit()
        conn.close()
    
    @staticmethod
    def delete_task(task_id):
        conn = get_db_connection()
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        conn.close()

# 专注记录相关操作
class FocusSessionDB:
    @staticmethod
    def get_total_focus_time(user_id):
        """获取用户的总专注时长（分钟）"""
        conn = get_db_connection()
        result = conn.execute('''
            SELECT SUM(duration) as total_duration
            FROM focus_sessions 
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        conn.close()
        return result['total_duration'] or 0
    
    @staticmethod
    def get_weekly_focus_time(user_id):
        """获取用户本周的专注时长（分钟）"""
        conn = get_db_connection()
        # 获取本周开始日期（周一）
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        result = conn.execute('''
            SELECT SUM(duration) as weekly_duration
            FROM focus_sessions 
            WHERE user_id = ? AND DATE(start_time) >= ?
        ''', (user_id, start_of_week)).fetchone()
        conn.close()
        return result['weekly_duration'] or 0

# 签到相关操作
class CheckinDB:
    @staticmethod
    def get_total_checkins(user_id):
        """获取用户的总签到次数"""
        conn = get_db_connection()
        result = conn.execute('''
            SELECT COUNT(*) as total_checkins
            FROM checkins 
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        conn.close()
        return result['total_checkins'] or 0
    
    @staticmethod
    def get_monthly_checkins(user_id):
        """获取用户本月的签到次数"""
        conn = get_db_connection()
        # 获取本月第一天
        today = datetime.now()
        start_of_month = today.replace(day=1).date()
        
        result = conn.execute('''
            SELECT COUNT(*) as monthly_checkins
            FROM checkins 
            WHERE user_id = ? AND DATE(date) >= ?
        ''', (user_id, start_of_month)).fetchone()
        conn.close()
        return result['monthly_checkins'] or 0
    
    @staticmethod
    def get_streak_days(user_id):
        """获取用户的连续签到天数"""
        conn = get_db_connection()
        # 获取所有签到日期并按日期排序
        checkin_dates = conn.execute('''
            SELECT date FROM checkins 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (user_id,)).fetchall()
        conn.close()
        
        if not checkin_dates:
            return 0
        
        # 将日期字符串转换为日期对象
        dates = [datetime.strptime(row['date'], '%Y-%m-%d').date() for row in checkin_dates]
        
        # 计算连续签到天数
        streak = 0
        current_date = datetime.now().date()
        
        for date in dates:
            if date == current_date:
                streak += 1
                current_date -= timedelta(days=1)
            elif date == current_date - timedelta(days=1):
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
                
        return streak

# 报告相关操作
class ReportDB:
    @staticmethod
    def get_completed_tasks_count(user_id):
        """获取用户已完成的任务数量"""
        conn = get_db_connection()
        result = conn.execute('''
            SELECT COUNT(*) as completed_tasks
            FROM tasks 
            WHERE user_id = ? AND status = 'completed'
        ''', (user_id,)).fetchone()
        conn.close()
        return result['completed_tasks'] or 0
    
    @staticmethod
    def get_weekly_completed_tasks(user_id):
        """获取用户本周完成的任务数量"""
        conn = get_db_connection()
        # 获取本周开始日期（周一）
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        
        result = conn.execute('''
            SELECT COUNT(*) as weekly_completed
            FROM tasks 
            WHERE user_id = ? AND status = 'completed' AND due_date >= ?
        ''', (user_id, start_of_week)).fetchone()
        conn.close()
        return result['weekly_completed'] or 0
    
    @staticmethod
    def get_task_completion_rate(user_id):
        """计算用户的任务完成率"""
        conn = get_db_connection()
        result = conn.execute('''
            SELECT 
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
                COUNT(*) as total
            FROM tasks 
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        conn.close()
        
        if result['total'] == 0:
            return 0
        
        return int((result['completed'] / result['total']) * 100)

# 导入timedelta用于日期计算
from datetime import timedelta