from datetime import datetime, timedelta
import random
import string

# 生成随机字符串
def generate_random_string(length=10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))

# 获取当前时间段问候语
def get_time_greeting():
    current_hour = datetime.now().hour
    if 6 <= current_hour < 12:
        return '早上好'
    elif 12 <= current_hour < 18:
        return '下午好'
    else:
        return '晚上好'

# 生成随机颜色（用于头像背景）
def generate_random_color():
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
              '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']
    return random.choice(colors)

# 获取本周日期范围
def get_week_date_range():
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())  # 周一
    end_of_week = start_of_week + timedelta(days=6)  # 周日
    return start_of_week, end_of_week

# 获取本月日期范围
def get_month_date_range():
    today = datetime.now()
    start_of_month = today.replace(day=1)
    # 计算下个月的第一天，再减一天得到本月最后一天
    if today.month == 12:
        end_of_month = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        end_of_month = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    return start_of_month.date(), end_of_month.date()

# 计算加权平均分
def calculate_weighted_average(scores_with_weights):
    """
    计算加权平均分
    scores_with_weights: 包含(分数, 权重)元组的列表
    """
    if not scores_with_weights:
        return 0.0
    
    total_score = 0.0
    total_weight = 0.0
    
    for score, weight in scores_with_weights:
        total_score += score * weight
        total_weight += weight
    
    return total_score / total_weight if total_weight > 0 else 0.0


# 生成用户头像数据
def generate_avatar_data(user):
    """
    生成用户头像数据，显示名字和姓氏的首字母组合
    支持中英文名字处理，如：Jiayao Hu显示JH，启锋 林显示启林
    """
    # 确保user不为None
    if not user:
        return 'UU', generate_random_color()
    
    try:
        # 初始化名字和姓氏
        first_name = ''
        last_name = ''
        
        # 主要使用字典式访问（因为数据库查询返回的是sqlite3.Row对象）
        try:
            # 安全地获取名字
            if hasattr(user, '__contains__') and 'first_name' in user and user['first_name']:
                first_name = str(user['first_name']).strip()
            # 安全地获取姓氏
            if hasattr(user, '__contains__') and 'last_name' in user and user['last_name']:
                last_name = str(user['last_name']).strip()
        except (KeyError, TypeError):
            pass
        
        # 如果字典式访问失败，尝试属性访问
        if not first_name and hasattr(user, 'first_name') and user.first_name:
            first_name = str(user.first_name).strip()
        if not last_name and hasattr(user, 'last_name') and user.last_name:
            last_name = str(user.last_name).strip()
        
        # 提取首字母 - 支持中英文
        # 对于中文，直接获取第一个字符；对于英文，获取第一个字母并转为大写
        first_initial = first_name[0].upper() if first_name else 'U'
        last_initial = last_name[0].upper() if last_name else 'U'
        
        # 组合首字母
        initials = first_initial + last_initial
        
    except Exception:
        # 发生任何错误时使用默认值
        initials = 'UU'
    
    # 生成随机背景颜色
    user_avatar_color = generate_random_color()
    
    return initials, user_avatar_color