from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, session as flask_session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect, CSRFError
from config import Config
import os
import secrets

app = Flask(__name__)
app.config.from_object(Config)

# 根据环境变量控制debug模式
app.debug = os.environ.get('FLASK_DEBUG', '0') == '1'

# 文件上传大小限制 (16MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# 启用CSRF保护
csrf = CSRFProtect(app)

# CSRF错误处理：当CSRF验证失败时，清除旧session并重定向回登录页
@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    flask_session.clear()
    flash('会话已过期，请重新登录', 'info')
    return redirect(url_for('auth.login'))

@app.before_request
def csrf_exempt_json():
    # 仅对明确标记为csrf_exempt的视图函数豁免CSRF检查
    if request.endpoint:
        view_func = app.view_functions.get(request.endpoint)
        if view_func and getattr(view_func, '_csrf_exempt', False):
            request.csrf_valid = True
    # 对所有/api/开头的路径豁免CSRF（API路由使用API Key认证）
    if request.path.startswith('/api/'):
        request.csrf_valid = True

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

# 安全响应头
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Content-Security-Policy'] = "default-src 'self' https://cdn.jsdelivr.net https://cdn.bootcdn.net https://cdnjs.cloudflare.com; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdn.bootcdn.net; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://cdn.bootcdn.net; font-src 'self' https://cdnjs.cloudflare.com; img-src 'self' data:; connect-src 'self' https://cdn.jsdelivr.net https://cdn.bootcdn.net https://cdnjs.cloudflare.com;"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'
    return response

# 全局错误处理
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

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
                        elif key == 'AI_API_KEYS':
                            # 支持逗号分隔的多个API Key
                            app.config[key] = [k.strip() for k in value.split(',') if k.strip()]

load_ai_config()

from app.routes import auth, assets, personnel, departments, ai_assistant, ai_settings, security, audit, admin, case_management, emergency, ai_agents
app.register_blueprint(auth.bp)
app.register_blueprint(assets.bp)
app.register_blueprint(personnel.bp)
app.register_blueprint(departments.bp, url_prefix='/departments')
app.register_blueprint(ai_assistant.bp)
app.register_blueprint(ai_settings.bp)
app.register_blueprint(security.bp)
app.register_blueprint(audit.audit_bp)
app.register_blueprint(admin.bp)
app.register_blueprint(case_management.bp)
app.register_blueprint(emergency.bp)
app.register_blueprint(ai_agents.bp)

# 豁免AI助手蓝图的CSRF检查（API路由使用API Key认证，浏览器路由使用JSON非表单）
csrf.exempt(ai_assistant.bp)
csrf.exempt(ai_agents.bp)

@app.context_processor
def inject_permissions():
    from flask_login import current_user

    def can(module_code, action='view'):
        if not current_user.is_authenticated:
            return False
        if current_user.role == 'admin':
            return True
        from app.decorators import get_user_permissions
        perms = get_user_permissions()
        return perms.get(module_code, {}).get(action, 0) == 1

    def perms():
        if not current_user.is_authenticated:
            return {}
        if current_user.role == 'admin':
            return {}
        from app.decorators import get_user_permissions
        return get_user_permissions()

    return {'perms': perms, 'can': can}

# 单点登录会话校验
@app.before_request
def validate_session():
    """每次请求前检查会话是否被踢出"""
    # 跳过静态文件和登录/登出路由
    if request.endpoint and request.endpoint not in ('static', 'auth.login', 'auth.register', 'auth.logout'):
        from flask_login import current_user
        if current_user.is_authenticated:
            from app.routes.auth import check_session_valid
            result = check_session_valid()
            if result is not None:
                return result

# 数据库表将通过db_init.py手动创建