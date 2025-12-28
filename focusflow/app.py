# 修改导入语句，添加g对象
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, g, send_from_directory
from flask_bcrypt import Bcrypt
import sqlite3
import os
from datetime import datetime, timedelta
import random
from functools import wraps
from config import Config
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['DATABASE'] = os.path.join(app.root_path, 'focusflow.db')
app.config['LANGUAGES'] = Config.LANGUAGES
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

bcrypt = Bcrypt(app)

def allowed_file(filename):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_current_lang() -> str:
    """Get current language from query param or session, defaulting to en-US."""
    lang = request.args.get('lang') or session.get('lang') or 'en-US'
    # Persist selected language for requests that don't include ?lang=
    session['lang'] = lang
    return lang

# Register context processor for language + translations (so every template can access them)
@app.context_processor
def inject_i18n():
    lang = get_current_lang()
    return dict(
        supported_languages=app.config['LANGUAGES'],
        lang=lang,
        translations=get_translations(lang),
    )


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
    # print(f"[调试] 获取语言翻译，语言: {lang}")
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
            'profile': 'Personal center',
            'tasks': 'Mission',
            'focus': 'Focus mode',
            'reports': 'Report',
            'logout': 'Log out',
            'change_password': 'Change Password',
            'security_tips': 'Security Tips',
            'personal_info': 'Personal Information',
            'account_security': 'Account Security',
            'checkin_record': 'Check-in Record',
            'save_changes': 'Save Changes',
            'cancel': 'Cancel',
            'edit': 'Edit',
            'total_study_time': 'Total Study Time',
            'good_morning': 'Good morning',
            'good_afternoon': 'Good afternoon',
            'good_evening': 'Good evening',
            'greeting_subtitle': 'Today is a good day to study!',
            'signed_in': 'Already signed in today',
            'sign_in_now': 'Sign in immediately',
            'task_management': 'Task management',
            'study_report': 'Study report',
            'todays_task': "Today's task",
            'completed': 'Completed',
            'no_tasks_today': 'No tasks for today. Create some!',
            'view_all_tasks': 'View all tasks',
            'learning_statistics': 'Learning statistics',
            'learning_stats_subtitle': 'Keep going, you did a great job!',
            'this_week_focus_time': "This week's focus time",
            'focus_time_message': 'Every minute of concentration is the cornerstone of progress!',
            'recent_activity': 'Recent Activity',
            'no_recent_activity': 'No recent activity',
            'priority_high': 'High',
            'priority_medium': 'Medium',
            'priority_low': 'Low',
            'h': 'h',
            'min': 'min',
            'manage_profile': 'Manage your profile and account settings',
            'no_school': 'No School',
            'days_checked_in': 'days checked in',
            'streak': 'streak',
            'personal_information': 'Personal Information',
            'basic_profile_details': 'Your basic profile details',
            'gender': 'Gender',
            'male': 'Male',
            'female': 'Female',
            'not_set': 'Not set',
            'date_of_birth': 'Date of Birth',
            'school': 'School',
            'education_level': 'Education Level',
            'account_security': 'Account Security',
            'change_password_subtitle': 'Changing the password regularly can protect your account',
            'password_security': 'Password Security',
            'last_changed': 'Last changed',
            'change_password': 'Change Password',
            'security_tips': 'Security Tips',
            'tip_1': 'Use a strong password with letters, numbers, and symbols',
            'tip_2': 'Change your password every 3 months',
            'tip_3': 'Never share your password with others',
            'checkin_record': 'Check-in Record',
            'activity_30_days': 'Your study activity over the last 30 days',
            'current_streak': 'Current streak',
            'total_checkins': 'Total check-ins',
            'this_month': 'This month',
            'days': 'days',
            'last_30_days': 'Last 30 days',
            'legend_checked_in': 'Checked in',
            'legend_not_checked_in': 'Not checked in',
            'edit_personal_info': 'Edit Personal Information',
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'please_select': 'Please select',
            'current_password': 'Current Password',
            'new_password': 'New Password',
            'password_tip': 'Password should contain at least 6 characters'
            ,
            'flash_already_signed_in': 'You have already signed in today!',
            'flash_signin_success': 'Sign in successful! Keep up the good work!',
            'flash_signin_failed': 'Sign in failed, please try again later',
            
            # Avatar upload
            'change_avatar': 'Change profile picture',
            'no_file_selected': 'No file selected',
            'avatar_updated': 'Profile picture updated successfully!',
            'avatar_update_failed': 'Failed to update profile picture',
            'invalid_file_type': 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP.',
            'file_too_large': 'File is too large. Maximum size is 5MB.',

            # Common / misc
            'delete': 'Delete',
            'confirm_delete_task': 'Are you sure you want to delete this task?',
            'reset': 'Reset',
            'captcha_placeholder': 'Enter the captcha answer',
            'user_profile_not_found': 'User profile not found!',
            'today': 'Today',
            'tomorrow': 'Tomorrow',
            'hours': 'hours',
            'minutes': 'minutes',
            'items': 'items',
            'percent': 'percent',
            'months': ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'],
            'app_title': 'FocusFlow - A Personalized Learning Management and Focus Boost Platform',

            # Tasks page
            'tasks_page_title': 'Tasks',
            'tasks_page_subtitle': 'Manage your study tasks and assignments',
            'add_task': 'Add Task',
            'filters': 'Filters',
            'all_subjects': 'All Subjects',
            'all_priorities': 'All Priorities',
            'all_tasks': 'All Tasks',
            'active': 'active',
            'todo_list': 'To-do List',
            'not_finished': 'Not-finished',
            'already_done': 'Already-done',
            'no_tasks_yet': 'No tasks yet. Click "Add Task" to create your first task!',
            'create_task': 'Create Task',
            'edit_task': 'Edit Task',
            'save_task': 'Save Task',
            'task_title': 'Task Title',
            'task_title_placeholder': 'Enter task title',
            'description': 'Description',
            'description_placeholder': 'Enter task description',
            'subject': 'Subject',
            'subject_placeholder': 'e.g., Mathematics, Biology',
            'priority': 'Priority',
            'due_date': 'Due Date',
            'estimated_time_minutes': 'Estimated Time (minutes)',
            'estimated_time_placeholder': 'e.g., 60',
            'status': 'Status',
            'status_todo': 'To-do',
            'status_in_progress': 'Not-finished',
            'status_completed': 'Already-done',
            'repeat': 'Repeat',
            'no_repeat': 'No Repeat',
            'daily': 'Daily',
            'weekly': 'Weekly',
            'monthly': 'Monthly',
            'task_title_required': 'Please enter a task title!',
            'task_due_date_required': 'Please select a due date!',
            'task_not_found_or_no_permission': 'Task not found or you do not have permission.',
            'task_not_found_or_no_permission_delete': 'Task not found or you do not have permission.',
            'task_saved_success': 'Task saved successfully!',
            'task_save_failed': 'Failed to save task. Please try again.',
            'task_deleted_success': 'Task deleted successfully!',
            'task_delete_failed': 'Failed to delete task. Please try again.',
            'task_status_updated': 'Task status updated successfully!',
            'task_status_update_failed': 'Failed to update task status. Please try again.',

            # Focus page
            'focus_page_title': 'Study Timer',
            'focus_page_subtitle': 'Use the Pomodoro technique to boost your focus',
            'focus_time': 'Focus Time',
            'focus_time_subtitle': 'Stay focused on your study session',
            'select_subject': 'Select Subject',
            'choose_subject': 'Choose a subject',
            'start': 'Start',
            'pause': 'Pause',
            'custom_minutes_placeholder': 'Enter custom minutes',
            'set': 'Set',
            'todays_progress': "Today's Progress",
            'how_it_works': 'How it works',
            'how_it_works_1': 'Choose a subject and set your focus time',
            'how_it_works_2': 'Work with full concentration until the timer ends',
            'how_it_works_3': 'Take a short break to recharge',
            'how_it_works_4': 'Repeat the cycle to build momentum',
            'focus_mode_warning': 'Focus Mode Warning',
            'focus_mode_warning_message': 'Are you sure to proceed? If so, the duration of your current study will not be included in the records.',
            'continue': 'Continue',
            'focus_in_progress': 'Focusing',
            'break_in_progress': 'On break',
            'break_over_start_focus': 'Break is over — time to focus!',
            'focus_over_take_break': 'Focus time is over — take a break!',

            # Reports page
            'reports_page_title': 'Study report',
            'reports_page_subtitle': 'Check your learning progress and concentration effect.',
            'duration_of_concentration': 'Duration of concentration',
            'completed_tasks': 'Completed tasks',
            'continuous_checkin': 'Continuous check-in',
            'maintain_stability': '— Maintain stability',
            'task_completion_rate': 'Task completion rate',
            'compared_with_last_week': '5% increase ↑ compared with last week',
            'learning_trends_7_days': 'Learning trends in the last 7 days',
            'learning_trends_subtitle': 'Focus on the time and check-in situation.',
            'checkin_details': 'Check-in details',
            'checkin_details_subtitle': 'Check your daily check-in record list',
            'no_checkin_records': 'No check-in records',
            'no_checkin_records_subtitle': "You haven't checked in recently. Start focusing on your studies!",
            'start_focus': 'Start Focus',
            'task_completion_list': 'Task completion list',
            'task_completion_list_subtitle': 'Check the tasks you have completed recently',
            'no_completed_tasks': 'No completed tasks',
            'no_completed_tasks_subtitle': "You haven't completed any tasks recently. Go add and complete some tasks!",

            # Register / Forgot password
            'phone_placeholder': 'Enter your phone number',
            'phone_registered_placeholder': 'Enter your registered phone number',
            'first_name_placeholder': 'Enter your first name',
            'last_name_placeholder': 'Enter your last name',
            'email_optional_placeholder': 'Enter your email (optional)',
            'school_optional_placeholder': 'Enter your school (optional)',
            'select_school_level': '-- Select School Level --',
            'education_elementary': 'Elementary School',
            'education_junior_high': 'Junior High School',
            'education_senior_high': 'Senior High School',
            'education_university': 'University/College',
            'grade': 'Grade',
            'please_select_school_level': '-- Please select a school level --',
            'grade_1': 'Grade 1',
            'grade_2': 'Grade 2',
            'grade_3': 'Grade 3',
            'grade_4': 'Grade 4',
            'grade_5': 'Grade 5',
            'grade_6': 'Grade 6',
            'grade_7': 'Grade 7',
            'grade_8': 'Grade 8',
            'grade_9': 'Grade 9',
            'grade_10': 'Grade 10',
            'grade_11': 'Grade 11',
            'grade_12': 'Grade 12',
            'freshman': 'Freshman',
            'sophomore': 'Sophomore',
            'junior': 'Junior',
            'senior': 'Senior',
            'postgraduate': 'Postgraduate',
            'password_placeholder': 'Please set a password',
            'confirm_password_placeholder': 'Please confirm your password',
            'return_to_login': 'Return to Login',
            'next': 'Next',
            'user_information': 'User Information',
            'school_institution': 'School/Institution',
            'confirm_this_is_you': 'Please confirm that this is you',
            'back': 'Back',
            'confirm': 'Confirm',
            'new_password_placeholder': 'Enter new password',
            'confirm_new_password_placeholder': 'Confirm new password',
            'reset_password': 'Reset Password',
            'password_reset_success_title': 'Password Reset Successful!',
            'password_reset_success_subtitle': 'Your password has been reset successfully. You can now login with your new password.',
            'login_now': 'Login Now',
            'phone_required': 'Phone number is required',
            'phone_not_found': 'Phone number not found. Please check and try again.',
            'generic_error_try_again': 'An error occurred. Please try again.',
            'all_fields_required': 'All fields are required',
            'passwords_do_not_match': 'Passwords do not match',
            'user_not_found': 'User not found',
            'password_reset_success': 'Password reset successfully',
            'password_reset_failed': 'Password reset failed. Please try again.',
            'invalid_focus_duration': 'Invalid focus duration',
            'focus_session_saved': 'Focus session saved successfully',
            'focus_session_save_failed': 'Failed to save focus session'
        },
        'zh-CN': {
            'welcome': '欢迎',
            'login': '登录',
            'register': '注册',
            'phone': '电话号码',
            'password': '密码',
            'confirm_password': '确认密码',
            'forgot_password': '忘记密码',
            'dashboard': '仪表盘',
            'profile': '个人中心',
            'tasks': '任务',
            'focus': '专注模式',
            'reports': '报告',
            'logout': '退出登录',
            'change_password': '修改密码',
            'security_tips': '安全提示',
            'personal_info': '个人信息',
            'account_security': '账户安全',
            'checkin_record': '签到记录',
            'save_changes': '保存更改',
            'cancel': '取消',
            'edit': '编辑',
            'total_study_time': '总学习时间',
            # Profile page additions
            'manage_profile': '管理你的个人资料与账户设置',
            'no_school': '未设置学校',
            'days_checked_in': '天已签到',
            'streak': '连续',
            'personal_information': '个人信息',
            'basic_profile_details': '你的基本个人资料',
            'gender': '性别',
            'male': '男',
            'female': '女',
            'not_set': '未设置',
            'date_of_birth': '出生日期',
            'school': '学校',
            'education_level': '教育程度',
            'change_password_subtitle': '定期更改密码可以保护你的账户',
            'password_security': '密码安全',
            'last_changed': '上次更改',
            'tip_1': '使用包含字母、数字和符号的强密码',
            'tip_2': '每3个月更改一次密码',
            'tip_3': '切勿与他人分享你的密码',
            'activity_30_days': '你过去30天的学习活动',
            'current_streak': '当前连续',
            'total_checkins': '总签到次数',
            'this_month': '本月',
            'days': '天',
            'last_30_days': '过去30天',
            'legend_checked_in': '已签到',
            'legend_not_checked_in': '未签到',
            'edit_personal_info': '编辑个人信息',
            'first_name': '名',
            'last_name': '姓',
            'email': '电子邮件',
            'please_select': '请选择',
            'current_password': '当前密码',
            'new_password': '新密码',
            'password_tip': '密码至少需要6个字符',
            'flash_already_signed_in': '你今天已经签到了！',
            'flash_signin_success': '签到成功！继续加油！',
            'flash_signin_failed': '签到失败，请稍后再试',
            
            # Avatar upload
            'change_avatar': '更换头像',
            'no_file_selected': '未选择文件',
            'avatar_updated': '头像更新成功！',
            'avatar_update_failed': '头像更新失败',
            'invalid_file_type': '文件类型无效。请上传 PNG、JPG、JPEG、GIF 或 WebP 格式。',
            'file_too_large': '文件太大。最大大小为5MB。',
            
            'good_morning': '早上好',
            'good_afternoon': '下午好',
            'good_evening': '晚上好',
            'greeting_subtitle': '今天是学习的好日子！',
            'signed_in': '今日已签到',
            'sign_in_now': '立即签到',
            'task_management': '任务管理',
            'study_report': '学习报告',
            'todays_task': '今日任务',
            'completed': '已完成',
            'no_tasks_today': '今天没有任务。创建一些吧！',
            'view_all_tasks': '查看所有任务',
            'learning_statistics': '学习统计',
            'learning_stats_subtitle': '继续加油，你做得很棒！',
            'this_week_focus_time': '本周专注时间',
            'focus_time_message': '专注的每一分钟都是进步的基石！',
            'recent_activity': '最近活动',
            'no_recent_activity': '暂无最近活动',
            'priority_high': '高',
            'priority_medium': '中',
            'priority_low': '低',
            'h': '小时',
            'min': '分钟',

            # Common / misc
            'delete': '删除',
            'confirm_delete_task': '确定要删除这个任务吗？',
            'reset': '重置',
            'captcha_placeholder': '请输入验证码答案',
            'user_profile_not_found': '未找到用户资料！',
            'today': '今天',
            'tomorrow': '明天',
            'hours': '小时',
            'minutes': '分钟',
            'items': '件',
            'percent': '%',
            'months': ['1月', '2月', '3月', '4月', '5月', '6月',
                       '7月', '8月', '9月', '10月', '11月', '12月'],
            'app_title': 'FocusFlow - 个性化学习管理与专注提升平台',

            # Tasks page
            'tasks_page_title': '任务',
            'tasks_page_subtitle': '管理你的学习任务与作业',
            'add_task': '添加任务',
            'filters': '筛选',
            'all_subjects': '所有科目',
            'all_priorities': '所有优先级',
            'all_tasks': '所有任务',
            'active': '进行中',
            'todo_list': '待办清单',
            'not_finished': '未完成',
            'already_done': '已完成',
            'no_tasks_yet': '还没有任务。点击“添加任务”创建你的第一个任务！',
            'create_task': '创建任务',
            'edit_task': '编辑任务',
            'save_task': '保存任务',
            'task_title': '任务标题',
            'task_title_placeholder': '输入任务标题',
            'description': '描述',
            'description_placeholder': '输入任务描述',
            'subject': '科目',
            'subject_placeholder': '例如：数学、生物',
            'priority': '优先级',
            'due_date': '截止日期',
            'estimated_time_minutes': '预计时间（分钟）',
            'estimated_time_placeholder': '例如：60',
            'status': '状态',
            'status_todo': '待办',
            'status_in_progress': '进行中',
            'status_completed': '已完成',
            'repeat': '重复',
            'no_repeat': '不重复',
            'daily': '每天',
            'weekly': '每周',
            'monthly': '每月',
            'task_title_required': '请输入任务标题！',
            'task_due_date_required': '请选择截止日期！',
            'task_not_found_or_no_permission': '任务不存在或你没有权限。',
            'task_not_found_or_no_permission_delete': '任务不存在或你没有权限。',
            'task_saved_success': '任务保存成功！',
            'task_save_failed': '保存任务失败，请重试。',
            'task_deleted_success': '任务删除成功！',
            'task_delete_failed': '删除任务失败，请重试。',
            'task_status_updated': '任务状态更新成功！',
            'task_status_update_failed': '更新任务状态失败，请重试。',

            # Focus page
            'focus_page_title': '学习计时器',
            'focus_page_subtitle': '使用番茄工作法提升专注力',
            'focus_time': '专注时间',
            'focus_time_subtitle': '专注于你的学习时段',
            'select_subject': '选择科目',
            'choose_subject': '选择一个科目',
            'start': '开始',
            'pause': '暂停',
            'custom_minutes_placeholder': '输入自定义分钟数',
            'set': '设置',
            'todays_progress': '今日进度',
            'how_it_works': '使用说明',
            'how_it_works_1': '选择科目并设置专注时间',
            'how_it_works_2': '全神贯注学习直到计时结束',
            'how_it_works_3': '短暂休息为自己充电',
            'how_it_works_4': '重复循环建立学习节奏',
            'focus_mode_warning': '专注模式提示',
            'focus_mode_warning_message': '确定要继续吗？继续将不会记录当前学习时长。',
            'continue': '继续',
            'focus_in_progress': '专注中',
            'break_in_progress': '休息中',
            'break_over_start_focus': '休息结束，开始专注！',
            'focus_over_take_break': '专注结束，该休息了！',

            # Reports page
            'reports_page_title': '学习报告',
            'reports_page_subtitle': '查看你的学习进度与专注效果。',
            'duration_of_concentration': '专注时长',
            'completed_tasks': '完成任务',
            'continuous_checkin': '连续签到',
            'maintain_stability': '—保持稳定',
            'task_completion_rate': '任务完成率',
            'compared_with_last_week': '较上周提升 5% ↑',
            'learning_trends_7_days': '近7天学习趋势',
            'learning_trends_subtitle': '关注专注时长与签到情况。',
            'checkin_details': '签到详情',
            'checkin_details_subtitle': '查看每日签到记录列表',
            'no_checkin_records': '暂无签到记录',
            'no_checkin_records_subtitle': '你最近没有签到。开始专注学习吧！',
            'start_focus': '开始专注',
            'task_completion_list': '任务完成列表',
            'task_completion_list_subtitle': '查看你最近完成的任务',
            'no_completed_tasks': '暂无已完成任务',
            'no_completed_tasks_subtitle': '你最近没有完成任务。去添加并完成一些任务吧！',

            # Register / Forgot password
            'phone_placeholder': '输入你的手机号',
            'phone_registered_placeholder': '输入你注册的手机号',
            'first_name_placeholder': '输入你的名',
            'last_name_placeholder': '输入你的姓',
            'email_optional_placeholder': '输入邮箱（可选）',
            'school_optional_placeholder': '输入学校（可选）',
            'select_school_level': '-- 选择学段 --',
            'education_elementary': '小学',
            'education_junior_high': '初中',
            'education_senior_high': '高中',
            'education_university': '大学/学院',
            'grade': '年级',
            'please_select_school_level': '-- 请先选择学段 --',
            'grade_1': '一年级',
            'grade_2': '二年级',
            'grade_3': '三年级',
            'grade_4': '四年级',
            'grade_5': '五年级',
            'grade_6': '六年级',
            'grade_7': '七年级',
            'grade_8': '八年级',
            'grade_9': '九年级',
            'grade_10': '高一',
            'grade_11': '高二',
            'grade_12': '高三',
            'freshman': '大一',
            'sophomore': '大二',
            'junior': '大三',
            'senior': '大四',
            'postgraduate': '研究生',
            'password_placeholder': '请设置密码',
            'confirm_password_placeholder': '请确认密码',
            'return_to_login': '返回登录',
            'next': '下一步',
            'user_information': '用户信息',
            'school_institution': '学校/机构',
            'confirm_this_is_you': '请确认信息是否属于你',
            'back': '返回',
            'confirm': '确认',
            'new_password_placeholder': '输入新密码',
            'confirm_new_password_placeholder': '确认新密码',
            'reset_password': '重置密码',
            'password_reset_success_title': '密码重置成功！',
            'password_reset_success_subtitle': '你的密码已重置，现在可以使用新密码登录。',
            'login_now': '立即登录',
            'phone_required': '请输入手机号',
            'phone_not_found': '未找到该手机号，请检查后重试。',
            'generic_error_try_again': '发生错误，请重试。',
            'all_fields_required': '所有字段均为必填',
            'passwords_do_not_match': '两次输入的密码不一致',
            'user_not_found': '未找到用户',
            'password_reset_success': '密码重置成功',
            'password_reset_failed': '密码重置失败，请重试。',
            'invalid_focus_duration': '专注时长无效',
            'focus_session_saved': '专注记录已保存',
            'focus_session_save_failed': '保存专注记录失败'
        },
        'zh-TW': {
            'welcome': '歡迎',
            'login': '登入',
            'register': '註冊',
            'phone': '電話號碼',
            'password': '密碼',
            'confirm_password': '確認密碼',
            'forgot_password': '忘記密碼',
            'dashboard': '儀表板',
            'profile': '個人中心',
            'tasks': '任務',
            'focus': '專注模式',
            'reports': '報告',
            'logout': '登出',
            'change_password': '修改密碼',
            'security_tips': '安全提示',
            'personal_info': '個人資訊',
            'account_security': '帳戶安全',
            'checkin_record': '簽到記錄',
            'save_changes': '儲存更改',
            'cancel': '取消',
            'edit': '編輯',
            'total_study_time': '總學習時間',
            # Profile page additions
            'manage_profile': '管理你的個人資料與帳戶設定',
            'no_school': '未設定學校',
            'days_checked_in': '天已簽到',
            'streak': '連續',
            'personal_information': '個人資訊',
            'basic_profile_details': '你的基本個人資料',
            'gender': '性別',
            'male': '男',
            'female': '女',
            'not_set': '未設定',
            'date_of_birth': '出生日期',
            'school': '學校',
            'education_level': '教育程度',
            'change_password_subtitle': '定期更改密碼可以保護你的帳戶',
            'password_security': '密碼安全',
            'last_changed': '上次更改',
            'tip_1': '使用包含字母、數字和符號的強密碼',
            'tip_2': '每3個月更改一次密碼',
            'tip_3': '切勿與他人分享你的密碼',
            'activity_30_days': '你過去30天的學習活動',
            'current_streak': '目前連續',
            'total_checkins': '總簽到次數',
            'this_month': '本月',
            'last_30_days': '過去30天',
            'legend_checked_in': '已簽到',
            'legend_not_checked_in': '未簽到',
            'edit_personal_info': '編輯個人資訊',
            'first_name': '名',
            'last_name': '姓',
            'email': '電子郵件',
            'please_select': '請選擇',
            'current_password': '目前密碼',
            'new_password': '新密碼',
            'password_tip': '密碼至少需要6個字元',
            'flash_already_signed_in': '你今天已經簽到了！',
            'flash_signin_success': '簽到成功！繼續加油！',
            'flash_signin_failed': '簽到失敗，請稍後再試',
            
            # Avatar upload
            'change_avatar': '更換頭像',
            'no_file_selected': '未選擇文件',
            'avatar_updated': '頭像更新成功！',
            'avatar_update_failed': '頭像更新失敗',
            'invalid_file_type': '文件類型無效。請上傳 PNG、JPG、JPEG、GIF 或 WebP 格式。',
            'file_too_large': '文件太大。最大大小為5MB。',
            
            'good_morning': '早安',
            'good_afternoon': '午安',
            'good_evening': '晚安',
            'greeting_subtitle': '今天是學習的好日子！',
            'signed_in': '今日已簽到',
            'sign_in_now': '立即簽到',
            'task_management': '任務管理',
            'study_report': '學習報告',
            'todays_task': '今日任務',
            'completed': '已完成',
            'no_tasks_today': '今天沒有任務。創建一些吧！',
            'view_all_tasks': '查看所有任務',
            'learning_statistics': '學習統計',
            'learning_stats_subtitle': '繼續加油，你做得很棒！',
            'this_week_focus_time': '本週專注時間',
            'focus_time_message': '專注的每一分鐘都是進步的基石！',
            'recent_activity': '最近活動',
            'no_recent_activity': '暫無最近活動',
            'priority_high': '高',
            'priority_medium': '中',
            'priority_low': '低',
            'h': '小時',
            'min': '分鐘',

            # Common / misc
            'delete': '刪除',
            'confirm_delete_task': '確定要刪除此任務嗎？',
            'reset': '重設',
            'captcha_placeholder': '請輸入驗證碼答案',
            'user_profile_not_found': '找不到使用者資料！',
            'today': '今天',
            'tomorrow': '明天',
            'hours': '小時',
            'minutes': '分鐘',
            'items': '件',
            'percent': '%',
            'days': '天',
            'months': ['1月', '2月', '3月', '4月', '5月', '6月',
                       '7月', '8月', '9月', '10月', '11月', '12月'],
            'app_title': 'FocusFlow - 個人化學習管理與專注提升平台',

            # Tasks page
            'tasks_page_title': '任務',
            'tasks_page_subtitle': '管理你的學習任務與作業',
            'add_task': '新增任務',
            'filters': '篩選',
            'all_subjects': '所有科目',
            'all_priorities': '所有優先級',
            'all_tasks': '所有任務',
            'active': '進行中',
            'todo_list': '待辦清單',
            'not_finished': '未完成',
            'already_done': '已完成',
            'no_tasks_yet': '尚無任務。點擊「新增任務」建立你的第一個任務！',
            'create_task': '建立任務',
            'edit_task': '編輯任務',
            'save_task': '儲存任務',
            'task_title': '任務標題',
            'task_title_placeholder': '輸入任務標題',
            'description': '描述',
            'description_placeholder': '輸入任務描述',
            'subject': '科目',
            'subject_placeholder': '例如：數學、生物',
            'priority': '優先級',
            'due_date': '截止日期',
            'estimated_time_minutes': '預估時間（分鐘）',
            'estimated_time_placeholder': '例如：60',
            'status': '狀態',
            'status_todo': '待辦',
            'status_in_progress': '進行中',
            'status_completed': '已完成',
            'repeat': '重複',
            'no_repeat': '不重複',
            'daily': '每天',
            'weekly': '每週',
            'monthly': '每月',
            'task_title_required': '請輸入任務標題！',
            'task_due_date_required': '請選擇截止日期！',
            'task_not_found_or_no_permission': '任務不存在或你沒有權限。',
            'task_not_found_or_no_permission_delete': '任務不存在或你沒有權限。',
            'task_saved_success': '任務儲存成功！',
            'task_save_failed': '儲存任務失敗，請重試。',
            'task_deleted_success': '任務刪除成功！',
            'task_delete_failed': '刪除任務失敗，請重試。',
            'task_status_updated': '任務狀態更新成功！',
            'task_status_update_failed': '更新任務狀態失敗，請重試。',

            # Focus page
            'focus_page_title': '學習計時器',
            'focus_page_subtitle': '使用番茄工作法提升專注力',
            'focus_time': '專注時間',
            'focus_time_subtitle': '專注於你的學習時段',
            'select_subject': '選擇科目',
            'choose_subject': '選擇一個科目',
            'start': '開始',
            'pause': '暫停',
            'custom_minutes_placeholder': '輸入自訂分鐘數',
            'set': '設定',
            'todays_progress': '今日進度',
            'how_it_works': '使用說明',
            'how_it_works_1': '選擇科目並設定專注時間',
            'how_it_works_2': '全神貫注學習直到計時結束',
            'how_it_works_3': '短暫休息為自己充電',
            'how_it_works_4': '重複循環建立學習節奏',
            'focus_mode_warning': '專注模式提示',
            'focus_mode_warning_message': '確定要繼續嗎？繼續將不會記錄目前學習時長。',
            'continue': '繼續',
            'focus_in_progress': '專注中',
            'break_in_progress': '休息中',
            'break_over_start_focus': '休息結束，開始專注！',
            'focus_over_take_break': '專注結束，該休息了！',

            # Reports page
            'reports_page_title': '學習報告',
            'reports_page_subtitle': '查看你的學習進度與專注效果。',
            'duration_of_concentration': '專注時長',
            'completed_tasks': '完成任務',
            'continuous_checkin': '連續簽到',
            'maintain_stability': '—保持穩定',
            'task_completion_rate': '任務完成率',
            'compared_with_last_week': '較上週提升 5% ↑',
            'learning_trends_7_days': '近7天學習趨勢',
            'learning_trends_subtitle': '關注專注時長與簽到情況。',
            'checkin_details': '簽到詳情',
            'checkin_details_subtitle': '查看每日簽到記錄列表',
            'no_checkin_records': '暫無簽到記錄',
            'no_checkin_records_subtitle': '你最近沒有簽到。開始專注學習吧！',
            'start_focus': '開始專注',
            'task_completion_list': '任務完成列表',
            'task_completion_list_subtitle': '查看你最近完成的任務',
            'no_completed_tasks': '暫無已完成任務',
            'no_completed_tasks_subtitle': '你最近沒有完成任務。去新增並完成一些任務吧！',

            # Register / Forgot password
            'phone_placeholder': '輸入你的電話號碼',
            'phone_registered_placeholder': '輸入你註冊的電話號碼',
            'first_name_placeholder': '輸入你的名',
            'last_name_placeholder': '輸入你的姓',
            'email_optional_placeholder': '輸入電子郵件（選填）',
            'school_optional_placeholder': '輸入學校（選填）',
            'select_school_level': '-- 選擇學段 --',
            'education_elementary': '小學',
            'education_junior_high': '國中',
            'education_senior_high': '高中',
            'education_university': '大學/學院',
            'grade': '年級',
            'please_select_school_level': '-- 請先選擇學段 --',
            'password_placeholder': '請設定密碼',
            'confirm_password_placeholder': '請確認密碼',
            'return_to_login': '返回登入',
            'next': '下一步',
            'user_information': '使用者資訊',
            'school_institution': '學校/機構',
            'confirm_this_is_you': '請確認資訊是否屬於你',
            'back': '返回',
            'confirm': '確認',
            'new_password_placeholder': '輸入新密碼',
            'confirm_new_password_placeholder': '確認新密碼',
            'reset_password': '重設密碼',
            'password_reset_success_title': '密碼重設成功！',
            'password_reset_success_subtitle': '你的密碼已重設，現在可以使用新密碼登入。',
            'login_now': '立即登入',
            'phone_required': '請輸入電話號碼',
            'phone_not_found': '找不到此電話號碼，請檢查後重試。',
            'generic_error_try_again': '發生錯誤，請重試。',
            'all_fields_required': '所有欄位皆為必填',
            'passwords_do_not_match': '兩次輸入的密碼不一致',
            'user_not_found': '找不到使用者',
            'password_reset_success': '密碼重設成功',
            'password_reset_failed': '密碼重設失敗，請重試。',
            'invalid_focus_duration': '專注時長無效',
            'focus_session_saved': '專注記錄已儲存',
            'focus_session_save_failed': '儲存專注記錄失敗'
        },
        'ja-JP': {
            'welcome': 'ようこそ',
            'login': 'ログイン',
            'register': '登録',
            'phone': '電話番号',
            'password': 'パスワード',
            'confirm_password': 'パスワード確認',
            'forgot_password': 'パスワードを忘れた場合',
            'dashboard': 'ダッシュボード',
            'profile': '個人設定',
            'tasks': 'ミッション',
            'focus': '集中モード',
            'reports': 'レポート',
            'logout': 'ログアウト',
            'change_password': 'パスワード変更',
            'security_tips': 'セキュリティのヒント',
            'personal_info': '個人情報',
            'account_security': 'アカウントセキュリティ',
            'checkin_record': 'チェックイン記録',
            'save_changes': '変更を保存',
            'cancel': 'キャンセル',
            'edit': '編集',
            'total_study_time': '総学習時間',
            # Profile page additions
            'manage_profile': 'プロフィールとアカウント設定を管理',
            'no_school': '学校未設定',
            'days_checked_in': '日チェックイン済み',
            'streak': '連続',
            'personal_information': '個人情報',
            'basic_profile_details': '基本的なプロフィール情報',
            'gender': '性別',
            'male': '男性',
            'female': '女性',
            'not_set': '未設定',
            'date_of_birth': '生年月日',
            'school': '学校',
            'education_level': '教育レベル',
            'change_password_subtitle': '定期的にパスワードを変更するとアカウントを保護できます',
            'password_security': 'パスワードセキュリティ',
            'last_changed': '最終変更',
            'tip_1': '文字、数字、記号を含む強力なパスワードを使用してください',
            'tip_2': '3ヶ月ごとにパスワードを変更してください',
            'tip_3': 'パスワードを他人と共有しないでください',
            'activity_30_days': '過去30日間の学習活動',
            'current_streak': '現在の連続日数',
            'total_checkins': '総チェックイン数',
            'this_month': '今月',
            'days': '日',
            'last_30_days': '過去30日',
            'legend_checked_in': 'チェックイン済み',
            'legend_not_checked_in': '未チェックイン',
            'edit_personal_info': '個人情報を編集',
            'first_name': '名',
            'last_name': '姓',
            'email': 'メールアドレス',
            'please_select': '選択してください',
            'current_password': '現在のパスワード',
            'new_password': '新しいパスワード',
            'password_tip': 'パスワードは6文字以上である必要があります',
            'flash_already_signed_in': '今日はすでにチェックイン済みです！',
            'flash_signin_success': 'チェックイン成功！この調子で頑張りましょう！',
            'flash_signin_failed': 'チェックインに失敗しました。後でもう一度お試しください',
            
            # Avatar upload
            'change_avatar': 'プロフィール画像を変更',
            'no_file_selected': 'ファイルが選択されていません',
            'avatar_updated': 'プロフィール画像が更新されました！',
            'avatar_update_failed': 'プロフィール画像の更新に失敗しました',
            'invalid_file_type': 'ファイルタイプが無効です。PNG、JPG、JPEG、GIF、またはWebPをアップロードしてください。',
            'file_too_large': 'ファイルが大きすぎます。最大サイズは5MBです。',
            
            'good_morning': 'おはようございます',
            'good_afternoon': 'こんにちは',
            'good_evening': 'こんばんは',
            'greeting_subtitle': '今日は勉強日和です！',
            'signed_in': '本日はチェックイン済みです',
            'sign_in_now': '今すぐチェックイン',
            'task_management': 'タスク管理',
            'study_report': '学習レポート',
            'todays_task': '今日のタスク',
            'completed': '完了',
            'no_tasks_today': '今日のタスクはありません。作成しましょう！',
            'view_all_tasks': 'すべてのタスクを表示',
            'learning_statistics': '学習統計',
            'learning_stats_subtitle': 'その調子で頑張りましょう！',
            'this_week_focus_time': '今週の集中時間',
            'focus_time_message': '集中の1分1秒が進歩の礎です！',
            'recent_activity': '最近のアクティビティ',
            'no_recent_activity': '最近のアクティビティはありません',
            'priority_high': '高',
            'priority_medium': '中',
            'priority_low': '低',
            'h': '時間',
            'min': '分',

            # Common / misc
            'delete': '削除',
            'confirm_delete_task': 'このタスクを削除しますか？',
            'reset': 'リセット',
            'captcha_placeholder': 'キャプチャの答えを入力してください',
            'user_profile_not_found': 'ユーザープロフィールが見つかりません！',
            'today': '今日',
            'tomorrow': '明日',
            'hours': '時間',
            'minutes': '分',
            'items': '件',
            'percent': '%',
            'months': ['1月', '2月', '3月', '4月', '5月', '6月',
                       '7月', '8月', '9月', '10月', '11月', '12月'],
            'app_title': 'FocusFlow - パーソナライズ学習管理＆集中力向上プラットフォーム',

            # Tasks page
            'tasks_page_title': 'タスク',
            'tasks_page_subtitle': '学習タスクと課題を管理します',
            'add_task': 'タスク追加',
            'filters': 'フィルター',
            'all_subjects': 'すべての科目',
            'all_priorities': 'すべての優先度',
            'all_tasks': 'すべてのタスク',
            'active': '進行中',
            'todo_list': 'To-do リスト',
            'not_finished': '未完了',
            'already_done': '完了',
            'no_tasks_yet': 'まだタスクがありません。「タスク追加」をクリックして最初のタスクを作成しましょう！',
            'create_task': 'タスク作成',
            'edit_task': 'タスク編集',
            'save_task': '保存',
            'task_title': 'タイトル',
            'task_title_placeholder': 'タスクのタイトルを入力',
            'description': '説明',
            'description_placeholder': '説明を入力',
            'subject': '科目',
            'subject_placeholder': '例：数学、生物',
            'priority': '優先度',
            'due_date': '期限',
            'estimated_time_minutes': '見積もり時間（分）',
            'estimated_time_placeholder': '例：60',
            'status': '状態',
            'status_todo': '未着手',
            'status_in_progress': '進行中',
            'status_completed': '完了',
            'repeat': '繰り返し',
            'no_repeat': 'なし',
            'daily': '毎日',
            'weekly': '毎週',
            'monthly': '毎月',
            'task_title_required': 'タスクのタイトルを入力してください！',
            'task_due_date_required': '期限を選択してください！',
            'task_not_found_or_no_permission': 'タスクが見つからないか、権限がありません。',
            'task_not_found_or_no_permission_delete': 'タスクが見つからないか、権限がありません。',
            'task_saved_success': 'タスクを保存しました！',
            'task_save_failed': 'タスクの保存に失敗しました。もう一度お試しください。',
            'task_deleted_success': 'タスクを削除しました！',
            'task_delete_failed': 'タスクの削除に失敗しました。もう一度お試しください。',
            'task_status_updated': 'タスクの状態を更新しました！',
            'task_status_update_failed': 'タスク状態の更新に失敗しました。もう一度お試しください。',

            # Focus page
            'focus_page_title': '集中タイマー',
            'focus_page_subtitle': 'ポモドーロ・テクニックで集中力を高めよう',
            'focus_time': '集中時間',
            'focus_time_subtitle': '学習セッションに集中しましょう',
            'select_subject': '科目を選択',
            'choose_subject': '科目を選ぶ',
            'start': '開始',
            'pause': '一時停止',
            'custom_minutes_placeholder': 'カスタム分数を入力',
            'set': '設定',
            'todays_progress': '今日の進捗',
            'how_it_works': '使い方',
            'how_it_works_1': '科目を選び、集中時間を設定する',
            'how_it_works_2': 'タイマーが終わるまで集中して取り組む',
            'how_it_works_3': '短い休憩でリフレッシュする',
            'how_it_works_4': 'サイクルを繰り返して習慣化する',
            'focus_mode_warning': '集中モード警告',
            'focus_mode_warning_message': '続行しますか？続行すると、現在の学習時間は記録に含まれません。',
            'continue': '続行',
            'focus_in_progress': '集中中',
            'break_in_progress': '休憩中',
            'break_over_start_focus': '休憩終了。集中を始めましょう！',
            'focus_over_take_break': '集中終了。休憩しましょう！',

            # Reports page
            'reports_page_title': '学習レポート',
            'reports_page_subtitle': '学習の進捗と集中の効果を確認しましょう。',
            'duration_of_concentration': '集中時間',
            'completed_tasks': '完了したタスク',
            'continuous_checkin': '連続チェックイン',
            'maintain_stability': '—安定を維持',
            'task_completion_rate': 'タスク完了率',
            'compared_with_last_week': '先週比 +5%',
            'learning_trends_7_days': '直近7日間の学習トレンド',
            'learning_trends_subtitle': '集中時間とチェックイン状況。',
            'not_checked_in': '未チェックイン',
            'checkin_details': 'チェックイン詳細',
            'checkin_details_subtitle': '毎日のチェックイン記録を確認します',
            'no_checkin_records': 'チェックイン記録がありません',
            'no_checkin_records_subtitle': '最近チェックインしていません。集中学習を始めましょう！',
            'start_focus': '集中を開始',
            'task_completion_list': 'タスク完了一覧',
            'task_completion_list_subtitle': '最近完了したタスクを確認します',
            'no_completed_tasks': '完了したタスクがありません',
            'no_completed_tasks_subtitle': '最近完了したタスクがありません。追加して完了させましょう！',

            # Register / Forgot password
            'phone_placeholder': '電話番号を入力',
            'phone_registered_placeholder': '登録済みの電話番号を入力',
            'first_name_placeholder': '名を入力',
            'last_name_placeholder': '姓を入力',
            'email_optional_placeholder': 'メール（任意）',
            'school_optional_placeholder': '学校（任意）',
            'select_school_level': '-- 学年を選択 --',
            'education_elementary': '小学校',
            'education_junior_high': '中学校',
            'education_senior_high': '高校',
            'education_university': '大学/短大',
            'grade': '学年',
            'please_select_school_level': '-- 学年を選択してください --',
            'password_placeholder': 'パスワードを設定',
            'confirm_password_placeholder': 'パスワードを再入力',
            'return_to_login': 'ログインへ戻る',
            'next': '次へ',
            'user_information': 'ユーザー情報',
            'school_institution': '学校/機関',
            'confirm_this_is_you': '本人であることを確認してください',
            'back': '戻る',
            'confirm': '確認',
            'new_password_placeholder': '新しいパスワードを入力',
            'confirm_new_password_placeholder': '新しいパスワードを再入力',
            'reset_password': 'パスワードをリセット',
            'password_reset_success_title': 'パスワードのリセットに成功しました！',
            'password_reset_success_subtitle': 'パスワードをリセットしました。新しいパスワードでログインできます。',
            'login_now': '今すぐログイン',
            'phone_required': '電話番号を入力してください',
            'phone_not_found': '電話番号が見つかりません。確認して再試行してください。',
            'generic_error_try_again': 'エラーが発生しました。もう一度お試しください。',
            'all_fields_required': 'すべての項目が必須です',
            'passwords_do_not_match': 'パスワードが一致しません',
            'user_not_found': 'ユーザーが見つかりません',
            'password_reset_success': 'パスワードをリセットしました',
            'password_reset_failed': 'パスワードのリセットに失敗しました。もう一度お試しください。',
            'invalid_focus_duration': '集中時間が無効です',
            'focus_session_saved': '集中記録を保存しました',
            'focus_session_save_failed': '集中記録の保存に失敗しました'
        },
        'es-ES': {
            'welcome': 'Bienvenido',
            'login': 'Iniciar sesión',
            'register': 'Registrarse',
            'phone': 'Número de teléfono',
            'password': 'Contraseña',
            'confirm_password': 'Confirmar contraseña',
            'forgot_password': '¿Olvidaste tu contraseña?',
            'dashboard': 'Panel',
            'profile': 'Centro personal',
            'tasks': 'Misión',
            'focus': 'Modo de enfoque',
            'reports': 'Informe',
            'logout': 'Cerrar sesión',
            'change_password': 'Cambiar contraseña',
            'security_tips': 'Consejos de seguridad',
            'personal_info': 'Información personal',
            'account_security': 'Seguridad de la cuenta',
            'checkin_record': 'Registro de entrada',
            'save_changes': 'Guardar cambios',
            'cancel': 'Cancelar',
            'edit': 'Editar',
            'total_study_time': 'Tiempo total de estudio',
            'good_morning': '¡Buenos días',
            'good_afternoon': '¡Buenas tardes',
            'good_evening': '¡Buenas noches',
            'greeting_subtitle': '¡Hoy es un buen día para estudiar!',
            'signed_in': 'Ya te has registrado hoy',
            'sign_in_now': 'Registrarse inmediatamente',
            'task_management': 'Gestión de tareas',
            'study_report': 'Informe de estudio',
            'todays_task': 'Tarea de hoy',
            'completed': 'Completado',
            'no_tasks_today': 'No hay tareas para hoy. ¡Crea algunas!',
            'view_all_tasks': 'Ver todas las tareas',
            'learning_statistics': 'Estadísticas de aprendizaje',
            'learning_stats_subtitle': '¡Sigue así, hiciste un gran trabajo!',
            'this_week_focus_time': 'Tiempo de enfoque de esta semana',
            'focus_time_message': '¡Cada minuto de concentración es la piedra angular del progreso!',
            'recent_activity': 'Actividad reciente',
            'no_recent_activity': 'No hay actividad reciente',
            'priority_high': 'Alta',
            'priority_medium': 'Media',
            'priority_low': 'Baja',
            'h': 'h',
            'min': 'min',
            'manage_profile': 'Gestiona tu perfil y configuración de cuenta',
            'personal_information': 'Información personal',
            'basic_profile_details': 'Tus detalles básicos de perfil',
            'gender': 'Género',
            'male': 'Masculino',
            'female': 'Femenino',
            'not_set': 'No establecido',
            'date_of_birth': 'Fecha de nacimiento',
            'school': 'Escuela',
            'education_level': 'Nivel educativo',
            'account_security': 'Seguridad de la cuenta',
            'change_password_subtitle': 'Cambiar la contraseña regularmente protege tu cuenta',
            'password_security': 'Seguridad de contraseña',
            'last_changed': 'Último cambio',
            'change_password': 'Cambiar contraseña',
            'security_tips': 'Consejos de seguridad',
            'tip_1': 'Usa una contraseña segura con letras, números y símbolos',
            'tip_2': 'Cambia tu contraseña cada 3 meses',
            'tip_3': 'Nunca compartas tu contraseña con otros',
            'checkin_record': 'Registro de entrada',
            'activity_30_days': 'Tu actividad de estudio en los últimos 30 días',
            'current_streak': 'Racha actual',
            'total_checkins': 'Total de entradas',
            'this_month': 'Este mes',
            'days': 'días',
            'last_30_days': 'Últimos 30 días',
            'legend_checked_in': 'Registrado',
            'legend_not_checked_in': 'No registrado',
            'edit_personal_info': 'Editar información personal',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
            'please_select': 'Por favor seleccione',
            'current_password': 'Contraseña actual',
            'new_password': 'Nueva contraseña',
            'password_tip': 'La contraseña debe contener al menos 6 caracteres'
            ,
            'flash_already_signed_in': '¡Ya te has registrado hoy!',
            'flash_signin_success': '¡Registro exitoso! ¡Sigue así!',
            'flash_signin_failed': 'El registro falló, inténtalo de nuevo más tarde',
            
            # Avatar upload
            'change_avatar': 'Cambiar foto de perfil',
            'no_file_selected': 'No se seleccionó ningún archivo',
            'avatar_updated': '¡Foto de perfil actualizada con éxito!',
            'avatar_update_failed': 'No se pudo actualizar la foto de perfil',
            'invalid_file_type': 'Tipo de archivo no válido. Sube PNG, JPG, JPEG, GIF o WebP.',
            'file_too_large': 'El archivo es demasiado grande. El tamaño máximo es 5MB.',

            # Common / misc
            'delete': 'Eliminar',
            'confirm_delete_task': '¿Seguro que quieres eliminar esta tarea?',
            'reset': 'Restablecer',
            'captcha_placeholder': 'Introduce la respuesta del captcha',
            'user_profile_not_found': '¡No se encontró el perfil del usuario!',
            'today': 'Hoy',
            'tomorrow': 'Mañana',
            'hours': 'horas',
            'minutes': 'minutos',
            'items': 'elementos',
            'percent': 'por ciento',
            'months': ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                       'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'],
            'app_title': 'FocusFlow - Plataforma personalizada de gestión del aprendizaje y mejora del enfoque',

            # Tasks page
            'tasks_page_title': 'Tareas',
            'tasks_page_subtitle': 'Gestiona tus tareas y deberes de estudio',
            'add_task': 'Añadir tarea',
            'filters': 'Filtros',
            'all_subjects': 'Todas las asignaturas',
            'all_priorities': 'Todas las prioridades',
            'all_tasks': 'Todas las tareas',
            'active': 'activas',
            'todo_list': 'Lista de tareas',
            'not_finished': 'En progreso',
            'already_done': 'Terminadas',
            'no_tasks_yet': 'Aún no hay tareas. Haz clic en "Añadir tarea" para crear tu primera tarea.',
            'create_task': 'Crear tarea',
            'edit_task': 'Editar tarea',
            'save_task': 'Guardar tarea',
            'task_title': 'Título de la tarea',
            'task_title_placeholder': 'Introduce el título',
            'description': 'Descripción',
            'description_placeholder': 'Introduce la descripción',
            'subject': 'Asignatura',
            'subject_placeholder': 'p. ej., Matemáticas, Biología',
            'priority': 'Prioridad',
            'due_date': 'Fecha límite',
            'estimated_time_minutes': 'Tiempo estimado (minutos)',
            'estimated_time_placeholder': 'p. ej., 60',
            'status': 'Estado',
            'status_todo': 'Pendiente',
            'status_in_progress': 'En progreso',
            'status_completed': 'Completada',
            'repeat': 'Repetir',
            'no_repeat': 'Sin repetición',
            'daily': 'Diario',
            'weekly': 'Semanal',
            'monthly': 'Mensual',
            'task_title_required': '¡Por favor, introduce un título de tarea!',
            'task_due_date_required': '¡Por favor, selecciona una fecha límite!',
            'task_not_found_or_no_permission': 'Tarea no encontrada o sin permiso.',
            'task_not_found_or_no_permission_delete': 'Tarea no encontrada o sin permiso.',
            'task_saved_success': '¡Tarea guardada con éxito!',
            'task_save_failed': 'No se pudo guardar la tarea. Inténtalo de nuevo.',
            'task_deleted_success': '¡Tarea eliminada con éxito!',
            'task_delete_failed': 'No se pudo eliminar la tarea. Inténtalo de nuevo.',
            'task_status_updated': '¡Estado de la tarea actualizado!',
            'task_status_update_failed': 'No se pudo actualizar el estado. Inténtalo de nuevo.',

            # Focus page
            'focus_page_title': 'Temporizador de estudio',
            'focus_page_subtitle': 'Usa la técnica Pomodoro para mejorar tu enfoque',
            'focus_time': 'Tiempo de enfoque',
            'focus_time_subtitle': 'Mantente concentrado en tu sesión de estudio',
            'select_subject': 'Seleccionar asignatura',
            'choose_subject': 'Elige una asignatura',
            'start': 'Iniciar',
            'pause': 'Pausar',
            'custom_minutes_placeholder': 'Introduce minutos personalizados',
            'set': 'Establecer',
            'todays_progress': 'Progreso de hoy',
            'how_it_works': 'Cómo funciona',
            'how_it_works_1': 'Elige una asignatura y configura tu tiempo de enfoque',
            'how_it_works_2': 'Trabaja concentrado hasta que termine el temporizador',
            'how_it_works_3': 'Toma un descanso corto para recargar',
            'how_it_works_4': 'Repite el ciclo para ganar impulso',
            'focus_mode_warning': 'Advertencia de modo enfoque',
            'focus_mode_warning_message': '¿Seguro que deseas continuar? Si continúas, la duración del estudio actual no se incluirá en los registros.',
            'continue': 'Continuar',
            'focus_in_progress': 'Enfocando',
            'break_in_progress': 'Descanso',
            'break_over_start_focus': 'Fin del descanso — ¡a concentrarse!',
            'focus_over_take_break': 'Fin del enfoque — ¡toma un descanso!',

            # Reports page
            'reports_page_title': 'Informe de estudio',
            'reports_page_subtitle': 'Revisa tu progreso de aprendizaje y concentración.',
            'duration_of_concentration': 'Duración de concentración',
            'completed_tasks': 'Tareas completadas',
            'continuous_checkin': 'Racha de registro',
            'maintain_stability': '— Mantén la estabilidad',
            'task_completion_rate': 'Tasa de finalización',
            'compared_with_last_week': 'Aumento del 5% ↑ respecto a la semana pasada',
            'learning_trends_7_days': 'Tendencias de aprendizaje (7 días)',
            'learning_trends_subtitle': 'Tiempo de enfoque y registros.',
            'not_checked_in': 'No registrado',
            'checkin_details': 'Detalles de registro',
            'checkin_details_subtitle': 'Consulta tu lista diaria de registros',
            'no_checkin_records': 'Sin registros',
            'no_checkin_records_subtitle': 'No te has registrado recientemente. ¡Comienza a estudiar con enfoque!',
            'start_focus': 'Comenzar enfoque',
            'task_completion_list': 'Lista de tareas completadas',
            'task_completion_list_subtitle': 'Revisa las tareas que completaste recientemente',
            'no_completed_tasks': 'Sin tareas completadas',
            'no_completed_tasks_subtitle': 'No has completado tareas recientemente. ¡Agrega y completa algunas!',

            # Register / Forgot password
            'phone_placeholder': 'Introduce tu número de teléfono',
            'phone_registered_placeholder': 'Introduce tu teléfono registrado',
            'first_name_placeholder': 'Introduce tu nombre',
            'last_name_placeholder': 'Introduce tu apellido',
            'email_optional_placeholder': 'Introduce tu correo (opcional)',
            'school_optional_placeholder': 'Introduce tu escuela (opcional)',
            'select_school_level': '-- Selecciona nivel escolar --',
            'education_elementary': 'Primaria',
            'education_junior_high': 'Secundaria',
            'education_senior_high': 'Bachillerato',
            'education_university': 'Universidad',
            'grade': 'Curso',
            'please_select_school_level': '-- Selecciona un nivel escolar --',
            'password_placeholder': 'Establece una contraseña',
            'confirm_password_placeholder': 'Confirma tu contraseña',
            'return_to_login': 'Volver a iniciar sesión',
            'next': 'Siguiente',
            'user_information': 'Información del usuario',
            'school_institution': 'Escuela/Institución',
            'confirm_this_is_you': 'Confirma que eres tú',
            'back': 'Atrás',
            'confirm': 'Confirmar',
            'new_password_placeholder': 'Introduce nueva contraseña',
            'confirm_new_password_placeholder': 'Confirma nueva contraseña',
            'reset_password': 'Restablecer contraseña',
            'password_reset_success_title': '¡Contraseña restablecida!',
            'password_reset_success_subtitle': 'Tu contraseña se restableció correctamente. Ahora puedes iniciar sesión con tu nueva contraseña.',
            'login_now': 'Iniciar sesión ahora',
            'phone_required': 'Se requiere número de teléfono',
            'phone_not_found': 'No se encontró el teléfono. Verifica e inténtalo de nuevo.',
            'generic_error_try_again': 'Ocurrió un error. Inténtalo de nuevo.',
            'all_fields_required': 'Todos los campos son obligatorios',
            'passwords_do_not_match': 'Las contraseñas no coinciden',
            'user_not_found': 'Usuario no encontrado',
            'password_reset_success': 'Contraseña restablecida correctamente',
            'password_reset_failed': 'No se pudo restablecer la contraseña. Inténtalo de nuevo.',
            'invalid_focus_duration': 'Duración de enfoque inválida',
            'focus_session_saved': 'Sesión de enfoque guardada',
            'focus_session_save_failed': 'No se pudo guardar la sesión de enfoque'
        },
        'hi-IN': {
            'welcome': 'नमस्ते',
            'login': 'लॉग इन',
            'register': 'पंजीकरण',
            'phone': 'फ़ोन नंबर',
            'password': 'पासवर्ड',
            'confirm_password': 'पासवर्ड की पुष्टि करें',
            'forgot_password': 'पासवर्ड भूल गए',
            'dashboard': 'डैशबोर्ड',
            'profile': 'व्यक्तिगत केंद्र',
            'tasks': 'मिशन',
            'focus': 'फोकस मोड',
            'reports': 'रिपोर्ट',
            'logout': 'लॉग आउट',
            'change_password': 'पासवर्ड बदलें',
            'security_tips': 'सुरक्षा सुझाव',
            'personal_info': 'व्यक्तिगत जानकारी',
            'account_security': 'खाता सुरक्षा',
            'checkin_record': 'चेक-इन रिकॉर्ड',
            'save_changes': 'परिवर्तन सहेजें',
            'cancel': 'रद्द करें',
            'edit': 'संपादित करें',
            'total_study_time': 'कुल अध्ययन समय',
            # Profile page additions
            'manage_profile': 'अपनी प्रोफ़ाइल और खाता सेटिंग्स प्रबंधित करें',
            'no_school': 'कोई स्कूल नहीं',
            'days_checked_in': 'दिन चेक-इन किए',
            'streak': 'लगातार',
            'personal_information': 'व्यक्तिगत जानकारी',
            'basic_profile_details': 'आपकी बुनियादी प्रोफ़ाइल जानकारी',
            'gender': 'लिंग',
            'male': 'पुरुष',
            'female': 'महिला',
            'not_set': 'सेट नहीं है',
            'date_of_birth': 'जन्म तिथि',
            'school': 'स्कूल',
            'education_level': 'शिक्षा स्तर',
            'change_password_subtitle': 'नियमित रूप से पासवर्ड बदलना आपके खाते की सुरक्षा कर सकता है',
            'password_security': 'पासवर्ड सुरक्षा',
            'last_changed': 'अंतिम परिवर्तन',
            'tip_1': 'अक्षरों, संख्याओं और प्रतीकों के साथ एक मजबूत पासवर्ड का उपयोग करें',
            'tip_2': 'हर 3 महीने में अपना पासवर्ड बदलें',
            'tip_3': 'कभी भी अपना पासवर्ड दूसरों के साथ साझा न करें',
            'activity_30_days': 'पिछले 30 दिनों में आपकी अध्ययन गतिविधि',
            'current_streak': 'वर्तमान लगातार',
            'total_checkins': 'कुल चेक-इन',
            'this_month': 'इस महीने',
            'days': 'दिन',
            'last_30_days': 'पिछले 30 दिन',
            'legend_checked_in': 'चेक-इन किया',
            'legend_not_checked_in': 'चेक-इन नहीं किया',
            'edit_personal_info': 'व्यक्तिगत जानकारी संपादित करें',
            'first_name': 'पहला नाम',
            'last_name': 'अंतिम नाम',
            'email': 'ईमेल',
            'please_select': 'कृपया चुनें',
            'current_password': 'वर्तमान पासवर्ड',
            'new_password': 'नया पासवर्ड',
            'password_tip': 'पासवर्ड में कम से कम 6 अक्षर होने चाहिए',
            'flash_already_signed_in': 'आपने आज पहले ही साइन इन कर लिया है!',
            'flash_signin_success': 'साइन इन सफल! मेहनत करते रहो!',
            'flash_signin_failed': 'साइन इन विफल, कृपया बाद में पुनः प्रयास करें',
            
            # Avatar upload
            'change_avatar': 'प्रोफ़ाइल चित्र बदलें',
            'no_file_selected': 'कोई फ़ाइल नहीं चुनी गई',
            'avatar_updated': 'प्रोफ़ाइल चित्र सफलतापूर्वक अपडेट किया गया!',
            'avatar_update_failed': 'प्रोफ़ाइल चित्र अपडेट करने में विफल',
            'invalid_file_type': 'अमान्य फ़ाइल प्रकार। कृपया PNG, JPG, JPEG, GIF, या WebP अपलोड करें।',
            'file_too_large': 'फ़ाइल बहुत बड़ी है। अधिकतम आकार 5MB है।',
            
            'good_morning': 'सुप्रभात',
            'good_afternoon': 'शुभ अपराह्न',
            'good_evening': 'शुभ संध्या',
            'greeting_subtitle': 'आज अध्ययन करने के लिए एक अच्छा दिन है!',
            'signed_in': 'आज पहले ही साइन इन कर चुके हैं',
            'sign_in_now': 'तुरंत साइन इन करें',
            'task_management': 'कार्य प्रबंधन',
            'study_report': 'अध्ययन रिपोर्ट',
            'todays_task': 'आज का कार्य',
            'completed': 'पूर्ण',
            'no_tasks_today': 'आज के लिए कोई कार्य नहीं। कुछ बनाएँ!',
            'view_all_tasks': 'सभी कार्य देखें',
            'learning_statistics': 'सीखने के आँकड़े',
            'learning_stats_subtitle': 'लगे रहो, तुमने बहुत अच्छा काम किया!',
            'this_week_focus_time': 'इस सप्ताह का फोकस समय',
            'focus_time_message': 'एकाग्रता का हर मिनट प्रगति की आधारशिला है!',
            'recent_activity': 'हाल की गतिविधि',
            'no_recent_activity': 'कोई हालिया गतिविधि नहीं',
            'priority_high': 'उच्च',
            'priority_medium': 'मध्यम',
            'priority_low': 'कम',
            'h': 'घंटा',
            'min': 'मिनट',

            # Common / misc
            'delete': 'हटाएं',
            'confirm_delete_task': 'क्या आप वाकई यह कार्य हटाना चाहते हैं?',
            'reset': 'रीसेट',
            'captcha_placeholder': 'कृपया कैप्चा का उत्तर दर्ज करें',
            'user_profile_not_found': 'उपयोगकर्ता प्रोफ़ाइल नहीं मिली!',
            'today': 'आज',
            'tomorrow': 'कल',
            'hours': 'घंटे',
            'minutes': 'मिनट',
            'items': 'आइटम',
            'percent': 'प्रतिशत',
            'months': ['जनवरी', 'फ़रवरी', 'मार्च', 'अप्रैल', 'मई', 'जून',
                       'जुलाई', 'अगस्त', 'सितंबर', 'अक्टूबर', 'नवंबर', 'दिसंबर'],
            'app_title': 'FocusFlow - व्यक्तिगत सीखने प्रबंधन और फोकस बढ़ाने का प्लेटफ़ॉर्म',

            # Tasks page
            'tasks_page_title': 'कार्य',
            'tasks_page_subtitle': 'अपने अध्ययन कार्य और असाइनमेंट प्रबंधित करें',
            'add_task': 'कार्य जोड़ें',
            'filters': 'फ़िल्टर',
            'all_subjects': 'सभी विषय',
            'all_priorities': 'सभी प्राथमिकताएँ',
            'all_tasks': 'सभी कार्य',
            'active': 'सक्रिय',
            'todo_list': 'टू-डू सूची',
            'not_finished': 'प्रगति में',
            'already_done': 'पूर्ण',
            'no_tasks_yet': 'अभी कोई कार्य नहीं। पहला कार्य बनाने के लिए "कार्य जोड़ें" पर क्लिक करें!',
            'create_task': 'कार्य बनाएँ',
            'edit_task': 'कार्य संपादित करें',
            'save_task': 'कार्य सहेजें',
            'task_title': 'कार्य शीर्षक',
            'task_title_placeholder': 'शीर्षक दर्ज करें',
            'description': 'विवरण',
            'description_placeholder': 'विवरण दर्ज करें',
            'subject': 'विषय',
            'subject_placeholder': 'उदा., गणित, जीवविज्ञान',
            'priority': 'प्राथमिकता',
            'due_date': 'अंतिम तिथि',
            'estimated_time_minutes': 'अनुमानित समय (मिनट)',
            'estimated_time_placeholder': 'उदा., 60',
            'status': 'स्थिति',
            'status_todo': 'लंबित',
            'status_in_progress': 'प्रगति में',
            'status_completed': 'पूर्ण',
            'repeat': 'दोहराएँ',
            'no_repeat': 'नहीं',
            'daily': 'दैनिक',
            'weekly': 'साप्ताहिक',
            'monthly': 'मासिक',
            'task_title_required': 'कृपया कार्य शीर्षक दर्ज करें!',
            'task_due_date_required': 'कृपया अंतिम तिथि चुनें!',
            'task_not_found_or_no_permission': 'कार्य नहीं मिला या अनुमति नहीं है।',
            'task_not_found_or_no_permission_delete': 'कार्य नहीं मिला या अनुमति नहीं है।',
            'task_saved_success': 'कार्य सफलतापूर्वक सहेजा गया!',
            'task_save_failed': 'कार्य सहेजना विफल रहा। कृपया पुनः प्रयास करें।',
            'task_deleted_success': 'कार्य हटाया गया!',
            'task_delete_failed': 'कार्य हटाना विफल रहा। कृपया पुनः प्रयास करें।',
            'task_status_updated': 'कार्य की स्थिति अपडेट हुई!',
            'task_status_update_failed': 'स्थिति अपडेट विफल रही। कृपया पुनः प्रयास करें।',

            # Focus page
            'focus_page_title': 'अध्ययन टाइमर',
            'focus_page_subtitle': 'पोमोडोरो तकनीक से फोकस बढ़ाएँ',
            'focus_time': 'फोकस समय',
            'focus_time_subtitle': 'अपने अध्ययन सत्र पर ध्यान दें',
            'select_subject': 'विषय चुनें',
            'choose_subject': 'एक विषय चुनें',
            'start': 'शुरू',
            'pause': 'विराम',
            'custom_minutes_placeholder': 'कस्टम मिनट दर्ज करें',
            'set': 'सेट',
            'todays_progress': 'आज की प्रगति',
            'how_it_works': 'कैसे काम करता है',
            'how_it_works_1': 'विषय चुनें और फोकस समय सेट करें',
            'how_it_works_2': 'टाइमर खत्म होने तक पूरी एकाग्रता से काम करें',
            'how_it_works_3': 'रीचार्ज करने के लिए छोटा ब्रेक लें',
            'how_it_works_4': 'चक्र दोहराएँ और गति बनाएं',
            'focus_mode_warning': 'फोकस मोड चेतावनी',
            'focus_mode_warning_message': 'क्या आप जारी रखना चाहते हैं? जारी रखने पर वर्तमान अध्ययन अवधि रिकॉर्ड में शामिल नहीं होगी।',
            'continue': 'जारी रखें',
            'focus_in_progress': 'फोकस',
            'break_in_progress': 'ब्रेक',
            'break_over_start_focus': 'ब्रेक समाप्त — फोकस शुरू करें!',
            'focus_over_take_break': 'फोकस समाप्त — ब्रेक लें!',

            # Reports page
            'reports_page_title': 'अध्ययन रिपोर्ट',
            'reports_page_subtitle': 'अपनी प्रगति और एकाग्रता प्रभाव देखें।',
            'duration_of_concentration': 'एकाग्रता अवधि',
            'completed_tasks': 'पूर्ण कार्य',
            'continuous_checkin': 'लगातार चेक-इन',
            'maintain_stability': '— स्थिरता बनाए रखें',
            'task_completion_rate': 'कार्य पूर्णता दर',
            'compared_with_last_week': 'पिछले सप्ताह की तुलना में +5%',
            'learning_trends_7_days': 'पिछले 7 दिनों के रुझान',
            'learning_trends_subtitle': 'फोकस समय और चेक-इन स्थिति।',
            'not_checked_in': 'चेक-इन नहीं',
            'checkin_details': 'चेक-इन विवरण',
            'checkin_details_subtitle': 'दैनिक चेक-इन सूची देखें',
            'no_checkin_records': 'कोई चेक-इन रिकॉर्ड नहीं',
            'no_checkin_records_subtitle': 'हाल में चेक-इन नहीं किया। फोकस शुरू करें!',
            'start_focus': 'फोकस शुरू करें',
            'task_completion_list': 'पूर्ण कार्य सूची',
            'task_completion_list_subtitle': 'हाल में पूर्ण किए गए कार्य देखें',
            'no_completed_tasks': 'कोई पूर्ण कार्य नहीं',
            'no_completed_tasks_subtitle': 'हाल में कोई कार्य पूर्ण नहीं। कुछ जोड़ें और पूरा करें!',

            # Register / Forgot password
            'phone_placeholder': 'अपना फ़ोन नंबर दर्ज करें',
            'phone_registered_placeholder': 'पंजीकृत फ़ोन नंबर दर्ज करें',
            'first_name_placeholder': 'अपना पहला नाम दर्ज करें',
            'last_name_placeholder': 'अपना अंतिम नाम दर्ज करें',
            'email_optional_placeholder': 'ईमेल दर्ज करें (वैकल्पिक)',
            'school_optional_placeholder': 'स्कूल दर्ज करें (वैकल्पिक)',
            'select_school_level': '-- स्कूल स्तर चुनें --',
            'education_elementary': 'प्राथमिक',
            'education_junior_high': 'माध्यमिक',
            'education_senior_high': 'उच्च माध्यमिक',
            'education_university': 'विश्वविद्यालय',
            'grade': 'कक्षा',
            'please_select_school_level': '-- पहले स्कूल स्तर चुनें --',
            'password_placeholder': 'पासवर्ड सेट करें',
            'confirm_password_placeholder': 'पासवर्ड की पुष्टि करें',
            'return_to_login': 'लॉगिन पर वापस जाएँ',
            'next': 'अगला',
            'user_information': 'उपयोगकर्ता जानकारी',
            'school_institution': 'स्कूल/संस्था',
            'confirm_this_is_you': 'कृपया पुष्टि करें कि यह आप हैं',
            'back': 'वापस',
            'confirm': 'पुष्टि करें',
            'new_password_placeholder': 'नया पासवर्ड दर्ज करें',
            'confirm_new_password_placeholder': 'नए पासवर्ड की पुष्टि करें',
            'reset_password': 'पासवर्ड रीसेट करें',
            'password_reset_success_title': 'पासवर्ड रीसेट सफल!',
            'password_reset_success_subtitle': 'आपका पासवर्ड रीसेट हो गया है। अब आप नए पासवर्ड से लॉगिन कर सकते हैं।',
            'login_now': 'अभी लॉगिन करें',
            'phone_required': 'फ़ोन नंबर आवश्यक है',
            'phone_not_found': 'फ़ोन नंबर नहीं मिला। कृपया जांचें और पुनः प्रयास करें।',
            'generic_error_try_again': 'कोई त्रुटि हुई। कृपया पुनः प्रयास करें।',
            'all_fields_required': 'सभी फ़ील्ड आवश्यक हैं',
            'passwords_do_not_match': 'पासवर्ड मेल नहीं खाते',
            'user_not_found': 'उपयोगकर्ता नहीं मिला',
            'password_reset_success': 'पासवर्ड सफलतापूर्वक रीसेट हुआ',
            'password_reset_failed': 'पासवर्ड रीसेट विफल। कृपया पुनः प्रयास करें।',
            'invalid_focus_duration': 'अमान्य फोकस अवधि',
            'focus_session_saved': 'फोकस सत्र सहेजा गया',
            'focus_session_save_failed': 'फोकस सत्र सहेजना विफल'
        },
        'fr-FR': {
            'welcome': 'Bienvenue',
            'login': 'Connexion',
            'register': 'S\'inscrire',
            'phone': 'Numéro de téléphone',
            'password': 'Mot de passe',
            'confirm_password': 'Confirmer le mot de passe',
            'forgot_password': 'Mot de passe oublié',
            'dashboard': 'Tableau de bord',
            'profile': 'Centre personnel',
            'tasks': 'Mission',
            'focus': 'Mode concentration',
            'reports': 'Rapport',
            'logout': 'Déconnexion',
            'change_password': 'Changer le mot de passe',
            'security_tips': 'Conseils de sécurité',
            'personal_info': 'Informations personnelles',
            'account_security': 'Sécurité du compte',
            'checkin_record': 'Registre d\'enregistrement',
            'save_changes': 'Enregistrer les modifications',
            'cancel': 'Annuler',
            'edit': 'Modifier',
            'total_study_time': 'Temps d\'étude total',
            # Profile page additions
            'manage_profile': 'Gérez votre profil et les paramètres du compte',
            'no_school': 'Pas d\'école',
            'days_checked_in': 'jours enregistrés',
            'streak': 'série',
            'personal_information': 'Informations personnelles',
            'basic_profile_details': 'Vos informations de profil de base',
            'gender': 'Genre',
            'male': 'Homme',
            'female': 'Femme',
            'not_set': 'Non défini',
            'date_of_birth': 'Date de naissance',
            'school': 'École',
            'education_level': 'Niveau d\'éducation',
            'change_password_subtitle': 'Changer régulièrement votre mot de passe peut protéger votre compte',
            'password_security': 'Sécurité du mot de passe',
            'last_changed': 'Dernière modification',
            'tip_1': 'Utilisez un mot de passe fort avec des lettres, des chiffres et des symboles',
            'tip_2': 'Changez votre mot de passe tous les 3 mois',
            'tip_3': 'Ne partagez jamais votre mot de passe avec d\'autres personnes',
            'activity_30_days': 'Votre activité d\'étude au cours des 30 derniers jours',
            'current_streak': 'Série actuelle',
            'total_checkins': 'Total des enregistrements',
            'this_month': 'Ce mois-ci',
            'days': 'jours',
            'last_30_days': '30 derniers jours',
            'legend_checked_in': 'Enregistré',
            'legend_not_checked_in': 'Non enregistré',
            'edit_personal_info': 'Modifier les informations personnelles',
            'first_name': 'Prénom',
            'last_name': 'Nom de famille',
            'email': 'E-mail',
            'please_select': 'Veuillez sélectionner',
            'current_password': 'Mot de passe actuel',
            'new_password': 'Nouveau mot de passe',
            'password_tip': 'Le mot de passe doit contenir au moins 6 caractères',
            'flash_already_signed_in': 'Vous vous êtes déjà enregistré aujourd\'hui !',
            'flash_signin_success': 'Enregistrement réussi ! Continuez comme ça !',
            'flash_signin_failed': 'Échec de l\'enregistrement, veuillez réessayer plus tard',
            
            # Avatar upload
            'change_avatar': 'Changer la photo de profil',
            'no_file_selected': 'Aucun fichier sélectionné',
            'avatar_updated': 'Photo de profil mise à jour avec succès !',
            'avatar_update_failed': 'Échec de la mise à jour de la photo de profil',
            'invalid_file_type': 'Type de fichier non valide. Veuillez télécharger PNG, JPG, JPEG, GIF ou WebP.',
            'file_too_large': 'Le fichier est trop volumineux. La taille maximale est de 5 Mo.',
            
            'good_morning': 'Bonjour',
            'good_afternoon': 'Bonjour',
            'good_evening': 'Bonsoir',
            'greeting_subtitle': "C'est une belle journée pour étudier !",
            'signed_in': 'Déjà enregistré aujourd\'hui',
            'sign_in_now': 'S\'enregistrer maintenant',
            'task_management': 'Gestion des tâches',
            'study_report': 'Rapport d\'étude',
            'todays_task': 'Tâche du jour',
            'completed': 'Terminé',
            'no_tasks_today': 'Pas de tâches pour aujourd\'hui. Créez-en !',
            'view_all_tasks': 'Voir toutes les tâches',
            'learning_statistics': 'Statistiques d\'apprentissage',
            'learning_stats_subtitle': 'Continuez comme ça, beau travail !',
            'this_week_focus_time': 'Temps de concentration cette semaine',
            'focus_time_message': 'Chaque minute de concentration est la pierre angulaire du progrès !',
            'recent_activity': 'Activité récente',
            'no_recent_activity': 'Aucune activité récente',
            'priority_high': 'Haute',
            'priority_medium': 'Moyenne',
            'priority_low': 'Basse',
            'h': 'h',
            'min': 'min',

            # Common / misc
            'delete': 'Supprimer',
            'confirm_delete_task': 'Voulez-vous vraiment supprimer cette tâche ?',
            'reset': 'Réinitialiser',
            'captcha_placeholder': 'Saisissez la réponse du captcha',
            'user_profile_not_found': 'Profil utilisateur introuvable !',
            'today': "Aujourd'hui",
            'tomorrow': 'Demain',
            'hours': 'heures',
            'minutes': 'minutes',
            'items': 'éléments',
            'percent': 'pour cent',
            'months': ['janvier', 'février', 'mars', 'avril', 'mai', 'juin',
                       'juillet', 'août', 'septembre', 'octobre', 'novembre', 'décembre'],
            'app_title': 'FocusFlow - Plateforme personnalisée de gestion de l’apprentissage et d’amélioration de la concentration',

            # Tasks page
            'tasks_page_title': 'Tâches',
            'tasks_page_subtitle': 'Gérez vos tâches et devoirs d’étude',
            'add_task': 'Ajouter une tâche',
            'filters': 'Filtres',
            'all_subjects': 'Toutes les matières',
            'all_priorities': 'Toutes les priorités',
            'all_tasks': 'Toutes les tâches',
            'active': 'actives',
            'todo_list': 'Liste à faire',
            'not_finished': 'En cours',
            'already_done': 'Terminées',
            'no_tasks_yet': 'Aucune tâche pour le moment. Cliquez sur « Ajouter une tâche » pour créer votre première tâche !',
            'create_task': 'Créer une tâche',
            'edit_task': 'Modifier la tâche',
            'save_task': 'Enregistrer la tâche',
            'task_title': 'Titre de la tâche',
            'task_title_placeholder': 'Saisir le titre',
            'description': 'Description',
            'description_placeholder': 'Saisir la description',
            'subject': 'Matière',
            'subject_placeholder': 'ex. Mathématiques, Biologie',
            'priority': 'Priorité',
            'due_date': 'Date limite',
            'estimated_time_minutes': 'Temps estimé (minutes)',
            'estimated_time_placeholder': 'ex. 60',
            'status': 'Statut',
            'status_todo': 'À faire',
            'status_in_progress': 'En cours',
            'status_completed': 'Terminé',
            'repeat': 'Répéter',
            'no_repeat': 'Pas de répétition',
            'daily': 'Quotidien',
            'weekly': 'Hebdomadaire',
            'monthly': 'Mensuel',
            'task_title_required': 'Veuillez saisir un titre de tâche !',
            'task_due_date_required': 'Veuillez sélectionner une date limite !',
            'task_not_found_or_no_permission': 'Tâche introuvable ou autorisation refusée.',
            'task_not_found_or_no_permission_delete': 'Tâche introuvable ou autorisation refusée.',
            'task_saved_success': 'Tâche enregistrée avec succès !',
            'task_save_failed': "Échec de l'enregistrement de la tâche. Veuillez réessayer.",
            'task_deleted_success': 'Tâche supprimée avec succès !',
            'task_delete_failed': 'Échec de la suppression de la tâche. Veuillez réessayer.',
            'task_status_updated': 'Statut de la tâche mis à jour !',
            'task_status_update_failed': 'Échec de la mise à jour du statut. Veuillez réessayer.',

            # Focus page
            'focus_page_title': 'Minuteur d’étude',
            'focus_page_subtitle': 'Utilisez la technique Pomodoro pour améliorer votre concentration',
            'focus_time': 'Temps de concentration',
            'focus_time_subtitle': 'Restez concentré pendant votre session',
            'select_subject': 'Choisir une matière',
            'choose_subject': 'Choisir une matière',
            'start': 'Démarrer',
            'pause': 'Pause',
            'custom_minutes_placeholder': 'Saisir des minutes personnalisées',
            'set': 'Définir',
            'todays_progress': "Progression d'aujourd'hui",
            'how_it_works': 'Comment ça marche',
            'how_it_works_1': 'Choisissez une matière et définissez votre temps de concentration',
            'how_it_works_2': 'Travaillez à pleine concentration jusqu’à la fin du minuteur',
            'how_it_works_3': 'Prenez une courte pause pour recharger',
            'how_it_works_4': 'Répétez le cycle pour prendre le rythme',
            'focus_mode_warning': 'Avertissement du mode concentration',
            'focus_mode_warning_message': 'Voulez-vous continuer ? Si oui, la durée de votre étude actuelle ne sera pas comptabilisée.',
            'continue': 'Continuer',
            'focus_in_progress': 'Concentration',
            'break_in_progress': 'Pause',
            'break_over_start_focus': 'Pause terminée — retour à la concentration !',
            'focus_over_take_break': 'Concentration terminée — faites une pause !',

            # Reports page
            'reports_page_title': "Rapport d'étude",
            'reports_page_subtitle': 'Consultez votre progression et votre concentration.',
            'duration_of_concentration': 'Durée de concentration',
            'completed_tasks': 'Tâches terminées',
            'continuous_checkin': "Série d'enregistrement",
            'maintain_stability': '— Maintenir la stabilité',
            'task_completion_rate': "Taux d'achèvement",
            'compared_with_last_week': 'Augmentation de 5% ↑ par rapport à la semaine dernière',
            'learning_trends_7_days': "Tendances d'apprentissage (7 jours)",
            'learning_trends_subtitle': "Temps de concentration et enregistrements.",
            'not_checked_in': 'Non enregistré',
            'checkin_details': "Détails d'enregistrement",
            'checkin_details_subtitle': "Consultez la liste quotidienne d'enregistrements",
            'no_checkin_records': "Aucun enregistrement",
            'no_checkin_records_subtitle': "Vous ne vous êtes pas enregistré récemment. Commencez à vous concentrer !",
            'start_focus': 'Commencer la concentration',
            'task_completion_list': 'Liste des tâches terminées',
            'task_completion_list_subtitle': 'Consultez les tâches terminées récemment',
            'no_completed_tasks': 'Aucune tâche terminée',
            'no_completed_tasks_subtitle': "Vous n'avez terminé aucune tâche récemment. Ajoutez-en et terminez-en quelques-unes !",

            # Register / Forgot password
            'phone_placeholder': 'Entrez votre numéro de téléphone',
            'phone_registered_placeholder': 'Entrez votre numéro de téléphone enregistré',
            'first_name_placeholder': 'Entrez votre prénom',
            'last_name_placeholder': 'Entrez votre nom',
            'email_optional_placeholder': 'Entrez votre e-mail (optionnel)',
            'school_optional_placeholder': 'Entrez votre école (optionnel)',
            'select_school_level': '-- Sélectionner un niveau --',
            'education_elementary': 'Primaire',
            'education_junior_high': 'Collège',
            'education_senior_high': 'Lycée',
            'education_university': 'Université',
            'grade': 'Niveau',
            'please_select_school_level': '-- Veuillez sélectionner un niveau --',
            'password_placeholder': 'Veuillez définir un mot de passe',
            'confirm_password_placeholder': 'Veuillez confirmer votre mot de passe',
            'return_to_login': 'Retour à la connexion',
            'next': 'Suivant',
            'user_information': 'Informations utilisateur',
            'school_institution': 'École/Institution',
            'confirm_this_is_you': 'Veuillez confirmer que c’est bien vous',
            'back': 'Retour',
            'confirm': 'Confirmer',
            'new_password_placeholder': 'Entrez un nouveau mot de passe',
            'confirm_new_password_placeholder': 'Confirmez le nouveau mot de passe',
            'reset_password': 'Réinitialiser le mot de passe',
            'password_reset_success_title': 'Réinitialisation réussie !',
            'password_reset_success_subtitle': 'Votre mot de passe a été réinitialisé. Vous pouvez maintenant vous connecter avec votre nouveau mot de passe.',
            'login_now': 'Se connecter',
            'phone_required': 'Le numéro de téléphone est requis',
            'phone_not_found': 'Numéro introuvable. Vérifiez et réessayez.',
            'generic_error_try_again': 'Une erreur est survenue. Veuillez réessayer.',
            'all_fields_required': 'Tous les champs sont requis',
            'passwords_do_not_match': 'Les mots de passe ne correspondent pas',
            'user_not_found': 'Utilisateur introuvable',
            'password_reset_success': 'Mot de passe réinitialisé avec succès',
            'password_reset_failed': 'Échec de la réinitialisation. Veuillez réessayer.',
            'invalid_focus_duration': 'Durée de concentration invalide',
            'focus_session_saved': 'Session enregistrée',
            'focus_session_save_failed': "Échec de l'enregistrement de la session"
        }
    }
    
    # 使用英语作为默认回退
    result = translations['en-US'].copy()
    if lang in translations and lang != 'en-US':
        result.update(translations[lang])
        
    # print(f"[调试] 语言翻译获取成功，返回了{len(result)}个翻译项")
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
        lang = get_current_lang()
        translations = get_translations(lang)
        conn = get_db_connection()
        try:
            user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
            if user:
                # 添加调试信息，显示用户的具体姓名信息
                print(f"[调试] 用户ID: {session['user_id']}")
                print(f"[调试] 用户信息: {dict(user)}")
                
                # 调用generate_avatar_data函数生成头像数据
                initials, user_avatar_color = generate_avatar_data(user)
                # 将头像数据添加到g对象，使其在所有模板中可用
                g.initials = initials
                g.user_avatar_color = user_avatar_color
                
                # 添加用户头像到g对象
                try:
                    g.user_profile_picture = user['profile_picture'] if user['profile_picture'] else None
                except (KeyError, TypeError):
                    g.user_profile_picture = None
                
                print(f"[调试] 生成的头像字母: {initials}")

                # 添加用户真实姓名到g对象
                try:
                    # 尝试获取名字和姓氏
                    first_name = ''
                    last_name = ''

                    # 方法1：直接尝试字典式访问（适用于sqlite3.Row对象）
                    try:
                        # 直接访问字段，如果不存在会抛出KeyError
                        first_name = str(user['first_name']).strip()
                        last_name = str(user['last_name']).strip()
                        print(f"[调试] before_request: 字典式访问成功 - 名字: '{first_name}', 姓氏: '{last_name}'")
                    except (KeyError, TypeError) as e:
                        print(f"[调试] before_request: 字典式访问失败: {str(e)}，尝试属性式访问")
                        # 方法2：属性式访问（适用于对象）
                        if hasattr(user, 'first_name'):
                            first_name = str(getattr(user, 'first_name', '')).strip()
                        if hasattr(user, 'last_name'):
                            last_name = str(getattr(user, 'last_name', '')).strip()
                        print(f"[调试] before_request: 属性式访问结果 - 名字: '{first_name}', 姓氏: '{last_name}'")
                    
                    # 组合成完整姓名
                    g.user_name = f"{first_name} {last_name}".strip() if first_name or last_name else "User"
                except Exception as e:
                    print(f"[调试] 获取用户姓名时出错: {str(e)}")
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
                        g.total_study_time = f"{hours}{translations.get('h', 'h')} {minutes}{translations.get('min', 'min')}"
                    else:
                        g.total_study_time = f"{minutes}{translations.get('min', 'min')}"
                except Exception as e:
                    print(f"[调试] before_request出错: {str(e)}")
                    # 发生错误时不做处理，让模板使用默认值
                    pass
        finally:
            conn.close()


# 修改base.html中使用g对象的头像显示



# 路由：登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("[调试] 访问登录页面")
    lang = get_current_lang()
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
    lang = get_current_lang()
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
    lang = get_current_lang()
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

# 路由：验证手机号（AJAX接口）
@app.route('/verify_phone', methods=['POST'])
def verify_phone():
    print("[调试] 验证手机号")
    translations = get_translations(get_current_lang())
    data = request.get_json()
    phone = data.get('phone')
    
    if not phone:
        return jsonify({'success': False, 'message': translations.get('phone_required', 'Phone number is required')})
    
    conn = get_db_connection()
    try:
        print(f"[调试] 查询手机号: {phone}")
        user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
        
        if user:
            print("[调试] 找到用户，返回用户信息")
            return jsonify({
                'success': True,
                'user': {
                    'phone': user['phone'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'school': user['school'],
                    'email': user['email']
                }
            })
        else:
            print("[调试] 未找到用户")
            return jsonify({'success': False, 'message': translations.get('phone_not_found', 'Phone number not found. Please check and try again.')})
    except Exception as e:
        print(f"[调试] 验证手机号时出现错误: {str(e)}")
        return jsonify({'success': False, 'message': translations.get('generic_error_try_again', 'An error occurred. Please try again.')})
    finally:
        conn.close()

# 路由：重置密码（AJAX接口）
@app.route('/reset_password', methods=['POST'])
def reset_password():
    print("[调试] 重置密码")
    translations = get_translations(get_current_lang())
    data = request.get_json()
    phone = data.get('phone')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')
    
    if not phone or not new_password or not confirm_password:
        return jsonify({'success': False, 'message': translations.get('all_fields_required', 'All fields are required')})
    
    if new_password != confirm_password:
        return jsonify({'success': False, 'message': translations.get('passwords_do_not_match', 'Passwords do not match')})
    
    conn = get_db_connection()
    try:
        print(f"[调试] 查询用户: {phone}")
        user = conn.execute('SELECT * FROM users WHERE phone = ?', (phone,)).fetchone()
        
        if not user:
            return jsonify({'success': False, 'message': translations.get('user_not_found', 'User not found')})
        
        print("[调试] 加密新密码")
        hashed_password = bcrypt.generate_password_hash(new_password).decode('utf-8')
        
        print("[调试] 更新密码")
        conn.execute('UPDATE users SET password = ? WHERE phone = ?', (hashed_password, phone))
        conn.commit()
        
        print("[调试] 密码重置成功")
        return jsonify({'success': True, 'message': translations.get('password_reset_success', 'Password reset successfully')})
    except Exception as e:
        print(f"[调试] 重置密码时出现错误: {str(e)}")
        return jsonify({'success': False, 'message': translations.get('password_reset_failed', 'Password reset failed. Please try again.')})
    finally:
        conn.close()






# 路由：仪表盘
@app.route('/dashboard')
@login_required
def dashboard():
    print("[调试] 访问仪表盘页面")
    lang = get_current_lang()
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
            greeting = f"{translations['good_morning']}, {user_name}!"
        elif 12 <= current_hour < 18:
            greeting = f"{translations['good_afternoon']}, {user_name}!"
        else:
            greeting = f"{translations['good_evening']}, {user_name}!"

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
    lang = get_current_lang()
    translations = get_translations(lang)
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
            flash(translations.get('flash_already_signed_in', 'You have already signed in today!'), 'info')
        else:
            # 添加签到记录
            conn.execute(
                'INSERT INTO checkins (user_id, date) VALUES (?, ?)',
                (user_id, today)
            )
            conn.commit()
            print("[调试] 用户签到成功")
            flash(translations.get('flash_signin_success', 'Sign in successful! Keep up the good work!'), 'success')
    except Exception as e:
        print(f"[调试] 签到过程中出现错误: {str(e)}")
        flash(translations.get('flash_signin_failed', 'Sign in failed, please try again later'), 'error')
        conn.rollback()
    finally:
        conn.close()

    # 重定向回仪表盘
    return redirect(url_for('dashboard', lang=lang))


# 路由：任务列表
@app.route('/tasks')
@login_required
def tasks():
    print("[调试] 访问任务列表页面")
    lang = get_current_lang()
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
            
            # Localized due date (keep ISO for editing, display separately)
            task_dict['due_date_iso'] = task_dict.get('due_date') or ''
            task_dict['due_days_diff'] = None
            task_dict['due_date_display'] = task_dict.get('due_date') or ''
            if task_dict.get('due_date'):
                try:
                    due_date = datetime.strptime(task_dict['due_date'], '%Y-%m-%d').date()
                    days_diff = (due_date - today).days
                    task_dict['due_days_diff'] = days_diff
                    if days_diff == 0:
                        task_dict['due_date_display'] = translations.get('today', 'Today')
                    elif days_diff == 1:
                        task_dict['due_date_display'] = translations.get('tomorrow', 'Tomorrow')
                    elif days_diff > 1:
                        task_dict['due_date_display'] = f"{days_diff} {translations.get('days', 'days')}"
                    else:
                        task_dict['due_date_display'] = due_date.strftime('%Y-%m-%d')
                except Exception:
                    task_dict['due_date_display'] = task_dict['due_date']
            
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
    lang = get_current_lang()
    translations = get_translations(lang)
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
        flash(translations.get('task_title_required', 'Please enter a task title!'))
        return redirect(url_for('tasks', lang=lang))

    if not due_date:
        print("[调试] 截止日期为空，返回错误")
        flash(translations.get('task_due_date_required', 'Please select a due date!'))
        return redirect(url_for('tasks', lang=lang))

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
                flash(translations.get('task_not_found_or_no_permission', 'Task not found or you do not have permission to edit this task!'))
                return redirect(url_for('tasks', lang=lang))

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
        flash(translations.get('task_saved_success', 'Task saved successfully!'))

    except Exception as e:
        print(f"[调试] 任务保存失败: {str(e)}")
        flash(translations.get('task_save_failed', 'Task save failed, please try again later!'))
        if conn:
            conn.rollback()  # 发生错误时回滚事务
    finally:
        print("[调试] 关闭数据库连接")
        if conn:
            conn.close()

    return redirect(url_for('tasks', lang=lang))


# 路由：删除任务
@app.route('/tasks/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    print(f"[调试] 处理删除任务请求，任务ID: {task_id}")
    lang = get_current_lang()
    translations = get_translations(lang)
    user_id = session['user_id']

    conn = get_db_connection()
    try:
        print(f"[调试] 验证任务 {task_id} 是否属于用户 {user_id}")
        # 首先验证任务是否属于当前用户
        task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?', (task_id, user_id)).fetchone()

        if not task:
            print(f"[调试] 任务 {task_id} 不存在或不属于用户 {user_id}")
            flash(translations.get('task_not_found_or_no_permission_delete', 'Task not found or you do not have permission to delete this task!'))
            return redirect(url_for('tasks', lang=lang))

        print(f"[调试] 开始删除任务 {task_id}")
        # 先删除任务相关的标签
        conn.execute('DELETE FROM task_tags WHERE task_id = ?', (task_id,))
        print(f"[调试] 已删除任务 {task_id} 的标签")
        # 删除任务本身
        conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
        print(f"[调试] 成功删除任务 {task_id}")
        flash(translations.get('task_deleted_success', 'Task deleted successfully!'))
        return redirect(url_for('tasks', lang=lang))
    except Exception as e:
        print(f"[调试] 删除任务时发生错误: {str(e)}")
        conn.rollback()
        flash(translations.get('task_delete_failed', 'Task delete failed, please try again later!'))
        return redirect(url_for('tasks', lang=lang))
    finally:
        print("[调试] 关闭数据库连接")
        conn.close()


# 路由：统计页面
@app.route('/stats')
@login_required
def stats():
    print("[调试] 访问统计页面")
    lang = get_current_lang()
    translations = get_translations(lang)
    # NOTE: The legacy `stats.html` page uses gettext-style `_()` which isn't wired up in this project,
    # and the original stats backend was incomplete. To avoid a broken route, we redirect to `/reports`.
    flash(translations.get('reports', 'Reports'))
    return redirect(url_for('reports', lang=lang))


# 路由：报告
@app.route('/reports')
@login_required
def reports():
    print("[调试] 访问报告页面")
    lang = get_current_lang()
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
    lang = get_current_lang()
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
            today_progress = f"{hours}{translations.get('h', 'h')} {minutes}{translations.get('min', 'min')}"
        else:
            today_progress = f"{minutes}{translations.get('min', 'min')}"
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
    translations = get_translations(get_current_lang())
    user_id = session['user_id']

    # 获取请求数据
    data = request.get_json()
    duration = data.get('duration', 0)
    task_id = data.get('task_id')

    # 验证参数
    if duration <= 0:
        print("[调试] 专注时长无效")
        return jsonify({'success': False, 'message': translations.get('invalid_focus_duration', 'Invalid focus duration')}), 400

    conn = get_db_connection()
    try:
        # 验证任务是否存在且属于当前用户
        if task_id:
            task = conn.execute('SELECT * FROM tasks WHERE id = ? AND user_id = ?',
                                (task_id, user_id)).fetchone()
            if not task:
                print("[调试] 任务不存在或不属于当前用户")
                return jsonify({'success': False, 'message': translations.get('task_not_found_or_no_permission', 'Task not found or you do not have permission to edit this task!')}), 403

        # 插入专注会话记录
        print(f"[调试] 保存专注会话 - 用户ID: {user_id}, 任务ID: {task_id}, 时长: {duration}分钟")
        conn.execute('''
            INSERT INTO focus_sessions (user_id, task_id, duration, end_time)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, task_id, duration))
        conn.commit()

        print("[调试] 专注会话保存成功")
        return jsonify({'success': True, 'message': translations.get('focus_session_saved', 'Focus session saved successfully')})

    except Exception as e:
        print(f"[调试] 保存专注会话失败: {str(e)}")
        conn.rollback()
        return jsonify({'success': False, 'message': f"{translations.get('focus_session_save_failed', 'Failed to save focus session')}: {str(e)}"}), 500
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
    lang = get_current_lang()
    translations = get_translations(lang)

    user_id = session['user_id']
    conn = get_db_connection()
    try:
        print(f"[调试] 获取用户 {user_id} 的详细信息")
        user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()

        if not user:
            print("[调试] 未找到用户信息")
            flash(translations.get('user_profile_not_found', 'User profile not found!'))
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

    # Education level options
    education_levels = ['Elementary School', 'Junior High School', 'Senior High School', 'Undergraduate', 'Master', 'PhD']

    return render_template('profile.html', translations=translations, lang=lang, user=user,
                           education_levels=education_levels, monthly_checkins=monthly_checkins,
                           total_checkins=total_checkins, streak_days=streak_days,
                           calendar_dates=calendar_dates, this_month_checkins=this_month_checkins,
                           education_display=education_display, grade_display=grade_display,
                           password_last_changed=password_last_changed)


# 路由：上传头像
@app.route('/upload_avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Handle profile picture upload"""
    print("[调试] 处理头像上传请求")
    lang = get_current_lang()
    translations = get_translations(lang)
    user_id = session['user_id']
    
    if 'avatar' not in request.files:
        print("[调试] 未找到上传的文件")
        return jsonify({'success': False, 'message': translations.get('no_file_selected', 'No file selected')}), 400
    
    file = request.files['avatar']
    
    if file.filename == '':
        print("[调试] 文件名为空")
        return jsonify({'success': False, 'message': translations.get('no_file_selected', 'No file selected')}), 400
    
    if file and allowed_file(file.filename):
        # Generate a unique filename
        file_ext = file.filename.rsplit('.', 1)[1].lower()
        unique_filename = f"avatar_{user_id}_{uuid.uuid4().hex[:8]}.{file_ext}"
        filename = secure_filename(unique_filename)
        
        # Ensure upload folder exists
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        # Save the file
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print(f"[调试] 头像已保存到: {filepath}")
        
        # Update user's profile_picture in database
        conn = get_db_connection()
        try:
            # First, get the old avatar to delete it
            old_avatar = conn.execute('SELECT profile_picture FROM users WHERE id = ?', (user_id,)).fetchone()
            if old_avatar and old_avatar['profile_picture']:
                old_filepath = os.path.join(app.config['UPLOAD_FOLDER'], old_avatar['profile_picture'])
                if os.path.exists(old_filepath):
                    os.remove(old_filepath)
                    print(f"[调试] 已删除旧头像: {old_filepath}")
            
            # Update the database with new avatar filename
            conn.execute('UPDATE users SET profile_picture = ? WHERE id = ?', (filename, user_id))
            conn.commit()
            print(f"[调试] 数据库已更新，新头像: {filename}")
            
            # Return the URL for the new avatar
            avatar_url = url_for('static', filename=f'uploads/avatars/{filename}')
            return jsonify({
                'success': True, 
                'message': translations.get('avatar_updated', 'Profile picture updated successfully!'),
                'avatar_url': avatar_url
            })
        except Exception as e:
            print(f"[调试] 更新头像时出现错误: {str(e)}")
            # If database update fails, remove the uploaded file
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'success': False, 'message': translations.get('avatar_update_failed', 'Failed to update profile picture')}), 500
        finally:
            conn.close()
    else:
        print(f"[调试] 文件类型不支持: {file.filename}")
        return jsonify({
            'success': False, 
            'message': translations.get('invalid_file_type', 'Invalid file type. Please upload PNG, JPG, JPEG, GIF, or WebP.')
        }), 400


# 路由：更新个人资料
@app.route('/update_profile', methods=['POST'])
@login_required
def update_profile():
    print("[调试] 处理更新个人资料请求")
    lang = get_current_lang()
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
    lang = get_current_lang()
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
    lang = get_current_lang()
    session.clear()
    # keep language after clearing session
    session['lang'] = lang
    print("[调试] 会话已清除，用户已退出登录")
    return redirect(url_for('login', lang=lang))


# 路由：根路径
@app.route('/')
def index():
    print("[调试] 访问根路径，检查用户登录状态")
    lang = get_current_lang()
    if 'user_id' in session:
        print("[调试] 用户已登录，重定向到仪表盘")
        return redirect(url_for('dashboard', lang=lang))
    else:
        print("[调试] 用户未登录，重定向到登录页面")
        return redirect(url_for('login', lang=lang))


# 路由：更新任务状态
@app.route('/tasks/update_status/<int:task_id>', methods=['POST'])
@login_required
def update_task_status(task_id):
    print(f"[调试] 处理更新任务状态请求，任务ID: {task_id}")
    translations = get_translations(get_current_lang())
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
            return jsonify({'success': False, 'message': translations.get('task_not_found_or_no_permission', 'Task not found or you do not have permission to edit this task!')}), 403

        print(f"[调试] 更新任务 {task_id} 的状态为 {new_status}")
        # 更新任务状态
        conn.execute('UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?', (new_status, task_id))
        conn.commit()

        print(f"[调试] 任务 {task_id} 状态更新成功")
        return jsonify({'success': True, 'message': translations.get('task_status_updated', 'Task status updated successfully!')})

    except Exception as e:
        print(f"[调试] 更新任务状态失败: {str(e)}")
        return jsonify({'success': False, 'message': f"{translations.get('task_status_update_failed', 'Failed to update task status')}: {str(e)}"}), 500
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