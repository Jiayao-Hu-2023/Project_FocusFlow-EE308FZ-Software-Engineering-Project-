import sys
import sqlite3
import bcrypt
from flask import Flask


def init_database():
    """初始化SQLite数据库"""
    try:
        # 创建数据库连接
        conn = sqlite3.connect('focusflow.db')
        cursor = conn.cursor()

        # 检查表是否存在的函数
        def table_exists(table_name):
            cursor.execute(""" 
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name=? 
            """, (table_name,))
            return cursor.fetchone() is not None

        # 检查表是否存在，只在不存在时创建
        tables_to_check = ['users', 'checkins', 'tasks', 'subtasks', 'task_tags', 'focus_sessions', 'grades']
        tables_to_create = [table for table in tables_to_check if not table_exists(table)]

        # 如果有表需要创建，读取并执行schema.sql
        if tables_to_create:
            print(f"需要创建以下表: {', '.join(tables_to_create)}")
            with open('schema.sql', 'r', encoding='utf-8') as f:
                schema = f.read()
            cursor.executescript(schema)
        else:
            print("所有表已存在，跳过表创建步骤")

        # 检查是否需要插入示例用户数据
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 0:
            # 使用bcrypt哈希密码，与app.py中的做法一致
            hashed_password = bcrypt.generate_password_hash('admin123').decode('utf-8')

            cursor.execute("""
                INSERT INTO users (phone, first_name, last_name, email, gender, birth_date, 
                                school, education_level, grade, password)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                '13800138000', '管理员', '用户', 'admin@example.com', '男', '2000-01-01',
                '示例大学', '大学本科', '大一', hashed_password
            ))
            print("示例用户已成功插入")
        else:
            print(f"用户表已有 {user_count} 条记录，跳过示例用户插入")

        # 提交并关闭连接
        conn.commit()
        conn.close()
        print("数据库初始化成功！")
    except Exception as e:
        print(f"数据库初始化失败: {e}")


if __name__ == '__main__':
    print("开始初始化FocusFlow项目...")
    init_database()
    print("初始化完成！")