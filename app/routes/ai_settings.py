from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required
import os

bp = Blueprint('ai_settings', __name__)

@bp.route('/ai-settings')
@login_required
def ai_settings():
    config = {
        'provider': current_app.config.get('AI_PROVIDER', 'ollama'),
        'ollama_api_base': current_app.config.get('OLLAMA_API_BASE', 'http://localhost:11434/v1'),
        'ollama_model': current_app.config.get('OLLAMA_MODEL', ''),
        'openai_api_key': current_app.config.get('OPENAI_API_KEY', ''),
        'openai_api_base': current_app.config.get('OPENAI_API_BASE', ''),
        'openai_model': current_app.config.get('OPENAI_MODEL', 'gpt-4o'),
        'minimax_api_key': current_app.config.get('MINIMAX_API_KEY', ''),
        'minimax_model': current_app.config.get('MINIMAX_MODEL', 'MiniMax-M2.7'),
    }
    
    masked_config = config.copy()
    if masked_config.get('openai_api_key'):
        key = masked_config['openai_api_key']
        if len(key) > 12:
            masked_config['openai_api_key'] = key[:8] + '...' + key[-4:]
    if masked_config.get('minimax_api_key'):
        key = masked_config['minimax_api_key']
        if len(key) > 12:
            masked_config['minimax_api_key'] = key[:8] + '...' + key[-4:]
    
    return render_template('ai_assistant/ai_settings.html', config=masked_config)

@bp.route('/ai-settings/save', methods=['POST'])
@login_required
def save_settings():
    try:
        provider = request.form.get('provider')
        current_app.config['AI_PROVIDER'] = provider
        current_app.config['OLLAMA_API_BASE'] = request.form.get('ollama_api_base', '').strip()
        current_app.config['OLLAMA_MODEL'] = request.form.get('ollama_model', '').strip()
        current_app.config['OPENAI_API_KEY'] = request.form.get('openai_api_key', '').strip()
        current_app.config['OPENAI_API_BASE'] = request.form.get('openai_api_base', '').strip()
        current_app.config['OPENAI_MODEL'] = request.form.get('openai_model', '').strip()
        current_app.config['MINIMAX_API_KEY'] = request.form.get('minimax_api_key', '').strip()
        current_app.config['MINIMAX_MODEL'] = request.form.get('minimax_model', '').strip()
        
        save_config_to_env(
            provider,
            request.form.get('ollama_api_base', '').strip(),
            request.form.get('ollama_model', '').strip(),
            request.form.get('openai_api_key', '').strip(),
            request.form.get('openai_api_base', '').strip(),
            request.form.get('openai_model', '').strip(),
            request.form.get('minimax_api_key', '').strip(),
            request.form.get('minimax_model', '').strip()
        )
        
        flash('AI配置已保存成功！', 'success')
        return redirect(url_for('ai_settings.ai_settings'))
    except Exception as e:
        flash(f'保存配置失败: {str(e)}', 'danger')
        return redirect(url_for('ai_settings.ai_settings'))

def save_config_to_env(provider, ollama_base, ollama_model,
                       openai_key, openai_base, openai_model,
                       minimax_key, minimax_model):
    # 保存到项目根目录的.env文件（与app/__init__.py中的load_ai_config路径一致）
    env_file = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    env_content = f'''# AI Configuration
AI_PROVIDER={provider}
OLLAMA_API_BASE={ollama_base}
OLLAMA_MODEL={ollama_model}
OPENAI_API_KEY={openai_key}
OPENAI_API_BASE={openai_base}
OPENAI_MODEL={openai_model}
MINIMAX_API_KEY={minimax_key}
MINIMAX_MODEL={minimax_model}
'''
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)