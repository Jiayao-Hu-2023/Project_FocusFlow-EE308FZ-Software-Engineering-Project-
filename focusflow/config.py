import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'focusflow.db')
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # 专注模式配置
    DEFAULT_FOCUS_DURATION = 45  # 默认专注时长（分钟）
    DEFAULT_BREAK_DURATION = 15  # 默认休息时长（分钟）
    
    # 语言支持
    LANGUAGES = {
        'en-US': 'English (US)',
        'zh-CN': '简体中文',
        'zh-TW': '繁體中文（台灣）'
    }
    
    # 教育级别和对应年级
    EDUCATION_LEVELS = {
        '小学': ['一年级', '二年级', '三年级', '四年级', '五年级', '六年级'],
        '初中': ['初一', '初二', '初三'],
        '高中': ['高一', '高二', '高三'],
        '大学本科': ['大一', '大二', '大三', '大四'],
        '硕士研究生': ['研一', '研二', '研三'],
        '博士研究生': ['博一', '博二', '博三', '博四', '博五']
    }

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}