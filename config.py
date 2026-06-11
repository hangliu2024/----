import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        # 尝试从文件读取持久化的密钥，避免每次重启都生成新密钥导致CSRF token失效
        _secret_key_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.secret_key')
        if os.path.exists(_secret_key_file):
            with open(_secret_key_file, 'r') as f:
                SECRET_KEY = f.read().strip()
        if not SECRET_KEY:
            import warnings
            warnings.warn("SECRET_KEY not set, generating and persisting a new key. Set SECRET_KEY env var for production!")
            SECRET_KEY = secrets.token_hex(32)
            with open(_secret_key_file, 'w') as f:
                f.write(SECRET_KEY)
    
    # 从环境变量读取数据库配置
    MYSQL_HOST = os.environ.get('MYSQL_HOST', '127.0.0.1')
    MYSQL_PORT = os.environ.get('MYSQL_PORT', '3307')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'nocobase')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'nocobase')
    MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE', 'nocobase')
    
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f'mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'max_overflow': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'pool_timeout': 30,
        'connect_args': {
            'read_timeout': 30,
            'write_timeout': 30,
            'connect_timeout': 15,
            'charset': 'utf8mb4'
        }
    }
    SQLALCHEMY_ECHO = False
    
    # AI大模型配置
    AI_PROVIDER = 'ollama'  # ollama, baidu, aliyun, zhipu, minimax
    
    # Ollama本地配置
    OLLAMA_API_BASE = os.environ.get('OLLAMA_API_BASE', 'http://localhost:11434/v1')
    OLLAMA_MODEL = os.environ.get('OLLAMA_MODEL', 'llama3')
    
    BAIDU_API_KEY = ''
    BAIDU_SECRET_KEY = ''
    BAIDU_MODEL = 'ernie-bot'
    
    ALIYUN_API_KEY = ''
    ALIYUN_MODEL = 'qwen-turbo'
    
    ZHIPU_API_KEY = ''
    ZHIPU_MODEL = 'glm-4'
    
    # MiniMax配置
    MINIMAX_API_KEY = ''
    MINIMAX_MODEL = 'MiniMax-M2.7'
    
    # 外部API接口密钥配置（逗号分隔支持多个Key）
    AI_API_KEYS = ['asset-ai-api-key-2024']
    
    # Session安全配置
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', '').lower() in ('true', '1', 'yes') if os.environ.get('SESSION_COOKIE_SECURE') else os.environ.get('FLASK_ENV') == 'production'
    PERMANENT_SESSION_LIFETIME = 86400  # 24小时
