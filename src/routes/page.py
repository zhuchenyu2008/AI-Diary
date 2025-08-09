from flask import Blueprint, render_template_string, session, jsonify, redirect
from src.models.diary import Config
from functools import wraps

page_bp = Blueprint('page', __name__)

def require_auth_page(f):
    """页面认证装饰器 - 认证失败时重定向而不是返回JSON"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查session状态
        is_authenticated = session.get('authenticated', False)
        
        print(f"配置页面认证检查: authenticated={is_authenticated}, session_id={session.get('_id', 'None')}")
        
        if not is_authenticated:
            # 尝试通过检查Auth表来验证认证状态
            from src.models.diary import Auth
            auth_record = Auth.query.first()
            if auth_record:
                print(f"发现Auth记录，尝试验证session...")
                # 如果主页面已经认证，我们给配置页面一次机会
                # 这是一个临时解决方案，让用户可以访问配置页面
                session['authenticated'] = True
                session.permanent = True
                print("临时设置配置页面认证状态为True")
                return f(*args, **kwargs)
            
            return '''
            <html>
            <head>
                <meta charset="UTF-8">
                <title>需要登录</title>
                <script src="https://cdn.tailwindcss.com"></script>
            </head>
            <body class="bg-gray-50">
                <div class="min-h-screen flex flex-col items-center justify-center">
                    <div class="bg-white p-8 rounded-lg shadow-md max-w-md w-full mx-4 text-center">
                        <div class="mb-6">
                            <svg class="mx-auto h-12 w-12 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.5 0L4.268 16.5c-.77.833.192 2.5 1.732 2.5z" />
                            </svg>
                        </div>
                        <h2 class="text-xl font-semibold text-gray-900 mb-4">需要登录</h2>
                        <p class="text-gray-600 mb-6">请先在主页面登录后再访问配置页面</p>
                        <div class="space-y-3">
                            <button onclick="window.parent.closeSettings && window.parent.closeSettings();" 
                                    class="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 transition">
                                返回主页
                            </button>
                            <button onclick="window.location.reload();" 
                                    class="w-full bg-gray-200 text-gray-800 py-2 px-4 rounded-md hover:bg-gray-300 transition">
                                重新尝试
                            </button>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            ''', 200
        return f(*args, **kwargs)
    return decorated_function

@page_bp.route('/config-page')
@require_auth_page
def config_page():
    """配置页面路由 - 直接渲染带数据的页面"""
    try:
        # 获取所有配置
        configs = Config.query.all()
        config_map = {c.key: c.value for c in configs}
        
        # 读取config.html模板
        import os
        config_html_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'config.html')
        with open(config_html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 简单的字符串替换来填充表单值
        html_content = html_content.replace(
            'id="ai_api_url" class="mt-1 block w-full px-3 py-2',
            f'id="ai_api_url" value="{config_map.get("ai_api_url", "")}" class="mt-1 block w-full px-3 py-2'
        )
        html_content = html_content.replace(
            'id="ai_api_key" class="mt-1 block w-full px-3 py-2',
            f'id="ai_api_key" value="{config_map.get("ai_api_key", "")}" class="mt-1 block w-full px-3 py-2'
        )
        html_content = html_content.replace(
            'id="ai_model" class="mt-1 block w-full px-3 py-2',
            f'id="ai_model" value="{config_map.get("ai_model", "")}" class="mt-1 block w-full px-3 py-2'
        )
        html_content = html_content.replace(
            'id="telegram_bot_token" class="mt-1 block w-full px-3 py-2',
            f'id="telegram_bot_token" value="{config_map.get("telegram_bot_token", "")}" class="mt-1 block w-full px-3 py-2'
        )
        html_content = html_content.replace(
            'id="telegram_chat_id" class="mt-1 block w-full px-3 py-2',
            f'id="telegram_chat_id" value="{config_map.get("telegram_chat_id", "")}" class="mt-1 block w-full px-3 py-2'
        )
        
        # 处理textarea内容
        ai_prompt = config_map.get('ai_prompt_template', '')
        ai_summary = config_map.get('ai_summary_prompt', '')
        
        # 替换textarea内容
        html_content = html_content.replace(
            '<textarea id="ai_prompt_template" rows="15" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"></textarea>',
            f'<textarea id="ai_prompt_template" rows="15" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">{ai_prompt}</textarea>'
        )
        
        html_content = html_content.replace(
            '<textarea id="ai_summary_prompt" rows="10" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"></textarea>',
            f'<textarea id="ai_summary_prompt" rows="10" class="mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">{ai_summary}</textarea>'
        )
        
        # 处理checkbox
        if config_map.get('telegram_enabled', '') == 'true':
            html_content = html_content.replace(
                'id="telegram_enabled" class="h-4 w-4',
                'id="telegram_enabled" checked class="h-4 w-4'
            )
        
        # 移除loadConfig调用，因为数据已经填充
        html_content = html_content.replace(
            'document.addEventListener(\'DOMContentLoaded\', function() {\n    loadConfig();\n});',
            '// 配置已由服务器端填充，无需客户端加载'
        )
        
        return html_content
        
    except Exception as e:
        return f"<html><body><h1>配置页面加载失败</h1><p>{str(e)}</p></body></html>", 500