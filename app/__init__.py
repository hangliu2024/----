from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from config import Config
import os

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

def load_ai_config():
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[0].strip()
                        value = parts[1].strip()
                        if key in ['AI_PROVIDER', 'OLLAMA_API_BASE', 'OLLAMA_MODEL', 'OPENAI_API_KEY', 'OPENAI_API_BASE', 'OPENAI_MODEL', 'MINIMAX_API_KEY', 'MINIMAX_MODEL']:
                            app.config[key] = value

load_ai_config()

from app.routes import auth, assets, personnel, departments, ai_assistant, ai_settings, security, audit, admin
app.register_blueprint(auth.bp)
app.register_blueprint(assets.bp)
app.register_blueprint(personnel.bp)
app.register_blueprint(departments.bp, url_prefix='/departments')
app.register_blueprint(ai_assistant.bp)
app.register_blueprint(ai_settings.bp)
app.register_blueprint(security.bp)
app.register_blueprint(audit.audit_bp)
app.register_blueprint(admin.bp)

# 数据库表将通过db_init.py手动创建
