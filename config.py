class Config:
    SECRET_KEY = 'your-secret-key-change-this'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://nocobase:nocobase@127.0.0.1:3307/nocobase'
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
    OLLAMA_API_BASE = 'http://localhost:11434/v1'
    OLLAMA_MODEL = 'llama3'
    
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
