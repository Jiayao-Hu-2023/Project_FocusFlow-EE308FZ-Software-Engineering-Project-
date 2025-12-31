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
    生成用户头像数据，直接提取名字和姓氏的第一个字母
    确保头像字母与用户真实姓名一致
    """
    # 确保user不为None
    if not user:
        print("[调试] generate_avatar_data: user为None，返回默认值UU")
        return 'UU', generate_random_color()
    
    try:
        # 直接获取名字和姓氏，简化逻辑
        first_name = ''
        last_name = ''
        
        # 方法1：直接尝试字典式访问（适用于sqlite3.Row对象）
        try:
            # 直接访问字段，如果不存在会抛出KeyError
            first_name = str(user['first_name']).strip()
            last_name = str(user['last_name']).strip()
            print(f"[调试] generate_avatar_data: 字典式访问成功 - 名字: '{first_name}', 姓氏: '{last_name}'")
        except (KeyError, TypeError) as e:
            print(f"[调试] generate_avatar_data: 字典式访问失败: {str(e)}，尝试属性式访问")
            # 方法2：属性式访问（适用于对象）
            if hasattr(user, 'first_name'):
                first_name = str(getattr(user, 'first_name', '')).strip()
            if hasattr(user, 'last_name'):
                last_name = str(getattr(user, 'last_name', '')).strip()
            print(f"[调试] generate_avatar_data: 属性式访问结果 - 名字: '{first_name}', 姓氏: '{last_name}'")
        
        # 提取首字母 - 支持中英文
        # 对于中文，直接获取第一个字符；对于英文，获取第一个字母并转为大写
        first_initial = first_name[0].upper() if first_name and len(first_name) > 0 else ''
        last_initial = last_name[0].upper() if last_name and len(last_name) > 0 else ''
        
        # 组合首字母
        if first_initial and last_initial:
            initials = first_initial + last_initial
        elif first_initial:
            initials = first_initial + 'U'  # 只有名字，姓氏用U代替
        elif last_initial:
            initials = 'U' + last_initial  # 只有姓氏，名字用U代替
        else:
            initials = 'UU'  # 都没有，使用默认值
        
        print(f"[调试] generate_avatar_data: 最终组合的首字母: '{initials}'")
        
    except Exception as e:
        # 发生任何错误时使用默认值
        print(f"[调试] generate_avatar_data: 发生错误: {str(e)}，返回默认值UU")
        initials = 'UU'
    
    # 生成随机背景颜色
    user_avatar_color = generate_random_color()
    
    return initials, user_avatar_color