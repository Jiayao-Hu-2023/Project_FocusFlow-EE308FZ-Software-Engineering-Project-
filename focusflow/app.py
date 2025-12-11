# 修改导入语句，添加g对象
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g
from flask_bcrypt import Bcrypt
import sqlite3
import os
from datetime import datetime, timedelta
import random
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DATABASE'] = os.path.join(app.root_path, 'focusflow.db')
bcrypt = Bcrypt(app)

print("=== FocusFlow应用启动 ===")
print(f"数据库路径: {app.config['DATABASE']}")


# 数据库连接函数
def get_db_connection():
    print("[调试] 尝试连接数据库...")
    try:
        conn = sqlite3.connect(app.config['DATABASE'])
        conn.row_factory = sqlite3.Row
        print("[调试] 数据库连接成功")
        return conn
    except Exception as e:
        print(f"[调试] 数据库连接失败: {str(e)}")
        raise


# 初始化数据库
def init_db():
    print("[调试] 初始化数据库...")
    try:
        conn = get_db_connection()
        with app.open_resource('schema.sql', mode='r') as f:
            conn.executescript(f.read())
        conn.commit()
        print("[调试] 数据库初始化成功")
    except Exception as e:
        print(f"[调试] 数据库初始化失败: {str(e)}")
        raise
    finally:
        conn.close()


# 创建所需的数据库表
@app.cli.command('init-db')
def init_db_command():
    print("[调试] 执行init-db命令...")
    init_db()
    print('Initialized the database.')


# 语言支持
def get_translations(lang='en-US'):
    print(f"[调试] 获取语言翻译，语言: {lang}")
    translations = {
        'en-US': {
            'welcome': 'Welcome',
            'login': 'Login',
            'register': 'Register',
            'phone': 'Phone Number',
            'password': 'Password',
            'confirm_password': 'Confirm Password',
            'forgot_password': 'Forgot Password',
            'dashboard': 'Dashboard',
            'profile': 'Profile',
            'tasks': 'Tasks',
            'focus': 'Focus Mode',
            'reports': 'Reports',
            'logout': 'Logout',
            # 更多翻译...
        },
        # 'zh-CN': {
        #     'welcome': '欢迎',
        #     'login': '登录',
        #     'register': '注册',
        #     'phone': '电话号码',
        #     'password': '密码',
        #     'confirm_password': '确认密码',
        #     'forgot_password': '忘记密码',
        #     'dashboard': '仪表盘',
        #     'profile': '个人中心',
        #     'tasks': '任务',
        #     'focus': '专注模式',
        #     'reports': '报告',
        #     'logout': '退出登录',
        #     # 更多翻译...
        # },
        # 'zh-TW': {
        #     'welcome': '欢迎',
        #     'login': '登录',
        #     'register': '注册',
        #     'phone': '电话号码',
        #     'password': '密码',
        #     'confirm_password': '确认密码',
        #     'forgot_password': '忘记密码',
        #     'dashboard': '仪表盘',
        #     'profile': '个人中心',
        #     'tasks': '任务',
        #     'focus': '专注模式',
        #     'reports': '报告',
        #     'logout': '退出登录',
        #     # 更多翻译...
        # }
    }
    result = translations.get(lang, translations['en-US'])
    print(f"[调试] 语言翻译获取成功，返回了{len(result)}个翻译项")
    return result


# 身份验证装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        print(f"[调试] 验证用户登录状态，session中的user_id: {session.get('user_id')}")
        if 'user_id' not in session:
            print("[调试] 用户未登录，重定向到登录页面")
            return redirect(url_for('login'))
        print("[调试] 用户已登录，继续执行请求")
        return f(*args, **kwargs)

    return decorated_function


# 在文件顶部导入辅助函数
from utils.helpers import generate_avatar_data


@app.before_request
def before_request():
    # 如果用户已登录，为模板全局上下文添加头像数据
    if 'user_id' in session:
        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            if user:
                # 调用generate_avatar_data函数生成头像数据
                initials, user_avatar_color = generate_avatar_data(user)
                # 将头像数据添加到g对象，使其在所有模板中可用
                g.initials = initials
                g.user_avatar_color = user_avatar_color

                # 添加用户真实姓名到g对象
                try:
                    # 尝试获取名字和姓氏
                    first_name = ''
                    last_name = ''

                    # 安全地获取名字和姓氏，兼容字典式和属性式访问
                    if hasattr(user, '__contains__') and 'first_name' in user and user['first_name']:
                        first_name = str(user['first_name']).strip()
                    elif hasattr(user, 'first_name') and user.first_name:
                        first_name = str(user.first_name).strip()

                    if hasattr(user, '__contains__') and 'last_name' in user and user['last_name']:
                        last_name = str(user['last_name']).strip()
                    elif hasattr(user, 'last_name') and user.last_name:
                        last_name = str(user.last_name).strip()

                    # 组合成完整姓名（中文名字通常姓在前名在后，英文名字名在前姓在后）
                    # 这里我们简单地将姓和名连接起来
                    g.user_name = f"{first_name} {last_name}".strip() if first_name or last_name else "User"
                except Exception:
                    g.user_name = "User"
                
                # 计算总学习时间
                try:
                    total_stats = conn.execute('''
                        SELECT SUM(duration) as total_minutes
                        FROM focus_sessions
                        WHERE user_id = ? AND end_time IS NOT NULL
                    ''', (session['user_id'],)).fetchone()
                    
                    total_minutes = total_stats['total_minutes'] or 0
                    hours = total_minutes // 60
                    minutes = total_minutes % 60
                    
                    if hours > 0:
                        g.total_study_time = f"{hours}h {minutes}m"
                    else:
                        g.total_study_time = f"{minutes}m"
                except Exception:
                    g.total_study_time = "0h 0m"
        except Exception:
            # 发生错误时不做处理，让模板使用默认值
            pass
        finally:
            conn.close()


# 修改base.html中使用g对象的头像显示



# 路由：登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("[调试] 访问登录页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)

    if request.method == 'GET':
        # 只在GET请求时生成新的验证码
        import random
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        captcha_answer = str(num1 + num2)
        captcha_question = f"{num1} + {num2} = ?"

        # 将答案保存到session中
        session['captcha_answer'] = captcha_answer
        print(f"[调试] 生成验证码: {captcha_question}, 答案: {captcha_answer}")
        # 添加GET请求时的返回语句
        return render_template('login.html', translations=translations, lang=lang, captcha_question=captcha_question)
    else:
        # POST请求时从session获取之前生成的问题
        captcha_question = f"{session.get('num1', 0)} + {session.get('num2', 0)} = ?"

    if request.method == 'POST':
        print("[调试] 处理登录POST请求")
        phone = request.form.get('phone')
        password = request.form.get('password')
        user_captcha = request.form.get('captcha')

        print(f"[调试] 登录请求参数 - phone: {phone}, captcha: {user_captcha}")

        # 从session中获取正确答案进行验证
        correct_answer = session.get('captcha_answer', '')
        print(f"[调试] 验证验证码 - 用户输入: {user_captcha}, 正确答案: {correct_answer}")

        if user_captcha != correct_answer:
            print("[调试] 验证码错误")
            flash('Captcha answer WRONG!')
            # 生成新的验证码
            import random
            num1 = random.randint(1, 10)
            num2 = random.randint(1, 10)
            new_captcha_answer = str(num1 + num2)
            new_captcha_question = f"{num1} + {num2} = ?"
            session['captcha_answer'] = new_captcha_answer
            return render_template('login.html', translations=translations, lang=lang,
                                   captcha_question=new_captcha_question)

        conn = get_db_connection()
        try:
            print("[调试] 查询用户信息")
            user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()

            if user:
                print(f"[调试] 找到用户: {user['phone']}")
                if bcrypt.check_password_hash(user['password'], password):
                    print("[调试] 密码验证成功，设置用户会话")
                    session['user_id'] = user['id']
                    # 登录成功后清除验证码
                    session.pop('captcha_answer', None)
                    flash('Login SUCCESS!')
                    return redirect(url_for('dashboard', lang=lang))
                else:
                    print("[调试] 密码验证失败")
                    flash('Password WRONG!')
            else:
                print("[调试] 未找到用户")
                flash('User NOT FOUND!')
        except Exception as e:
            print(f"[调试] 登录过程中出现错误: {str(e)}")
            flash('Login FAILED! Please try again.')
        finally:
            conn.close()

        # 密码错误或其他错误时，生成新的验证码
        import random
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)
        new_captcha_answer = str(num1 + num2)
        new_captcha_question = f"{num1} + {num2} = ?"
        session['captcha_answer'] = new_captcha_answer
        return render_template('login.html', translations=translations, lang=lang,
                               captcha_question=new_captcha_question)
    return None


# 路由：注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    print("[调试] 访问注册页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)

    if request.method == 'POST':
        print("[调试] 处理注册POST请求")
        phone = request.form.get('phone')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        email = request.form.get('email')
        education_level = request.form.get('education_level')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        print(f"[调试] 注册请求参数 - phone: {phone}, first_name: {first_name}, last_name: {last_name}, email: {email}")

        if password != confirm_password:
            print("[调试] 两次输入的密码不一致")
            flash('Two passwords do NOT match!')
            return redirect(url_for('register', lang=lang))

        conn = get_db_connection()
        try:
            print("[调试] 检查手机号是否已被注册")
            existing_user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
            if existing_user:
                print("[调试] 手机号已被注册")
                flash('This phone number has already been registered!')
                return redirect(url_for('register', lang=lang))
                print("[调试] 检查邮箱是否已被注册")
            existing_email = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
            if existing_email:
                print("[调试] 邮箱已被注册")
                flash('This email has already been registered!')
                return redirect(url_for('register', lang=lang))

            print("[调试] 密码加密")
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

            print("[调试] 插入新用户记录")
            conn.execute('''
                INSERT INTO users (phone, first_name, last_name, email, education_level, password)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (phone, first_name, last_name, email, education_level, hashed_password))
            conn.commit()

            print("[调试] 注册成功，获取新用户ID")
            user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
            session['user_id'] = user['id']

            flash('Registration SUCCESS!')
            return redirect(url_for('dashboard', lang=lang))
        except Exception as e:
            print(f"[调试] 注册过程中出现错误: {str(e)}")
            flash('Registration FAILED! Please try again.')
        finally:
            conn.close()

    # 教育级别选项
    education_levels = ['Elementary school', 'Junior high school', 'Senior high school', 'Undergraduate', 'Master', 'Doctor']

    return render_template('register.html', translations=translations, lang=lang, education_levels=education_levels)


# 路由：忘记密码
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    print("[调试] 访问忘记密码页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)

    if request.method == 'POST':
        print("[调试] 处理忘记密码POST请求")
        phone = request.form.get('phone')
        last_name = request.form.get('last_name')
        first_name = request.form.get('first_name')
        school = request.form.get('school')
        email = request.form.get('email')

        print(f"[调试] 忘记密码请求参数 - phone: {phone}, last_name: {last_name}, first_name: {first_name}, school: {school}, email: {email}")

        conn = get_db_connection()
        try:
            print("[调试] 查询用户信息")
            # 修改SQL查询，增加对姓名等信息的验证
            user = conn.execute('''
                SELECT * FROM users 
                WHERE phone = ? AND last_name = ? AND first_name = ?
            ''', (phone, last_name, first_name)).fetchone()

            if user:
                print("[调试] 找到用户，模拟发送重置密码邮件/SMS")
                # 这里应该发送重置密码的邮件或短信
                flash('Processing SUCCESS!')
            else:
                print("[调试] 未找到用户或信息不匹配")
                flash('Phone number or name does NOT match!')
        except Exception as e:
            print(f"[调试] 处理忘记密码请求时出现错误: {str(e)}")
            flash('Processing FAILED! Please try again.')
        finally:
            conn.close()

    return render_template('forgot_password.html', translations=translations, lang=lang)






# 路由：仪表盘
@app.route('/dashboard')
@login_required
def dashboard():
    print("[调试] 访问仪表盘页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        # 获取用户信息
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        
        # 添加基于时间的问候语逻辑
        current_hour = datetime.now().hour
        if user:
            user_name = user['first_name'] or 'User'
        else:
            user_name = 'User'
        
        if 0 <= current_hour < 12:
            greeting = f"Good morning, {user_name}!"
        elif 12 <= current_hour < 18:
            greeting = f"Good afternoon, {user_name}!"
        else:
            greeting = f"Good evening, {user_name}!"

        print(f"[调试] 获取用户 {user_id} 的任务列表")
        tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY due_date ASC LIMIT 5',
                             (user_id,)).fetchall()
        
        print(f"[调试] 获取用户 {user_id} 的签到信息")
        today = datetime.now().strftime('%Y-%m-%d')
        has_checked_in = conn.execute('SELECT * FROM checkins WHERE user_id = ? AND date = ?',
                                      (user_id, today)).fetchone() is not None

        # 计算任务进度
        # 获取今天的日期
        today_date = datetime.now().date()
        today_str = today_date.strftime('%Y-%m-%d')

        # 获取今天的任务数量
        today_tasks_query = conn.execute('''
            SELECT * FROM tasks WHERE user_id = ? AND date(due_date) = ?
        ''', (user_id, today_str)).fetchall()

        # 计算已完成和总任务数
        completed_today = sum(1 for task in today_tasks_query if task['status'] == 'completed')
        total_today = len(today_tasks_query)
        task_progress_percentage = (completed_today / total_today * 100) if total_today > 0 else 0
        # 获取连续签到天数
        streak_days = 0
        checkin_dates = conn.execute('''
            SELECT date FROM checkins WHERE user_id = ? ORDER BY date DESC
        ''', (user_id,)).fetchall()

        if checkin_dates:
            current_date = datetime.now().date()
            for checkin_date in checkin_dates:
                checkin_date_obj = datetime.strptime(checkin_date['date'], '%Y-%m-%d').date()
                if (current_date - checkin_date_obj).days == streak_days:
                    streak_days += 1
                else:
                    break

        # 获取本周专注时长（小时）
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
        focus_time_query = conn.execute('''
            SELECT SUM(duration) as total_minutes 
            FROM focus_sessions 
            WHERE user_id = ? AND date(start_time) >= ?
        ''', (user_id, week_start)).fetchone()

        # 修改为计算小时和分钟
        total_minutes = focus_time_query['total_minutes'] or 0
        focus_hours = total_minutes // 60
        focus_minutes = total_minutes % 60
        weekly_focus_time = {'hours': focus_hours, 'minutes': focus_minutes}

        # 获取已完成任务总数
        completed_tasks_query = conn.execute('''
            SELECT COUNT(*) as count FROM tasks WHERE user_id = ? AND status = 'completed'
        ''', (user_id,)).fetchone()
        completed_tasks = completed_tasks_query['count']

        # 获取总任务数
        total_tasks_query = conn.execute('''
            SELECT COUNT(*) as count FROM tasks WHERE user_id = ?
        ''', (user_id,)).fetchone()
        total_tasks = total_tasks_query['count']

        # 获取专注会话统计
        # 获取专注会话统计 - 修复版本
        sessions_query = conn.execute('''
            SELECT COUNT(*) as total, SUM(CASE WHEN end_time IS NOT NULL THEN 1 ELSE 0 END) as completed 
            FROM focus_sessions 
            WHERE user_id = ? AND date(start_time) >= ?
        ''', (user_id, week_start)).fetchone()
        total_sessions = sessions_query['total'] or 0
        completed_sessions = sessions_query['completed'] or 0

        # 计算任务完成率
        task_completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

        # 生成最近7天的学习趋势数据（基于签到和专注时间）
        # 在reports路由函数中，修改生成weekly_trend的代码部分（约820-840行）
        weekly_trend = []
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # 计算最近7天的日期
        for i in range(6, -1, -1):
            # 获取日期
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            weekday_name = weekdays[date.weekday()]

            # 检查是否签到
            is_checked_in = conn.execute('''
            SELECT * FROM checkins WHERE user_id = ? AND date = ?
            ''', (user_id, date_str)).fetchone() is not None

            # 获取当天的专注时间（分钟转换为小时）
            focus_query = conn.execute('''
                SELECT SUM(duration) as total_minutes 
                FROM focus_sessions 
                WHERE user_id = ? AND date(start_time) = ?
            ''', (user_id, date_str)).fetchone()

            focus_hours = focus_query['total_minutes'] / 60 if focus_query['total_minutes'] else 0

            # 获取当天完成的任务 - 添加这部分代码
            completed_tasks_day = conn.execute('''
                SELECT t.id, t.title, t.description, t.course, t.updated_at as completion_time 
                FROM tasks t 
                WHERE t.user_id = ? AND t.status = 'completed' AND date(t.updated_at) = ?
                ORDER BY t.updated_at DESC
            ''', (user_id, date_str)).fetchall()

            # 格式化任务数据 - 添加这部分代码
            tasks_data = []
            for task in completed_tasks_day:
                tasks_data.append({
                    'id': task['id'],
                    'title': task['title'],
                    'description': task['description'],
                    'course_info': task['course'] if task['course'] else '无课程信息',
                    'completion_time': task['completion_time']
                })

            weekly_trend.append({
                'day': weekday_name,
                'value': round(focus_hours, 1),
                'date': date_str,
                'date_display': date.strftime('%m月%d日'),
                'checked_in': is_checked_in,
                'tasks': tasks_data,  # 添加任务数据
                'task_count': len(tasks_data)  # 添加任务数量
            })

        # 获取签到详情（仅显示签到的日期）
        checked_in_dates = []
        for trend_data in weekly_trend:
            if trend_data['checked_in']:
                checked_in_dates.append({
                    'date': trend_data['date'],
                    'date_display': trend_data['date_display'],
                    'day': trend_data['day'],
                    'focus_hours': trend_data['value']
                })

        # 组装统计数据
        weekly_stats = {
            'focus_time': weekly_focus_time,  # 使用已计算的weekly_focus_time
            'completed_sessions': completed_sessions,  # 已定义的变量
            'total_sessions': total_sessions,  # 已定义的变量
            'completed_tasks': completed_tasks,  # 已定义的变量
            'total_tasks': total_tasks,  # 新增的变量
            'productivity_score': task_completion_rate,  # 新增的变量
            'streak_days': streak_days  # 已定义的变量
        }
        print(f"[调试] 最终统计数据: {weekly_stats}")
        print(f"[调试] 趋势数据: {weekly_trend}")

    except Exception as e:
        print(f"[调试] 获取报告数据时出现错误: {str(e)}")
        weekly_stats = {'focus_time': 0, 'completed_sessions': 0, 'total_sessions': 0, 'completed_tasks': 0,
                        'total_tasks': 0, 'productivity_score': 0, 'streak_days': 0}
        weekly_trend = []
        checked_in_dates = []
        # 初始化user为None
        user = None
        # 发生错误时使用空的趋势数据
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        for i in range(6, -1, -1):
            date = datetime.now() - timedelta(days=i)
            weekly_trend.append({
                'day': weekdays[date.weekday()],
                'value': 0,
                'date': date.strftime('%Y-%m-%d'),
                'date_display': date.strftime('%m月%d日'),
                'checked_in': False,
                'tasks': [],
                'task_count': 0
            })
    finally:
        conn.close()

    # 修改render_template调用，添加缺失的变量
    return render_template('dashboard.html',
                           translations=translations,
                           lang=lang,
                           tasks=tasks,
                           user=user,
                           # 添加缺失的变量
                           today_tasks=today_tasks_query,  # 使用已查询的today_tasks_query
                           completed_today=completed_today,  # 已计算的已完成任务数
                           total_today=total_today,  # 已计算的总任务数
                           weekly_trend=weekly_trend,  # 7天学习趋势数据
                           # 原有的变量继续保留
                           has_checked_in=has_checked_in,
                           task_progress_percentage=task_progress_percentage,
                           streak_days=streak_days,
                           weekly_focus_time=weekly_focus_time,
                           completed_tasks=completed_tasks,
                           # 添加greeting变量
                           greeting=greeting)


# 路由：签到功能
@app.route('/checkin', methods=['POST'])
@login_required
def checkin():
    print("[调试] 用户尝试签到")
    user_id = session['user_id']
    today = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    try:
        # 检查今天是否已经签到
        existing_checkin = conn.execute(
            'SELECT * FROM checkins WHERE user_id = ? AND date = ?',
            (user_id, today)
        ).fetchone()

        if existing_checkin:
            print("[调试] 用户今天已经签到过了")
            flash('You have already signed in today!', 'info')
        else:
            # 添加签到记录
            conn.execute(
                'INSERT INTO checkins (user_id, date) VALUES (?, ?)',
                (user_id, today)
            )
            conn.commit()
            print("[调试] 用户签到成功")
            flash('Sign in successful! Keep up the good work!', 'success')
    except Exception as e:
        print(f"[调试] 签到过程中出现错误: {str(e)}")
        flash('Sign in failed, please try again later', 'error')
        conn.rollback()
    finally:
        conn.close()

    # 重定向回仪表盘
    return redirect(url_for('dashboard'))


# 路由：任务列表
@app.route('/tasks')
@login_required
def tasks():
    print("[调试] 访问任务列表页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        print(f"[调试] 获取用户 {user_id} 的所有任务")
        tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ? ORDER BY due_date ASC', (user_id,)).fetchall()

        # 为每个任务获取标签并格式化日期
        tasks_with_tags = []
        today = datetime.now().date()
        
        for task in tasks:
            print(f"[调试] 获取任务 {task['id']} 的标签")
            tags = conn.execute('SELECT tag FROM task_tags WHERE task_id = ?', (task['id'],)).fetchall()
            task_dict = dict(task)
            task_dict['tags'] = [tag['tag'] for tag in tags]
            
            # Format due date
            if task_dict['due_date']:
                try:
                    due_date = datetime.strptime(task_dict['due_date'], '%Y-%m-%d').date()
                    days_diff = (due_date - today).days
                    
                    if days_diff == 0:
                        task_dict['due_date'] = 'Today'
                    elif days_diff == 1:
                        task_dict['due_date'] = 'Tomorrow'
                    elif days_diff > 1:
                        task_dict['due_date'] = f'{days_diff} days'
                    else:
                        task_dict['due_date'] = due_date.strftime('%Y-%m-%d')
                except:
                    task_dict['due_date'] = task_dict['due_date']
            
            # Calculate estimated time (default to 60 minutes if not set)
            # You can add an estimated_time field to the database later
            task_dict['estimated_time'] = 60  # Default value
            
            tasks_with_tags.append(task_dict)

    except Exception as e:
        print(f"[调试] 获取任务列表时出现错误: {str(e)}")
        tasks_with_tags = []
    finally:
        conn.close()

    return render_template('tasks.html', translations=translations, lang=lang, tasks=tasks_with_tags)


# 路由：创建/编辑任务
@app.route('/tasks/add', methods=['POST'])
@login_required
def add_task():
    """处理创建或编辑任务的请求"""
    print("[调试] 处理创建/编辑任务请求")
    user_id = session['user_id']

    # 获取表单数据
    task_id = request.form.get('task_id')
    title = request.form.get('task_title')
    description = request.form.get('task_description', '')
    course = request.form.get('task_course', '')
    priority = request.form.get('task_priority', 'medium')
    due_date = request.form.get('task_due_date')
    repeat = request.form.get('task_repeat', '')
    tags = request.form.get('task_tags', '')
    status = request.form.get('task_status', 'pending')

    # 添加详细的日志记录
    print(f"\n[调试] 任务请求参数:")
    print(f"[调试] task_id: {task_id}, user_id: {user_id}")
    print(f"[调试] title: {title}, course: {course}")
    print(f"[调试] due_date: {due_date}, priority: {priority}")

    # 服务器端验证 - 验证必填字段
    if not title:
        print("[调试] 任务标题为空，返回错误")
        flash('Please enter a task title!')
        return redirect(url_for('tasks'))

    if not due_date:
        print("[调试] 截止日期为空，返回错误")
        flash('Please select a due date!')
        return redirect(url_for('tasks'))

    conn = None
    try:
        conn = get_db_connection()
        # 统一使用conn.execute()，避免使用cursor带来的初始化问题

        # 检查是否是编辑任务
        if task_id:
            print(f"[调试] 编辑任务模式，任务ID: {task_id}")
            # 验证任务是否属于当前用户
            task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()
            if not task:
                print("[调试] 任务不存在或不属于当前用户")
                flash('Task not found or you do not have permission to edit this task!')
                return redirect(url_for('tasks'))

            # 更新任务
            print("[调试] 更新任务")
            conn.execute('''
                UPDATE tasks 
                SET title = ?, description = ?, course = ?, priority = ?, 
                    due_date = ?, repeat = ?, status = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ? 
            ''', (title, description, course, priority, due_date, repeat, status, task_id))
            print("[调试] 任务更新成功")

            # 删除旧标签
            print("[调试] 删除旧标签")
            conn.execute('DELETE FROM task_tags WHERE task_id = ?', (task_id,))
        else:
            print("[调试] 创建新任务模式")
            # 插入任务到数据库
            print("[调试] 插入任务到tasks表")
            cursor = conn.cursor()  # 这里使用cursor是为了获取lastrowid
            cursor.execute('''
                INSERT INTO tasks (user_id, title, description, course, priority, due_date, repeat, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, title, description, course, priority, due_date, repeat, status))

            # 获取新插入任务的ID
            task_id = cursor.lastrowid
            print(f"[调试] 任务插入成功，任务ID: {task_id}")

        # 处理标签（无论是创建还是编辑都需要处理）
        if tags:
            print(f"[调试] 处理任务标签: {tags}")
            tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
            print(f"[调试] 解析后的标签列表: {tag_list}")

            for tag in tag_list:
                print(f"[调试] 插入标签 '{tag}' 到task_tags表")
                conn.execute(
                    'INSERT INTO task_tags (task_id, tag) VALUES (?, ?)',
                    (task_id, tag)
                )
            print(f"[调试] 成功插入 {len(tag_list)} 个标签")

        # 提交事务
        print("[调试] 提交事务")
        conn.commit()
        flash('Task saved successfully!')

    except Exception as e:
        print(f"[调试] 任务保存失败: {str(e)}")
        flash('Task save failed, please try again later!')
        if conn:
            conn.rollback()  # 发生错误时回滚事务
    finally:
        print("[调试] 关闭数据库连接")
        if conn:
            conn.close()

    return redirect(url_for('tasks'))


# 路由：删除任务
@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    print(f"[调试] 处理删除任务请求，任务ID: {task_id}")
    user_id = session['user_id']

    conn = get_db_connection()
    try:
        print(f"[调试] 验证任务 {task_id} 是否属于用户 {user_id}")
        # 首先验证任务是否属于当前用户
        task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()

        if not task:
            print(f"[调试] 任务 {task_id} 不存在或不属于用户 {user_id}")
            flash('Task not found or you do not have permission to delete this task!')
            return redirect(url_for('tasks'))

        print(f"[调试] 开始删除任务 {task_id}")
        # 先删除任务相关的标签
        conn.execute('DELETE FROM task_tags WHERE task_id = ?', (task_id,))
        print(f"[调试] 已删除任务 {task_id} 的标签")
        # 删除任务本身
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        print(f"[调试] 成功删除任务 {task_id}")
        flash('Task deleted successfully!')
        return redirect(url_for('tasks'))
    except Exception as e:
        print(f"[调试] 删除任务时发生错误: {str(e)}")
        conn.rollback()
        flash('Task delete failed, please try again later!')
        return redirect(url_for('tasks'))
    finally:
        print("[调试] 关闭数据库连接")
        conn.close()


# 路由：统计页面
@app.route('/stats')
@login_required
def stats():
    print("[调试] 访问统计页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)
    user_id = session['user_id']

    # 获取时间范围参数
    time_range = request.args.get('range', 'week')
    today = datetime.now().date()

    if time_range == 'today':
        start_date = today
        end_date = today
    elif time_range == 'week':
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif time_range == 'month':
        start_date = today.replace(day=1)
        # 计算下个月的第一天，再减一天得到本月最后一天
        if today.month == 12:
            end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)


# 路由：报告
@app.route('/reports')
@login_required
def reports():
    print("[调试] 访问报告页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)
# 初始化变量，避免NameError
    weekly_stats = {'focus_time': 0, 'completed_sessions': 0, 'total_sessions': 0,
                    'completed_tasks': 0, 'total_tasks': 0, 'productivity_score': 0, 'streak_days': 0}
    weekly_trend = []
    checked_in_dates = []

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        # 获取专注时长数据 - 限制为最近7天
        week_start = (datetime.now() - timedelta(days=6)).strftime('%Y-%m-%d')
        focus_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_sessions,
                COUNT(CASE WHEN end_time IS NOT NULL THEN 1 END) as completed_sessions,
SUM(duration) as total_duration
            FROM focus_sessions 
            WHERE user_id = ? AND date(start_time) >= ?
        ''', (user_id, week_start)).fetchone()

        total_sessions = focus_stats['total_sessions'] or 0
        completed_sessions = focus_stats['completed_sessions'] or 0
        total_duration = focus_stats['total_duration'] or 0

        # 修改为计算小时和分钟
        focus_hours = total_duration // 60
        focus_minutes = total_duration % 60
        # 计算专注时长（小时和分钟）
        focus_time_info = {'hours': focus_hours, 'minutes': focus_minutes, 'total_minutes': total_duration}

        # 获取任务统计数据 - 限制为最近7天
        task_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_tasks,
                COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tasks
            FROM tasks 
            WHERE user_id = ? AND date(created_at) >= ?
        ''', (user_id, week_start)).fetchone()

        total_tasks = task_stats['total_tasks'] or 0
        completed_tasks = task_stats['completed_tasks'] or 0

        # 计算任务完成率
        if total_tasks == 0:
            task_completion_rate = 0
        else:
            task_completion_rate = int((completed_tasks / total_tasks) * 100)

        # 获取连续签到天数
        checkin_dates = conn.execute('''
            SELECT date FROM checkins 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (user_id,)).fetchall()

        streak_days = 0
        if checkin_dates:
            # 计算连续签到天数
            current_date = datetime.now().date()
            for checkin_date in checkin_dates:
                checkin_date_obj = datetime.strptime(checkin_date['date'], '%Y-%m-%d').date()
                if (current_date - checkin_date_obj).days == streak_days:
                    streak_days += 1
                else:
                    break

        # 组装统计数据
        weekly_stats = {
            'focus_time': focus_time_info,  # 总专注时长（小时和分钟）
            'completed_sessions': completed_sessions,  # 完成的专注会话数
            'total_sessions': total_sessions,  # 总专注会话数
            'completed_tasks': completed_tasks,  # 完成任务数
            'total_tasks': total_tasks,  # 总任务数
            'productivity_score': task_completion_rate,  # 任务完成率
            'streak_days': streak_days  # 连续签到天数
        }
        # 生成最近7天的学习趋势数据 - 修改这部分以添加任务信息
        weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # 计算最近7天的日期
        for i in range(6, -1, -1):
            # 获取日期
            date = datetime.now() - timedelta(days=i)
            date_str = date.strftime('%Y-%m-%d')
            weekday_name = weekdays[date.weekday()]

            # 检查是否签到
            is_checked_in = conn.execute('''
            SELECT * FROM checkins WHERE user_id = ? AND date = ?
            ''', (user_id, date_str)).fetchone() is not None

            # 获取当天的专注时间（分钟转换为小时和分钟）
            focus_query = conn.execute('''
                SELECT SUM(duration) as total_minutes 
                FROM focus_sessions 
                WHERE user_id = ? AND date(start_time) = ?
            ''', (user_id, date_str)).fetchone()

            # 修改为计算小时和分钟
            daily_minutes = focus_query['total_minutes'] or 0
            daily_hours = daily_minutes // 60
            daily_minutes_remainder = daily_minutes % 60
            focus_time = {'hours': daily_hours, 'minutes': daily_minutes_remainder}

            # 获取当天完成的任务 - 添加这部分代码
            completed_tasks_day = conn.execute('''
                SELECT t.id, t.title, t.description, t.course, t.updated_at as completion_time 
                FROM tasks t 
                WHERE t.user_id = ? AND t.status = 'completed' AND date(t.updated_at) = ?
                ORDER BY t.updated_at DESC
            ''', (user_id, date_str)).fetchall()

            # 格式化任务数据 - 添加这部分代码
            tasks_data = []
            for task in completed_tasks_day:
                tasks_data.append({
                    'id': task['id'],
                    'title': task['title'],
                    'description': task['description'],
                    'course_info': task['course'] if task['course'] else '无课程信息',
                    'completion_time': task['completion_time']
                })

            weekly_trend.append({
                'day': weekday_name,
                'value': daily_minutes,  # 保留原始分钟数用于图表计算
                'focus_time': focus_time,  # 添加小时和分钟的字典用于显示
                'date': date_str,
                'date_display': date.strftime('%m月%d日'),
                'checked_in': is_checked_in,
                'tasks': tasks_data,  # 添加任务数据
                'task_count': len(tasks_data)  # 添加任务数量
            })

        # 获取签到详情
        checked_in_dates = []
        for trend_data in weekly_trend:
            if trend_data['checked_in']:
                # 计算小时和分钟
                daily_minutes = trend_data['value']
                daily_hours = daily_minutes // 60
                daily_minutes_remainder = daily_minutes % 60
                focus_time = {'hours': daily_hours, 'minutes': daily_minutes_remainder}

                checked_in_dates.append({
                    'date': trend_data['date'],
                    'date_display': trend_data['date_display'],
                    'day': trend_data['day'],
                    'focus_hours': focus_time,  # 使用小时和分钟的字典
                    'value': trend_data['value']  # 保留原始分钟数
                })

        # 获取最近完成的任务列表（最近30天）
        completed_tasks_query = conn.execute('''
            SELECT t.id, t.title, t.course, t.updated_at as completion_time
            FROM tasks t 
            WHERE t.user_id = ? AND t.status = 'completed'
            ORDER BY t.updated_at DESC
            LIMIT 20
        ''', (user_id,)).fetchall()

        # 格式化已完成任务数据
        completed_tasks_list = []
        for task in completed_tasks_query:
            try:
                # Try to parse the datetime string
                if isinstance(task['completion_time'], str):
                    completion_time = datetime.strptime(task['completion_time'], '%Y-%m-%d %H:%M:%S')
                else:
                    completion_time = datetime.fromisoformat(str(task['completion_time']))
                
                completed_tasks_list.append({
                    'id': task['id'],
                    'title': task['title'],
                    'course': task['course'] if task['course'] else None,
                    'completion_date': completion_time.strftime('%m/%d'),
                    'completion_time': completion_time.strftime('%H:%M')
                })
            except Exception as e:
                print(f"[调试] 解析任务完成时间时出错: {str(e)}")
                # If parsing fails, use current time as fallback
                completed_tasks_list.append({
                    'id': task['id'],
                    'title': task['title'],
                    'course': task['course'] if task['course'] else None,
                    'completion_date': datetime.now().strftime('%m/%d'),
                    'completion_time': datetime.now().strftime('%H:%M')
                })

    except Exception as e:
        print(f"[调试] 报告页面出现错误: {str(e)}")
        # 错误处理中已经有默认值了
        completed_tasks_list = []
    finally:
        conn.close()

    return render_template('reports.html', translations=translations, lang=lang, weekly_stats=weekly_stats,
                           weekly_trend=weekly_trend, checked_in_dates=checked_in_dates, 
                           completed_tasks_list=completed_tasks_list)


# 路由：专注模式
@app.route('/focus')
@login_required
def focus():
    print("[调试] 访问专注模式页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        print(f"[调试] 获取用户 {user_id} 的未完成任务列表")
        tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ? AND status != ?',
                             (user_id, 'completed')).fetchall()
        
        # 获取今日专注时长
        today = datetime.now().strftime('%Y-%m-%d')
        today_stats = conn.execute('''
            SELECT SUM(duration) as total_minutes
            FROM focus_sessions
            WHERE user_id = ? AND date(start_time) = ?
        ''', (user_id, today)).fetchone()
        
        today_duration = today_stats['total_minutes'] or 0
        hours = today_duration // 60
        minutes = today_duration % 60
        
        if hours > 0:
            today_progress = f"{hours}h {minutes}m"
        else:
            today_progress = f"{minutes}m"
    except Exception as e:
        print(f"[调试] 获取专注模式数据时出现错误: {str(e)}")
        tasks = []
        today_progress = "0h 0m"
    finally:
        conn.close()

    return render_template('focus.html', translations=translations, lang=lang, tasks=tasks, today_progress=today_progress)


# 路由：保存专注会话
@app.route('/focus/save_session', methods=['POST'])
@login_required
def save_focus_session():
    print("[调试] 处理保存专注会话请求")
    user_id = session['user_id']

    # 获取请求数据
    data = request.get_json()
    duration = data.get('duration', 0)
    task_id = data.get('task_id')

    # 验证参数
    if duration <= 0:
        print("[调试] 专注时长无效")
        return jsonify({'success': False, 'message': '专注时长无效！'}), 400

    conn = get_db_connection()
    try:
        # 验证任务是否存在且属于当前用户
        if task_id:
            task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?',
                                (task_id, user_id)).fetchone()
            if not task:
                print("[调试] 任务不存在或不属于当前用户")
                return jsonify({'success': False, 'message': '任务不存在或不属于当前用户！'}), 403

        # 插入专注会话记录
        print(f"[调试] 保存专注会话 - 用户ID: {user_id}, 任务ID: {task_id}, 时长: {duration}分钟")
        conn.execute('''
            INSERT INTO focus_sessions (user_id, task_id, duration, end_time)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, task_id, duration))
        conn.commit()

        print("[调试] 专注会话保存成功")
        return jsonify({'success': True, 'message': '专注会话保存成功！'})

    except Exception as e:
        print(f"[调试] 保存专注会话失败: {str(e)}")
        conn.rollback()
        return jsonify({'success': False, 'message': f'保存专注会话失败: {str(e)}'}), 500
    finally:
        conn.close()


# 路由：获取专注统计
@app.route('/focus/stats')
@login_required
def get_focus_stats():
    print("[调试] 获取专注统计数据")
    user_id = session['user_id']
    today = datetime.now().strftime('%Y-%m-%d')

    conn = get_db_connection()
    try:
        # 获取今日专注时长
        today_stats = conn.execute('''
            SELECT SUM(duration) as total_minutes
            FROM focus_sessions
            WHERE user_id = ? AND date(start_time) = ?
        ''', (user_id, today)).fetchone()

        today_duration = today_stats['total_minutes'] or 0

        # 获取已完成的专注会话数
        completed_sessions = conn.execute('''
            SELECT COUNT(*) as count
            FROM focus_sessions
            WHERE user_id = ? AND end_time IS NOT NULL
        ''', (user_id,)).fetchone()['count']

        # 计算任务完成率（这里可以根据实际需求调整）
        total_tasks = conn.execute('''
            SELECT COUNT(*) as count
            FROM tasks
            WHERE user_id = ?
        ''', (user_id,)).fetchone()['count']

        completed_tasks = conn.execute('''
            SELECT COUNT(*) as count
            FROM tasks
            WHERE user_id = ? AND status = 'completed'
        ''', (user_id,)).fetchone()['count']

        completion_rate = 0
        if total_tasks > 0:
            completion_rate = int((completed_tasks / total_tasks) * 100)

        print(
            f"[调试] 专注统计 - 今日时长: {today_duration}分钟, 已完成会话: {completed_sessions}, 完成率: {completion_rate}%")

        return jsonify({
            'today_duration': today_duration,
            'completed_sessions': completed_sessions,
            'completion_rate': completion_rate
        })

    except Exception as e:
        print(f"[调试] 获取专注统计失败: {str(e)}")
        # 返回默认值，避免前端出错
        return jsonify({
            'today_duration': 0,
            'completed_sessions': 0,
            'completion_rate': 0
        })
    finally:
        conn.close()


# 路由：个人资料
@app.route('/profile')
@login_required
def profile():
    print("[调试] 访问个人资料页面")
    lang = request.args.get('lang', 'en-US')
    translations = get_translations(lang)

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        print(f"[调试] 获取用户 {user_id} 的详细信息")
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if not user:
            print("[调试] 未找到用户信息")
            flash('User profile not found!')
            conn.close()
            return redirect(url_for('dashboard', lang=lang))

        # 获取签到统计数据
        from database import CheckinDB
        monthly_checkins = CheckinDB.get_monthly_checkins(user_id)
        total_checkins = CheckinDB.get_total_checkins(user_id)
        
        # 获取连续签到天数
        checkin_dates = conn.execute('''
            SELECT date FROM checkins 
            WHERE user_id = ? 
            ORDER BY date DESC
        ''', (user_id,)).fetchall()
        
        streak_days = 0
        if checkin_dates:
            current_date = datetime.now().date()
            for checkin_date in checkin_dates:
                checkin_date_obj = datetime.strptime(checkin_date['date'], '%Y-%m-%d').date()
                if (current_date - checkin_date_obj).days == streak_days:
                    streak_days += 1
                else:
                    break
        
        # 获取最近30天的签到记录用于日历显示
        thirty_days_ago = (datetime.now() - timedelta(days=29)).date()
        checkin_records = {}
        checkin_list = conn.execute('''
            SELECT date FROM checkins 
            WHERE user_id = ? AND date >= ?
            ORDER BY date ASC
        ''', (user_id, thirty_days_ago.strftime('%Y-%m-%d'))).fetchall()
        
        for record in checkin_list:
            checkin_records[record['date']] = True
        
        # 生成最近30天的日期列表
        calendar_dates = []
        for i in range(30):
            date = datetime.now() - timedelta(days=29-i)
            date_str = date.strftime('%Y-%m-%d')
            calendar_dates.append({
                'date': date_str,
                'day': date.day,
                'checked_in': date_str in checkin_records
            })
        
        # 获取本月签到天数
        current_month_start = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        this_month_checkins = conn.execute('''
            SELECT COUNT(*) as count FROM checkins 
            WHERE user_id = ? AND date >= ?
        ''', (user_id, current_month_start)).fetchone()['count']
        
        # 获取教育级别显示名称
        education_level_map = {
            '1': 'Elementary',
            '2': 'Middle School',
            '3': 'High School',
            '4': 'Undergraduate'
        }
        
        grade_map = {
            '1': 'Freshman',
            '2': 'Sophomore',
            '3': 'Junior',
            '4': 'Senior'
        }
        
        education_display = education_level_map.get(str(user['education_level']), 'Undergraduate')
        grade_display = grade_map.get(str(user['grade']), '') if user['grade'] else ''
        
        # 获取密码最后修改时间（如果有的话，这里简化处理）
        password_last_changed = "November 1, 2025"  # Placeholder, can be updated if you track this

    except Exception as e:
        print(f"[调试] 获取个人资料时出现错误: {str(e)}")
        user = None
        monthly_checkins = 0
        total_checkins = 0
        streak_days = 0
        calendar_dates = []
        this_month_checkins = 0
        education_display = 'Undergraduate'
        grade_display = ''
        password_last_changed = "November 1, 2025"
    finally:
        conn.close()

    # 教育级别选项
    education_levels = ['小学', '初中', '高中', '大学本科', '硕士研究生', '博士研究生']

    return render_template('profile.html', translations=translations, lang=lang, user=user,
                           education_levels=education_levels, monthly_checkins=monthly_checkins,
                           total_checkins=total_checkins, streak_days=streak_days,
                           calendar_dates=calendar_dates, this_month_checkins=this_month_checkins,
                           education_display=education_display, grade_display=grade_display,
                           password_last_changed=password_last_changed)

# 路由：更新个人资料
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    print("[调试] 处理更新个人资料请求")
    lang = request.args.get('lang', 'en-US')
    user_id = session['user_id']

    # 获取表单数据
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    phone = request.form.get('phone')
    email = request.form.get('email')
    gender = request.form.get('gender', '')
    birth_date = request.form.get('birth_date', '')
    school = request.form.get('school', '')
    education_level = request.form.get('education_level')
    grade = request.form.get('grade', '')

    print(f"[调试] 更新个人资料请求参数 - user_id: {user_id}, first_name: {first_name}, last_name: {last_name}, "
          f"phone: {phone}, email: {email}, education_level: {education_level}")

    conn = get_db_connection()
    try:
        print("[调试] 执行个人资料更新操作")
        conn.execute('''
            UPDATE users 
            SET first_name = ?, last_name = ?, phone = ?, email = ?, 
                gender = ?, birth_date = ?, school = ?, education_level = ?, grade = ?
            WHERE id = ?
        ''', (first_name, last_name, phone, email, gender, birth_date, school, education_level, grade, user_id))
        conn.commit()
        print("[调试] 个人资料更新成功")
        flash('Profile updated successfully!')
    except Exception as e:
        print(f"[调试] 个人信息更新失败: {str(e)}")
        flash(f'Profile update failed: {str(e)}')
    finally:
        conn.close()

    return redirect(url_for('profile', lang=lang))


# 路由：修改密码
@app.route('/change_password', methods=['POST'])
@login_required
def change_password():
    print("[调试] 处理修改密码请求")
    lang = request.args.get('lang', 'en-US')
    user_id = session['user_id']

    # 获取表单数据
    current_password = request.form.get('current_password')
    new_password = request.form.get('new_password')
    confirm_new_password = request.form.get('confirm_new_password')

    print(f"[调试] 修改密码请求参数 - user_id: {user_id}")

    # 验证新密码是否一致
    if new_password != confirm_new_password:
        print("[调试] 两次输入的新密码不一致")
        flash('New passwords do not match!')
        return redirect(url_for('profile', lang=lang))

    # 验证当前密码
    conn = get_db_connection()
    try:
        print("[调试] 获取用户当前密码信息")
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if not user:
            print("[调试] 未找到用户信息")
            flash('User profile not found!')
            return redirect(url_for('profile', lang=lang))

        if not bcrypt.check_password_hash(user['password'], current_password):
            print("[调试] 当前密码不正确")
            flash('Current password is incorrect!')
            return redirect(url_for('profile', lang=lang))

        # 更新密码
        print("[调试] 加密新密码")
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')

        print("[调试] 执行密码更新操作")
        conn.execute('UPDATE users SET password = ? WHERE id = ?', (hashed_password, user_id))
        conn.commit()

        print("[调试] 密码修改成功")
        flash('Password updated successfully!')
    except Exception as e:
        print(f"[调试] 密码修改失败: {str(e)}")
        flash(f'Password update failed: {str(e)}')
    finally:
        conn.close()

    return redirect(url_for('profile', lang=lang))


# 路由：退出登录
@app.route('/logout')
@login_required
def logout():
    print("[调试] 处理退出登录请求")
    session.clear()
    print("[调试] 会话已清除，用户已退出登录")
    return redirect(url_for('login'))


# 路由：根路径
@app.route('/')
def index():
    print("[调试] 访问根路径，检查用户登录状态")
    if 'user_id' in session:
        print("[调试] 用户已登录，重定向到仪表盘")
        return redirect(url_for('dashboard', lang='en-US'))
    else:
        print("[调试] 用户未登录，重定向到登录页面")
        return redirect(url_for('login', lang='en-US'))


# 路由：更新任务状态
@app.route('/tasks/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    print(f"[调试] 处理更新任务状态请求，任务ID: {task_id}")
    user_id = session['user_id']
    # 获取请求数据
    data = request.get_json()
    new_status = data.get('status', 'completed')

    print(f"[调试] 更新任务状态 - 任务ID: {task_id}, 新状态: {new_status}")

    conn = get_db_connection()
    try:
        print(f"[调试] 验证任务 {task_id} 是否属于用户 {user_id}")
        # 首先验证任务是否属于当前用户
        task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()

        if not task:
            print(f"[调试] 任务 {task_id} 不存在或不属于用户 {user_id}")
            return jsonify({'success': False, 'message': '任务不存在或您没有权限修改此任务！'}), 403

        print(f"[调试] 更新任务 {task_id} 的状态为 {new_status}")
        # 更新任务状态
        conn.execute('UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (new_status, task_id))
        conn.commit()

        print(f"[调试] 任务 {task_id} 状态更新成功")
        return jsonify({'success': True, 'message': '任务状态更新成功！'})

    except Exception as e:
        print(f"[调试] 更新任务状态失败: {str(e)}")
        return jsonify({'success': False, 'message': f'更新任务状态失败: {str(e)}'}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    print("[调试] 应用启动中...")
    # 初始化数据库
    if not os.path.exists(app.config['DATABASE']):
        print("[调试] 数据库文件不存在，正在初始化...")
        init_db()
    print("[调试] 应用启动成功，运行在debug模式")
    app.run(debug=True)