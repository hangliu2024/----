from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, session
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash as werkzeug_check_password_hash, generate_password_hash as werkzeug_generate_password_hash
from datetime import datetime, timedelta
from app import db, bcrypt
from app.models import User, LoginLog
from app.forms import RegistrationForm, LoginForm
import secrets

bp = Blueprint('auth', __name__)

# 简单的注册频率限制（基于内存，生产环境建议用Redis）
_registration_attempts = {}

# 登录失败次数记录（基于内存，生产环境建议用Redis）
_login_failures = {}

MAX_LOGIN_FAILURES = 5       # 最大失败次数
LOGIN_LOCKOUT_MINUTES = 15   # 锁定时间（分钟）

@bp.route('/register', methods=['GET', 'POST'])
def register():
    # 注册功能已关闭，仅管理员可通过后台管理页面创建用户
    flash('注册功能已关闭，请联系管理员创建账号', 'info')
    return redirect(url_for('auth.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('assets.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # 检查是否被锁定
        client_ip = request.remote_addr
        now = datetime.utcnow()
        if client_ip in _login_failures:
            _login_failures[client_ip] = [
                t for t in _login_failures[client_ip] 
                if now - t < timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
            ]
            if len(_login_failures[client_ip]) >= MAX_LOGIN_FAILURES:
                flash(f'登录失败次数过多，请{LOGIN_LOCKOUT_MINUTES}分钟后再试', 'warning')
                return render_template('auth/login.html', title='登录', form=form)
        
        # 兼容 bcrypt ($2b$...) 和 werkzeug (scrypt:..., pbkdf2:...) 两种哈希格式
        password_valid = False
        if user:
            if user.password.startswith('$2b$') or user.password.startswith('$2a$'):
                password_valid = bcrypt.check_password_hash(user.password, form.password.data)
            else:
                try:
                    password_valid = werkzeug_check_password_hash(user.password, form.password.data)
                except Exception:
                    password_valid = False
                # 如果验证成功，自动升级为 bcrypt 格式
                if password_valid:
                    user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
                    db.session.commit()
        
        if user and password_valid:
            if not user.is_active:
                flash('账号已被禁用，请联系管理员', 'danger')
                return render_template('auth/login.html', title='登录', form=form)
            
            # 登录成功，清除失败记录
            if client_ip in _login_failures:
                del _login_failures[client_ip]
            
            login_user(user, remember=form.remember.data)
            
            # 记录登录日志
            try:
                login_log = LoginLog(
                    user_id=user.id,
                    username=user.username,
                    login_type='normal',
                    ip_address=request.remote_addr,
                    user_agent=str(request.user_agent)[:200] if request.user_agent else '',
                    login_time=datetime.utcnow()
                )
                db.session.add(login_log)
                db.session.commit()
            except Exception as e:
                current_app.logger.error(f'记录登录日志失败: {e}')
            
            next_page = request.args.get('next')
            # 安全验证：只允许相对路径，避免开放重定向攻击
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            else:
                return redirect(url_for('assets.dashboard'))
        else:
            # 记录登录失败
            client_ip = request.remote_addr
            now = datetime.utcnow()
            if client_ip not in _login_failures:
                _login_failures[client_ip] = []
            # 清理过期记录
            _login_failures[client_ip] = [
                t for t in _login_failures[client_ip] 
                if now - t < timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
            ]
            _login_failures[client_ip].append(now)
            
            remaining = MAX_LOGIN_FAILURES - len(_login_failures[client_ip])
            if remaining > 0:
                flash(f'登录失败，请检查邮箱和密码（还剩{remaining}次机会）', 'danger')
            else:
                flash(f'登录失败次数过多，IP已被锁定{LOGIN_LOCKOUT_MINUTES}分钟', 'danger')
    else:
        # 检查是否被锁定
        client_ip = request.remote_addr
        now = datetime.utcnow()
        if client_ip in _login_failures:
            _login_failures[client_ip] = [
                t for t in _login_failures[client_ip] 
                if now - t < timedelta(minutes=LOGIN_LOCKOUT_MINUTES)
            ]
            if len(_login_failures[client_ip]) >= MAX_LOGIN_FAILURES:
                flash(f'登录失败次数过多，请{LOGIN_LOCKOUT_MINUTES}分钟后再试', 'warning')
                return render_template('auth/login.html', title='登录', form=form)
    
    return render_template('auth/login.html', title='登录', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def check_session_valid():
    return None
