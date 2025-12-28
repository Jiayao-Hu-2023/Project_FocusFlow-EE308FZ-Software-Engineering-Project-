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
        'zh-TW': '繁體中文（台灣）',
        'ja-JP': '日本語',
        'es-ES': 'Español',
        'hi-IN': 'हिन्दी',
        'fr-FR': 'Français'
    }
    
    # 教育级别和对应年级
    EDUCATION_LEVELS = {
        'Elementary School': ['Grade 1', 'Grade 2', 'Grade 3', 'Grade 4', 'Grade 5', 'Grade 6'],
        'Junior High School': ['Grade 7', 'Grade 8', 'Grade 9'],
        'Senior High School': ['Grade 10', 'Grade 11', 'Grade 12'],
        'Undergraduate': ['Freshman', 'Sophomore', 'Junior', 'Senior'],
        'Master': ['Year 1', 'Year 2', 'Year 3'],
        'PhD': ['Year 1', 'Year 2', 'Year 3', 'Year 4', 'Year 5']
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